# Prompt version evidence status

The application contract is implemented: every response log now records
`prompt_name`, `prompt_label`, `prompt_version`, and `prompt_source`, and the
agent sends the same metadata to the tracing client.

Langfuse Cloud was reconnected successfully (`/api/public/health` returned
HTTP 200). Prompt `day13-chat` resolved as follows:

- Candidate/production trace using version 2: `82a646a95a436091cbcd2cd4f9f65c8d`
- Additional version 2 traces: `4ecc6ea1ba8afade3560dc8205dca1e6`, `287a6d25c2aa27125c29ac00ab76672e`
- Rollback trace using production label on version 1: `8f3beac64e659b639ffd8ce232e040c7`
- Rollback request correlation ID: `req-132b3b93`
- Version 2 metadata: `prompt_name=day13-chat`, `prompt_label=production`,
  `prompt_version=2`, `prompt_source=langfuse`
- Version 1 rollback metadata: `prompt_name=day13-chat`,
  `prompt_label=production`, `prompt_version=1`, `prompt_source=langfuse`

After the rollback check, production was restored and verified to resolve to
version 2. The full trace list is available in the Langfuse project under the
run name `run` and the timestamps from this execution.
