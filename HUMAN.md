# rp-why - what changes for you

rp-why gives you a mirror on how you work with your agent. It reads your past sessions and reports three things: how complex your prompts are (DOK), how you orchestrate tools (Tool Maturity), and where the collaboration sits (one of seven diagnostic zones).

## What it does to the agent

Nothing changes until you ask. When you run `/rp-why init`, `current`, `compare` or `overall`, the agent classifies your prompts and writes a report. `/rp-why ce` scores whether the agent acted on the trigger phrases in your AGENTS.md.

## When to use it

- At the end of a work block, with `/rp-why current`.
- Once, at the start, with `/rp-why init` to set a baseline.
- When you want the long view, with `/rp-why overall`.

Skip it when you need an answer, not a reflection. It measures practice; it doesn't do the work.

## Reserved for human judgment

The scores are a reading of your prompts, not a grade on you. What a zone means for your week, and whether to change anything, is yours to decide. A low DOK day can be a good execution day.

## What it reads and writes

- Reads your goose session database (SQLite, stored locally, `~/.local/share/goose/sessions/` on macOS and Linux).
- Reads the Implicit Commands table in your AGENTS.md for the `ce` report.
- Saves a baseline for later comparisons. The exact path isn't documented in the README.
- The README says all data stays local and nothing is sent externally.

## Cost

About 3,600 tokens of context (`token_cost` in bpm.json).

## Check it's working

Run `/rp-why current`. You should see a session snapshot with DOK, TM and ADT, a DOK distribution and a peak moment.

## Turn it off

`bpm remove rp-why`. Your saved baseline isn't documented as removed with it.
