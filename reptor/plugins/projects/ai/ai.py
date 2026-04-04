"""
AI-powered report section processing using OpenAI.

This module automates the processing of report sections using OpenAI's API,
integrating dynamic skill selection to enhance content generation.
"""

import logging
import os
import time
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

from requests.exceptions import HTTPError

try:
    import yaml
except ImportError:
    yaml = None

from reptor.lib.plugins.Base import Base
from reptor.models.Base import ProjectFieldTypes
from reptor.models.Finding import Finding
from reptor.models.Section import Section
from reptor.models.UserConfig import UserConfig

try:
    from openai import OpenAI, RateLimitError, APIError
except ImportError:
    OpenAI = None


logger = logging.getLogger(__name__)


class SkillLoader:
    """Loads and manages skill files from the skills directory."""

    def __init__(self, skills_dir: Path):
        """Initialize skill loader with skills directory."""
        self.skills_dir = Path(skills_dir)

    @lru_cache(maxsize=32)
    def load_skill(self, skill_name: str) -> Optional[str]:
        """Load a skill file by name (cached)."""
        skill_path = self.skills_dir / f"{skill_name}.md"
        if not skill_path.exists():
            return None

        try:
            content = skill_path.read_text(encoding="utf-8")
            return content
        except Exception as e:
            logger.warning(f"Failed to load skill {skill_name}: {e}")
            return None

    def list_skills(self) -> list[str]:
        """List all available skills."""
        if not self.skills_dir.exists():
            return []
        return [f.stem for f in self.skills_dir.glob("*.md")]

# This can be extended in the future to support multiple selection strategies (e.g. pattern-based)
class SkillSelector(ABC):
    """Abstract base class for skill selection strategy."""

    @abstractmethod
    def select(self, task_prompt: str, available_skills: list[str]) -> Optional[str]:
        """Select the most relevant skill for the given task."""
        pass


class AISkillSelector(SkillSelector):
    """Selects skills using OpenAI API to determine the best match."""

    def __init__(self, openai_processor: Optional["OpenAIProcessor"] = None, dry_run: bool = False):
        """Initialize AI-based skill selector."""
        self.openai_processor = openai_processor
        self.dry_run = dry_run

    def select(self, task_prompt: str, available_skills: list[str]) -> Optional[str]:
        """Select skill using AI-powered analysis."""
        if not available_skills or not self.openai_processor:
            return available_skills[0] if available_skills else None

        if len(available_skills) == 1:
            return available_skills[0]

        skills_list = ", ".join(f"'{skill}'" for skill in available_skills)
        
        prompt = f"""You are a skill selector for an AI report processing system.

Available skills: {skills_list}

Task: {task_prompt}

Analyze the task and select the SINGLE most appropriate skill from the available options.
Return ONLY the skill name, nothing else. Do not include quotes or explanation."""

        try:
            response = self.openai_processor.process(prompt)
            if response:
                selected = response.strip().strip("'\"")
                if selected in available_skills:
                    if not self.dry_run:
                        logger.info(f"AI selected skill: {selected}")
                    return selected
        except Exception as e:
            logger.warning(f"AI skill selection failed: {e}. Falling back to first skill.")

        return available_skills[0]


class PromptBuilder:
    """Constructs structured prompts for the AI model."""

    def __init__(self, template: Optional[str] = None):
        """Initialize prompt builder."""
        self.template = template or self._default_template()

    @staticmethod
    def _default_template() -> str:
        """Default prompt template."""
        return """{skill}

## Task
{task}

## Content to Process
{content}

Process the content according to the task and skill instructions above."""

    def build(
        self,
        skill_content: Optional[str],
        task_prompt: str,
        section_content: str,
    ) -> str:
        """Build the final prompt."""
        skill_section = skill_content if skill_content else "No specific skill provided."

        return self.template.format(
            skill=skill_section,
            task=task_prompt,
            content=section_content,
        )


