AI-powered report section processing using **OpenAI**.

## Examples
```
reptor ai --task "Fix all grammar and spelling errors" --dry-run
reptor ai --task "Expand findings with technical details" --duplicate
reptor ai --task "Translate to Italian" --model gpt-5.4-mini --duplicate
```

## Installation
Make sure you installed required dependencies by using `pip install reptor[ai]` or `pip install reptor[all]`.

For OpenAI support, also install: `pip install openai`

## Configuration
The Ai module needs additional configurations, which you can add to `~/.sysreptor/config.yaml`:

### OpenAI Configuration
```
ai:
  openai_api_key: <your-openai-api-key>
  model: gpt-5.4-mini  
  temperature: 0.7
  skip_fields:
  - affected_components
  - references
```

Configuration options:
- `openai_api_key`: Your OpenAI API key (required)
- `model`: Model to use. Check all models at [https://developers.openai.com/api/docs/models](https://developers.openai.com/api/docs/models) (default: `gpt-5.4-mini`)

- `temperature`: Sampling temperature 0-2 (default: `0.7`)
- `skip_fields`: Fields to skip during processing (optional)

`skip_fields` can be used to skip processing of certain report or finding fields.

## Skills

The plugin includes pre-built skills like:

- **grammar**: Fix spelling, grammar, and punctuation
- **expand**: Expand content with additional details
- **translate**: Translate while preserving markdown formatting

Skills are **automatically selected** based on your task prompt, or you can explicitly reference a skill name in your task.
Custom skills can be added in the skills/ directory.


## Usage

```
reptor ai [options]
```

### Options
```
--task TASK                 Task description for the AI (required)
--model MODEL              OpenAI model to use (default: gpt-5.4-mini)
--temperature TEMP         Sampling temperature 0-2 (default: 0.7)
--skip-fields FIELDS      Fields to skip, comma-separated
--skills-dir DIR          Custom skills directory
--dry-run                 Preview without making API calls
--duplicate               Duplicate project before processing (applies to copy, not original)
--conf                    Configure API credentials
```

## Examples by Use Case

### Fix Grammar
```bash
# Modify in-place
reptor ai --task "Fix all grammar and spelling errors"

reptor ai --task "Fix all grammar and spelling errors" --duplicate
```

### Improve Security Findings
```bash
reptor ai \
  --task "Improve security findings with business impact and remediation steps" \
  --skip-fields "affected_components,references" \
  --duplicate
```

### Expand Technical Details
```bash
reptor ai \
  --task "Expand findings with additional technical details and examples" \
  --duplicate
```

### Translate Content
```bash
reptor ai \
  --task "Translate to German" \
  --model gpt-5.4-mini \
  --duplicate
```

### Preview Before Processing
```bash
reptor ai --task "Your task here" --dry-run
```