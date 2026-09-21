# Start with one message

Copy this into Codex, Claude Code, Hermes or OpenClaw:

```text
Read https://github.com/sojuhub/business-context-starter, set it up in my current workspace, and guide me through business onboarding.
```

The same instruction starts the same repository-read workflow in each tool.
Your agent reads [START_HERE.md](START_HERE.md), prepares the files using its own
available tools, and asks about your business. No manual plugin installation is
needed. The agent asks which services you use and what you do there, confirms business-source candidates, then proposes a business-only reading scope and reads approved sources. It follows up on missing knowledge, saves the reviewed result and verifies reuse in a fresh session before calling onboarding complete. Account connections still use that tool's normal login and permission flow. Repository preparation alone is not completed onboarding.
