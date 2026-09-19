# Business Onboarding concept demo

This is the existing approved v2 static demonstration, included with the README.
It reuses the local handoff's `landing/index.html`, with the repository-status
notice updated for the public instruction alpha. Its UI and behavior were not rebuilt. The original [MIT notice](LICENSE) is retained.

From the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs/demo
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). Stop with `Ctrl+C`.
No dependencies, environment variables or build step are needed for the page.

## What to try

- Compare the two authored replies to the fictional cafe inquiry.
- Switch to the social-post example; both examples use the same sample business.
- Expand the rule editor and change the staff-approval threshold or tone.
- Inspect the sample brief export. The inquiry dialog only prepares a local draft.

The page uses deterministic JavaScript, not an AI model. Browser storage holds
fictional preferences, not business context shared with Codex. No private account,
booking system, analytics service or model API is connected. No inquiry recipient
is configured, and nothing is sent. Service copy is a concept, not a confirmed offer.

The GitHub link points to the public instruction-alpha repository. The page is served locally; no hosted demo is claimed.

The README's [comparison screenshot](../assets/cafe-comparison.png) is an existing
authored-demo asset, visually checked against the current page. It does not prove
model performance, mobile acceptance or fresh-session context retrieval.