class OpenAIProcessor:
    """Handles OpenAI API interactions with error handling and retry logic."""
    
    MAX_RETRIES = 3

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.4-mini",
        temperature: float = 0.7,
    ) -> None:
        """Initialize OpenAI processor.
        """
        if not OpenAI:
            raise ImportError(
                "OpenAI library not found. Install with: pip install openai"
            )
        
        if not 0 <= temperature <= 2:
            raise ValueError(f"Temperature must be between 0 and 2, got {temperature}")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.usage_stats = {"tokens": 0, "calls": 0, "errors": 0}

    def process(self, prompt: str) -> Optional[str]:
        """Send prompt to OpenAI and get response."""
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                )

                self.usage_stats["calls"] += 1
                if response.usage:
                    self.usage_stats["tokens"] += response.usage.total_tokens

                return response.choices[0].message.content

            except RateLimitError as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2 * (attempt + 1)
                    logger.warning(
                        f"Rate limited. Retrying in {wait_time}s (attempt {attempt + 1}/{self.MAX_RETRIES})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Rate limit exceeded after {self.MAX_RETRIES} retries")
                    self.usage_stats["errors"] += 1
                    return None

            except APIError as e:
                logger.error(f"API error: {e}")
                self.usage_stats["errors"] += 1
                return None

        return None

    def get_usage_summary(self) -> dict:
        """Get usage statistics."""
        return self.usage_stats.copy()


class SectionProcessor:
    """Processes report sections using skills and OpenAI integration."""

    PROCESSABLE_TYPES = [
        ProjectFieldTypes.string.value,
        ProjectFieldTypes.markdown.value,
    ]

    def __init__(
        self,
        skill_loader: SkillLoader,
        skill_selector: SkillSelector,
        prompt_builder: PromptBuilder,
        openai_processor: OpenAIProcessor,
        skip_fields: Optional[list[str]] = None,
    ):
        """Initialize section processor."""
        self.skill_loader = skill_loader
        self.skill_selector = skill_selector
        self.prompt_builder = prompt_builder
        self.openai_processor = openai_processor
        self.skip_fields = skip_fields or []
        self.processed_count = 0
        self.error_count = 0

    def process_section(
        self,
        section: Union[Finding, Section],
        task_prompt: str,
    ) -> Union[Finding, Section]:
        """Process a single section using the task prompt and skills."""
        available_skills = self.skill_loader.list_skills()
        selected_skill = self.skill_selector.select(task_prompt, available_skills)
        skill_content = None

        if selected_skill:
            skill_content = self.skill_loader.load_skill(selected_skill)

        for field in section.data:
            if field.type not in self.PROCESSABLE_TYPES:
                continue
            if field.name in self.skip_fields:
                continue
            if not field.value:
                continue

            prompt = self.prompt_builder.build(
                skill_content=skill_content,
                task_prompt=task_prompt,
                section_content=field.value,
            )

            result = self.openai_processor.process(prompt)

            if result:
                field.value = result
                self.processed_count += 1
            else:
                self.error_count += 1
                logger.warning(f"Failed to process field: {field.name}")

        return section

    def get_stats(self) -> dict:
        """Get processing statistics."""
        return {
            "processed_fields": self.processed_count,
            "errors": self.error_count,
            "openai_usage": self.openai_processor.get_usage_summary() if self.openai_processor else {},
        }


