---
description: Tick tracker items, only if a passing verification record exists
argument-hint: <item> [item...], e.g. W1.3.c
allowed-tools: Bash(epochzero-tutor:*)
---
Tick `$ARGUMENTS` in the curriculum tracker. Never edit the tracker yourself: the CLI takes the
tracker lock and enforces the gates (passing record, unlocked week).

1. Run `epochzero-tutor checkoff $ARGUMENTS`
2. If an item is **refused**, explain what's missing, based on the message:
   - "no passing record": `epochzero-tutor status` shows how the item is verified.
     `pytest` → `/verify`. `quiz` → the learner passes the quiz in the cockpit.
     `artifact` → the plan/walkthrough must exist, then `epochzero-tutor record <item> --kind artifact`.
     `tutor` → check it with the learner for real, then
     `epochzero-tutor record <item> --kind tutor --summary "<what you checked>"`.
   - "locked": the previous week isn't finished.
3. When an item is ticked, run `epochzero-tutor status` and say what's next in one line.
   If that finished a `[PROJECT]`'s code, `walkthrough.md` is next: have the learner explain one
   part of it back in their own words.
