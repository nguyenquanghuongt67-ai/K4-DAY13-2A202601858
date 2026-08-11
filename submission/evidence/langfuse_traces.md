# Langfuse Cloud trace evidence

Langfuse health check: `https://us.cloud.langfuse.com/api/public/health` → HTTP 200.

## Ten production traces using prompt version 2

All traces below were queried from the Langfuse API and contained
`prompt_name=day13-chat`, `prompt_label=production`,
`prompt_version=2`, and `prompt_source=langfuse`.

1. `82a646a95a436091cbcd2cd4f9f65c8d`
2. `4ecc6ea1ba8afade3560dc8205dca1e6`
3. `287a6d25c2aa27125c29ac00ab76672e`
4. `82c57a79655917014905cccbbf443b1c`
5. `7a00c3cdb295f24b8442bd9d6d38c9d8`
6. `195226425d2101e3c1b6dd561e799c21`
7. `700416071f2253602c05c752c7aec9e5`
8. `5c141d973c522089598d567d3815e3fd`
9. `80cfa79a33bd68f6dc5383ead9ac22f5`
10. `fe60f49dccf2699432cb168971df28bf`

## Real rollback

- Production label was moved to version 1.
- Rollback trace: `8f3beac64e659b639ffd8ce232e040c7`
- Metadata: `prompt_version=1`, `prompt_label=production`, `prompt_source=langfuse`
- The production label was restored to version 2 and verified through
  `get_prompt(..., label="production")`.

## Trace waterfall

Trace: `82a646a95a436091cbcd2cd4f9f65c8d`

- Trace name: `run`
- Generation observation: `ca4cbf2f46980725`
- Model: `claude-sonnet-4-5`
- Duration: approximately 151ms
- Usage: 39 prompt tokens, 149 completion tokens, 188 total tokens
- Cost: `0.002352` USD
- Prompt ID: `7d2ac412-0fca-424c-801d-abc85b49a4e9`
- Deep link: https://us.cloud.langfuse.com/project/cmsocpun500joad0e4lreykbg/traces/82a646a95a436091cbcd2cd4f9f65c8d