class Ai(Base):
    """Main plugin class for AI-powered report processing."""

    meta = {
        "name": "ai",
        "summary": "Process report sections using OpenAI with dynamic skill selection",
    }

    def __init__(self, **kwargs):
        """Initialize the plugin."""
        super().__init__(**kwargs)

        config_path_str = os.environ.get(
            "SYSREPTOR_CONFIG",
            str(Path.home() / ".sysreptor" / "config.yaml")
        )
        config_path = Path(config_path_str)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
            except (yaml.YAMLError, IOError) as e:
                logger.warning(f"Failed to read configuration file: {e}. Using defaults.")
                config = {}
        else:
            logger.debug(f"Configuration file not found at {config_path}. Using defaults.")
            config = {}

        ai_config = config.get('ai', {})

        self.openai_api_key = kwargs.get("openai_api_key") or ai_config.get("openai_api_key")
        self.model = kwargs.get("model") or ai_config.get("model", "gpt-5.4-mini")
        
        temp_value = kwargs.get("temperature") or ai_config.get("temperature", 0.7)
        try:
            self.temperature = float(temp_value)
            if not 0 <= self.temperature <= 2:
                raise ValueError(f"Temperature {self.temperature} outside valid range [0, 2]")
        except ValueError as e:
            raise ValueError(f"Invalid temperature value: {e}")
        self.task_prompt = kwargs.get("task") or ai_config.get("task_prompt")
        self.skills_dir = Path(kwargs.get("skills_dir") or ai_config.get("skills_dir", Path(__file__).parent / "skills"))
        self.dry_run = kwargs.get("dry_run", False)
        self.duplicate = kwargs.get("duplicate", False)

        skip_fields_input = kwargs.get("skip_fields") or ai_config.get("skip_fields")
        if skip_fields_input:
            if isinstance(skip_fields_input, str):
                self.skip_fields = [s.strip() for s in skip_fields_input.split(",")]
            else:
                self.skip_fields = list(skip_fields_input)
        else:
            self.skip_fields = []

        self._initialize_components()

    def _initialize_components(self):
        """Initialize processing components."""
        if not getattr(self, "openai_api_key", None):
            if self.dry_run:
                logger.warning("Running in dry-run mode without OpenAI API key")
            else:
                raise ValueError(
                    "OpenAI API key required. Configure with 'reptor ai --conf' "
                    "or set 'openai_api_key' in ~/.sysreptor/config.yaml under the 'ai:' section."
                )

        if not self.task_prompt:
            raise ValueError("Task prompt required. Use --task argument.")

        if not self.dry_run:
            self.openai_processor = OpenAIProcessor(
                api_key=self.openai_api_key,
                model=self.model,
                temperature=self.temperature,
            )
        else:
            self.openai_processor = None

        self.skill_loader = SkillLoader(self.skills_dir)
        self.skill_selector = AISkillSelector(openai_processor=self.openai_processor, dry_run=self.dry_run)
        self.prompt_builder = PromptBuilder()

        self.section_processor = SectionProcessor(
            skill_loader=self.skill_loader,
            skill_selector=self.skill_selector,
            prompt_builder=self.prompt_builder,
            openai_processor=self.openai_processor,
            skip_fields=self.skip_fields,
        )

    @property
    def user_config(self):
        """User configuration for API keys."""
        return [
            UserConfig(
                name="openai_api_key",
                friendly_name="OpenAI API Key",
                redact_current_value=True,
            ),
            UserConfig(
                name="task_prompt",
                friendly_name="Default Task Prompt",
            ),
        ]

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        """Add command-line arguments."""
        super().add_arguments(parser, plugin_filepath=plugin_filepath)

        parser.add_argument(
            "--task",
            metavar="TASK",
            help="Task prompt for processing sections",
            action="store",
            required=True,
        )

        parser.add_argument(
            "--model",
            metavar="MODEL",
            help="OpenAI model to use (default: gpt-5.4-mini)",
            action="store",
            default="gpt-5.4-mini",
        )

        parser.add_argument(
            "--temperature",
            metavar="TEMP",
            help="Sampling temperature 0-2 (default: 0.7)",
            action="store",
            type=float,
            default=0.7,
        )

        parser.add_argument(
            "--skills-dir",
            metavar="DIR",
            help="Directory containing skill .md files",
            action="store",
        )

        parser.add_argument(
            "--skip-fields",
            metavar="FIELDS",
            help="Fields to skip, comma-separated",
            action="store",
        )

        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            help="Preview processing without making API calls",
            action="store_true",
        )

        parser.add_argument(
            "--duplicate",
            dest="duplicate",
            help="Duplicate the project before processing (applies changes to copy, not original)",
            action="store_true",
        )

    def _process_project(self):
        """Process all sections and findings in the project."""
        self.display(
            f"Processing sections with task: '{self.task_prompt}'{' (dry run)' if self.dry_run else ''}"
        )

        if not self.dry_run:
            selected_skill = self._get_selected_skill()
            self.display(f"Selected skill: {selected_skill}")

        sections = [
            Finding(f, self.reptor.api.project_designs.project_design)
            for f in self.reptor.api.projects.get_findings()
        ] + self.reptor.api.projects.get_sections()

        sections_to_process = [
            s for s in sections 
            if getattr(s, "id", None) not in self.skip_fields
        ]

        for processed_index, section in enumerate(sections_to_process, 1):
            section_type = "Finding" if isinstance(section, Finding) else "Section"
            section_name = getattr(section, "id", None)

            self.display(f"Processing {section_type} {processed_index}/{len(sections_to_process)}: {section_name}...")

            try:
                if self.dry_run:
                    self._preview_section(section)
                else:
                    processed_section = self.section_processor.process_section(
                        section, self.task_prompt
                    )
                    self._save_section(processed_section)

            except Exception as e:
                self.warning(f"Error processing section: {e}")

        self._log_summary()

    def _duplicate_and_update_project(self) -> None:
        """Duplicate the project and switch to the duplicated version."""
        self.display(f"Duplicating project{' (dry run)' if self.dry_run else ''}.")
        if not self.dry_run:
            to_project_id = self.reptor.api.projects.duplicate_project().id
            self.display(f"Switched to duplicated project {to_project_id}.")
            self.reptor.api.projects.init_project(to_project_id)

    def _get_selected_skill(self) -> Optional[str]:
        """Get the selected skill for the current task."""
        available_skills = self.skill_loader.list_skills()
        return self.skill_selector.select(self.task_prompt, available_skills)

    def _preview_section(self, section: Union[Finding, Section]):
        """Preview what would be processed without making changes."""
        selected_skill = self._get_selected_skill()
        
        if selected_skill:
            skill_content = self.skill_loader.load_skill(selected_skill)
        else:
            skill_content = None

        for field in section.data:
            if field.type not in SectionProcessor.PROCESSABLE_TYPES:
                continue
            if field.name in self.skip_fields:
                continue
            if not field.value:
                continue

            prompt = self.prompt_builder.build(
                skill_content=skill_content,
                task_prompt=self.task_prompt,
                section_content=field.value,
            )
            self.display(f"\nField: {field.name}")
            self.display(f"Prompt:\n{prompt}\n")

    def _save_section(self, section: Union[Finding, Section]):
        """Save processed section back to the API."""
        section_data = section.data.to_dict()

        try:
            if isinstance(section, Finding):
                self.reptor.api.projects.update_finding(
                    section.id, {"data": section_data}
                )
            elif isinstance(section, Section):
                self.reptor.api.projects.update_section(
                    section.id, {"data": section_data}
                )
        except HTTPError as e:
            self.warning(f"Failed to save section {section.id}: {e.response.text}")

    def _log_summary(self):
        """Log processing summary."""
        stats = self.section_processor.get_stats()

        self.display(f"\nProcessing Summary:")
        self.display(f"  Fields processed: {stats['processed_fields']}")
        self.display(f"  Errors: {stats['errors']}")

        if stats["openai_usage"] and stats["openai_usage"].get("calls", 0) > 0:
            self.display(f"OpenAI Usage:")
            self.display(f"  API calls: {stats['openai_usage']['calls']}")
            self.display(f"  Tokens used: {stats['openai_usage']['tokens']}")
            self.display(f"  Errors: {stats['openai_usage']['errors']}")

        self.success(f"Project processed{' (dry run)' if self.dry_run else ''}.")

    def run(self):
        """Execute the plugin."""
        if self.duplicate:
            self._duplicate_and_update_project()
        self._process_project()


loader = Ai
