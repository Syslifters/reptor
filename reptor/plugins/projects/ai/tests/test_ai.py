"""
Unit tests for the Ai module.

Tests cover all major components and integration scenarios.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai import (
    SkillLoader,
    AISkillSelector,
    SkillSelector,
    PromptBuilder,
    OpenAIProcessor,
    SectionProcessor,
)


def create_skill(skills_dir: Path, name: str, description: str|None = None, content: str|None = None):
    description = description or f'{name} skill'
    content = content or f'{name} skill content'

    sdir = skills_dir / name
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n---\n{content}")


class TestSkillLoader(unittest.TestCase):
    """Tests for SkillLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.skills_dir = Path(self.temp_dir.name)
        create_skill(self.skills_dir, "test_skill", "Test skill", "Test skill content")
        create_skill(self.skills_dir, "another_skill", "Another skill", "Another skill content")
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_load_existing_skill(self):
        """Test loading an existing skill file."""
        loader = SkillLoader(self.skills_dir)
        content = loader.load_skill("test_skill")
        self.assertEqual(content, "Test skill content")

    def test_load_nonexistent_skill(self):
        """Test loading a non-existent skill returns None."""
        loader = SkillLoader(self.skills_dir)
        content = loader.load_skill("nonexistent")
        self.assertIsNone(content)

    def test_list_skills(self):
        """Test listing available skills."""
        loader = SkillLoader(self.skills_dir)
        skills = loader.list_skills()
        self.assertEqual(set(s['name'] for s in skills), {"test_skill", "another_skill"})

    def test_list_skills_empty_directory(self):
        """Test listing skills in empty directory."""
        with TemporaryDirectory() as temp_dir:
            loader = SkillLoader(Path(temp_dir))
            skills = loader.list_skills()
            self.assertEqual(skills, [])


class TestAISkillSelector(unittest.TestCase):
    """Tests for AISkillSelector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.selector = AISkillSelector(openai_processor=MagicMock())
        self.available_skills = [{"name": s, "description": f"{s} description"} for s in ["grammar", "security", "technical", "expand"]]

    @patch("ai.OpenAI")
    def test_skill_selection_with_api(self, mock_openai):
        """Test AI-based skill selection with mocked OpenAI."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "grammar"
        mock_response.usage.total_tokens = 50
        mock_client.chat.completions.create.return_value = mock_response

        mock_processor = MagicMock()
        mock_processor.process.return_value = "grammar"
        selector = AISkillSelector(openai_processor=mock_processor)

        result = selector.select("fix spelling errors", self.available_skills)
        self.assertEqual(result, "grammar")

    def test_no_skills_available(self):
        """Test selection with no available skills."""
        result = self.selector.select("any task", [])
        self.assertIsNone(result)

    def test_fallback_to_first_skill_on_error(self):
        """Test fallback to first skill when API fails."""
        self.selector = AISkillSelector(openai_processor=MagicMock())
        self.selector.openai_processor.process.return_value = None
        
        result = self.selector.select("random task", self.available_skills)
        self.assertEqual(result, "grammar")


class TestPromptBuilder(unittest.TestCase):
    """Tests for PromptBuilder class."""

    def test_default_template(self):
        """Test building prompt with default template."""
        builder = PromptBuilder()
        prompt = builder.build(
            skill_content="Skill instructions",
            task_prompt="Do something",
            section_content="Content to process",
        )

        self.assertIn("Skill instructions", prompt)
        self.assertIn("Do something", prompt)
        self.assertIn("Content to process", prompt)

    def test_custom_template(self):
        """Test building prompt with custom template."""
        custom_template = "Skill: {skill}\nTask: {task}\nContent: {content}"
        builder = PromptBuilder(template=custom_template)
        prompt = builder.build(
            skill_content="Test skill",
            task_prompt="Test task",
            section_content="Test content",
        )

        self.assertEqual(
            prompt, "Skill: Test skill\nTask: Test task\nContent: Test content"
        )

    def test_none_skill_content(self):
        """Test building prompt with None skill content."""
        builder = PromptBuilder()
        prompt = builder.build(
            skill_content=None,
            task_prompt="Do something",
            section_content="Content",
        )

        self.assertIn("No specific skill provided", prompt)

    def test_prompt_deterministic(self):
        """Test that same inputs produce same output."""
        builder = PromptBuilder()
        prompt1 = builder.build("skill", "task", "content")
        prompt2 = builder.build("skill", "task", "content")
        self.assertEqual(prompt1, prompt2)


class TestOpenAIProcessor(unittest.TestCase):
    """Tests for OpenAIProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "sk-test-key"

    @patch("ai.OpenAI")
    def test_initialization(self, mock_openai):
        """Test processor initialization."""
        processor = OpenAIProcessor(api_key=self.api_key)
        self.assertEqual(processor.model, "gpt-5.4-mini")
        self.assertEqual(processor.temperature, 0.7)

    @patch("ai.OpenAI")
    def test_custom_parameters(self, mock_openai):
        """Test processor with custom parameters."""
        processor = OpenAIProcessor(
            api_key=self.api_key,
            model="gpt-3.5-turbo",
            temperature=0.5,
        )
        self.assertEqual(processor.model, "gpt-3.5-turbo")
        self.assertEqual(processor.temperature, 0.5)

    @patch("ai.OpenAI")
    def test_process_successful(self, mock_openai):
        """Test successful API call."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Processed result"
        mock_response.usage.total_tokens = 100
        mock_client.chat.completions.create.return_value = mock_response

        processor = OpenAIProcessor(api_key=self.api_key)
        result = processor.process("Test prompt")

        self.assertEqual(result, "Processed result")
        self.assertEqual(processor.usage_stats["calls"], 1)
        self.assertEqual(processor.usage_stats["tokens"], 100)

    @patch("ai.OpenAI")
    def test_get_usage_summary(self, mock_openai):
        """Test getting usage statistics."""
        mock_openai.return_value = MagicMock()
        processor = OpenAIProcessor(api_key=self.api_key)

        stats = processor.get_usage_summary()
        self.assertIn("calls", stats)
        self.assertIn("tokens", stats)
        self.assertIn("errors", stats)


