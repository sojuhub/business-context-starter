# Primary references and provenance

Public docs were reviewed while preparing this package; they can change. Verify the installed host's supported method before applying configuration.

- OpenAI plugin package / portable manifest / local marketplace: https://developers.openai.com/plugins/build/plugins
- OpenAI skills and explicit/implicit invocation: https://developers.openai.com/codex/skills
- OpenAI project instruction discovery: https://developers.openai.com/codex/guides/agents-md
- Claude plugin format and local testing: https://code.claude.com/docs/en/plugins
- Claude plugin technical reference: https://code.claude.com/docs/en/plugins-reference
- Composio Connect and existing-client options: https://docs.composio.dev/docs/composio-connect
- Composio account authentication: https://docs.composio.dev/docs/authentication
- Composio Instagram account support: https://docs.composio.dev/toolkits/instagram
- Company AI OS: https://github.com/DINAKAR-S/company-ai-os
- OpenAI business-context skill: https://github.com/openai/role-specific-plugins/blob/main/plugins/data-analytics/skills/gather-business-context/SKILL.md

## Actual reuse
This package reuses the supplied Company_Onboarding_v0.2_Design_and_Local_Pilot.zip's context_bridge.py unchanged.
Its 21 tests are retained with only the helper location adjusted.
The previous onboarding instructions are reduced and reorganized into two internal skills; no new connector engine is copied or claimed.
Retained original MIT notices are under the plugin's third_party directory.

## Affiliation and evidence boundary
This is an independent starter, not a Liam Ottley / Morningside / OpenAI / Anthropic / Composio product.
No proprietary AI Makeover package, full video transcript, customer data, or live authentication is included.
Do not present inferred product design as Liam's private method or claim directory certification.

## Copy-first update, 2026-09-18
Official native import and memory references are recorded in plugins/business-context-starter/references/PRIOR_CONTEXT.md. Native imports, ChatGPT exports and Claude memory exports were researched, NOT executed on an account. No proprietary transcript or provider importer was copied.
The bridge helper is unchanged from v0.3/v0.2. Copy-first entry, minimal existing-context reuse and an optional native-plugin route replace plugin-first onboarding.
