# Verification scope

Run the current checks with `python3 -m unittest discover -s tests -v` on Python
3.10 or newer. These test local bridge behavior and static package contracts.
They do not invoke an AI host, authenticate a provider or send a message.

Separate actual Codex instruction-mode checks used three fictional businesses
on 2026-09-19. Their limits and opt-in reproduction command are in
[LOCAL_VALIDATION.md](docs/LOCAL_VALIDATION.md). Source publication does not
constitute a new tagged release or live-provider certification.

Historical reports live in docs/HISTORICAL_TEST_RESULTS.md. They describe the
older package, not the current public commit. Current host acceptance items are
in docs/ACCEPTANCE.md; unrun items remain unverified.