class TestSectionProcessor(unittest.TestCase):
    """Tests for SectionProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.skill_loader = Mock()
        self.skill_selector = Mock()
        self.prompt_builder = Mock()
        self.openai_processor = Mock()

    def test_initialization(self):
        """Test section processor initialization."""
        processor = SectionProcessor(
            skill_loader=self.skill_loader,
            skill_selector=self.skill_selector,
            prompt_builder=self.prompt_builder,
            openai_processor=self.openai_processor,
        )

        self.assertEqual(processor.skill_loader, self.skill_loader)
        self.assertEqual(processor.processed_count, 0)
        self.assertEqual(processor.error_count, 0)

    def test_skip_fields_configuration(self):
        """Test skip fields configuration."""
        skip_fields = ["references", "affected_components"]
        processor = SectionProcessor(
            skill_loader=self.skill_loader,
            skill_selector=self.skill_selector,
            prompt_builder=self.prompt_builder,
            openai_processor=self.openai_processor,
            skip_fields=skip_fields,
        )

        self.assertEqual(processor.skip_fields, skip_fields)

    def test_process_section_with_fields(self):
        """Test processing a section with fields."""
        self.skill_loader.list_skills.return_value = ["grammar"]
        self.skill_loader.load_skill.return_value = "Skill content"
        self.skill_selector.select.return_value = "grammar"
        self.prompt_builder.build.return_value = "Built prompt"
        self.openai_processor.process.return_value = "Processed content"

        processor = SectionProcessor(
            skill_loader=self.skill_loader,
            skill_selector=self.skill_selector,
            prompt_builder=self.prompt_builder,
            openai_processor=self.openai_processor,
        )

        mock_section = Mock()
        mock_field = Mock()
        mock_field.type = "markdown"
        mock_field.name = "description"
        mock_field.value = "Original content"
        mock_section.data = [mock_field]

        result = processor.process_section(mock_section, "Fix grammar")

        self.assertEqual(mock_field.value, "Processed content")
        self.assertEqual(processor.processed_count, 1)

    def test_skip_non_processable_types(self):
        """Test that non-processable field types are skipped."""
        self.openai_processor.process.return_value = None

        processor = SectionProcessor(
            skill_loader=self.skill_loader,
            skill_selector=self.skill_selector,
            prompt_builder=self.prompt_builder,
            openai_processor=self.openai_processor,
        )

        mock_section = Mock()
        mock_field = Mock()
        mock_field.type = "number"  # Not processable
        mock_field.name = "severity"
        mock_field.value = "5"
        mock_section.data = [mock_field]

        processor.process_section(mock_section, "Do something")

        self.assertEqual(mock_field.value, "5")
        self.assertEqual(processor.processed_count, 0)

    def test_skip_empty_fields(self):
        """Test that empty fields are skipped."""
        processor = SectionProcessor(
            skill_loader=self.skill_loader,
            skill_selector=self.skill_selector,
            prompt_builder=self.prompt_builder,
            openai_processor=self.openai_processor,
        )

        mock_section = Mock()
        mock_field = Mock()
        mock_field.type = "markdown"
        mock_field.name = "description"
        mock_field.value = None  # Empty
        mock_section.data = [mock_field]

        processor.process_section(mock_section, "Do something")

        self.openai_processor.process.assert_not_called()
        self.assertEqual(processor.processed_count, 0)

    def test_get_stats(self):
        """Test getting processing statistics."""
        self.openai_processor.get_usage_summary.return_value = {
            "tokens": 500,
            "calls": 5,
            "errors": 0,
        }

        processor = SectionProcessor(
            skill_loader=self.skill_loader,
            skill_selector=self.skill_selector,
            prompt_builder=self.prompt_builder,
            openai_processor=self.openai_processor,
        )

        processor.processed_count = 10
        processor.error_count = 2

        stats = processor.get_stats()

        self.assertEqual(stats["processed_fields"], 10)
        self.assertEqual(stats["errors"], 2)
        self.assertEqual(stats["openai_usage"]["tokens"], 500)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.skills_dir = Path(self.temp_dir.name)
        (self.skills_dir / "test.md").write_text("Test skill")

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_complete_workflow_with_mocks(self):
        """Test complete processing workflow with mocked API."""
        loader = SkillLoader(self.skills_dir)
        mock_selector = MagicMock()
        builder = PromptBuilder()

        mock_processor = MagicMock()
        mock_processor.process.return_value = "Enhanced content"
        mock_processor.get_usage_summary.return_value = {
            "tokens": 100,
            "calls": 1,
            "errors": 0,
        }

        processor = SectionProcessor(
            skill_loader=loader,
            skill_selector=mock_selector,
            prompt_builder=builder,
            openai_processor=mock_processor,
        )

        mock_section = Mock()
        mock_field = Mock()
        mock_field.type = "markdown"
        mock_field.name = "content"
        mock_field.value = "Original content"
        mock_section.data = [mock_field]

        result = processor.process_section(mock_section, "Fix grammar")

        self.assertEqual(mock_field.value, "Enhanced content")
        stats = processor.get_stats()
        self.assertEqual(stats["processed_fields"], 1)
        self.assertEqual(stats["openai_usage"]["calls"], 1)


if __name__ == "__main__":
    unittest.main()
