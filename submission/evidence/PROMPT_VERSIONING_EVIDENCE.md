# Prompt Versioning Evidence

The code supports prompt versioning with Langfuse:

- Prompt name from `LANGFUSE_PROMPT_NAME`, default `day13-chat`
- Prompt label from `LANGFUSE_PROMPT_LABEL`, default `production`
- Managed prompt version stored as `prompt_version`
- Fallback version `local-v1` when Langfuse is disabled or unavailable

Trace/generation metadata attached when Langfuse keys are configured:

- `prompt_name`
- `prompt_label`
- `prompt_version`
- `prompt_source`
- `prompt_fetch_error`
- token usage
- cost details

Public tests confirm the managed prompt version is linked to trace and generation metadata.
