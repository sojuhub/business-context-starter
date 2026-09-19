# Verification scope

Run the current checks with `python3 -m unittest discover -s tests -v` on Python
3.10 or newer. These test local bridge behavior and static package contracts.
They do not invoke an AI host, authenticate a provider or send a message.

Historical reports live in docs/HISTORICAL_TEST_RESULTS.md. They describe the
older package, not the current public commit. Current host acceptance items are
in docs/ACCEPTANCE.md; unrun items remain unverified.
