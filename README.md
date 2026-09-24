# /build

A Claude Code skill that turns one big job into a small team: one Claude plans, several
Claudes build, and a separate Claude checks their work before anything gets built on top of it.

Built by Chuck Crouse.

Works in **Claude Code** (it needs subagents, so it does not run in the claude.ai chat).

---

## *What's GitHub?*

Think of GitHub as Google Drive, but for code. People use it to share code and files like this
skill. You're on a GitHub page right now.

---

## What's a skill?

A skill is a small set of instructions you give to your AI. Think of it like a job description
for one kind of task. Once it's installed, you trigger it with a phrase and Claude knows exactly
how to handle that task.

This skill teaches Claude how to run a build the way a tech lead runs a team. It comes with three
**agents**, which are the team members Claude hands the work to.

---

## What it does

Ask one AI to build something big and it does everything in one long pass: it plans, writes,
tests and then tells you it all works. The same mind that wrote the code is grading it, at the
moment it is most sure it got everything right.

`/build` splits those jobs up:

1. **The orchestrator (your Claude) understands the job first.** It reads the project, the code
   and the plan, and says the plan back to you before any work starts.
2. **It breaks the job into pieces that can't collide.** Each piece gets its own files, a written
   brief, and a check that proves whether it worked. The plan goes in a file, so nothing is lost
   if the conversation gets compacted.
3. **`coder` agents build the pieces**, in parallel when they don't share files. A `coder-ui`
   agent takes the pieces that change a screen and checks them in a real browser.
4. **A `verifier` agent attacks every claim.** It has no ability to edit files, on purpose, so it
   can't quietly "fix" what it's supposed to be judging. It answers CONFIRMED, REFUTED or UNPROVEN
   for each claim.
5. **The orchestrator commits, pushes and reports** what each agent actually delivered, and what
   was checked versus taken on trust.

---

## When to use it

Good `/build` jobs:

- "Add the export feature from the roadmap: API, CSV writer and the settings screen."
- "Migrate these twelve endpoints to the new auth middleware."
- "Build the notification service from this spec, with tests."
- "Fix the three bugs in this issue list, and prove each one is gone."

Bad `/build` jobs:

- "Rename this variable." (one-line fix, just do it)
- "Why is this test failing?" (a question, not a build)
- "Tweak the button color." (one file, one idea)

Every agent costs a full load of context, so small jobs get slower and more expensive, not better.
The skill says so itself and does small work directly.

---

## How it was tuned

This isn't a first draft. Five versions of the skill built the same app from the same frozen
plan, and were then scored against 38 hidden tests plus a blind code review:

| Version | Hidden tests | Defects (blind review) | Cost per run |
| --- | --- | --- | --- |
| Before tuning | 38/38 | 2 | $5.86 |
| **This version** | **38/38** | **1** | $6.27 |
| Coders at low effort | 38/38 | 3 | $5.90 |
| Cheaper model for simple pieces | 37/38 | 2 | $5.30 |
| Coders at high effort | 38/38 | 2 | $5.81 |

The cheaper-model version saved about $0.10 per piece and shipped the only failing test, so that
idea was dropped. Rules that came out of the test are now in the skill: briefs must spell out edge
cases, and no agent deletes anything it didn't create.

---

## How to install it

### Option 1: Let Claude install it for you

Open Claude Code and paste this in:

> Please install the /build skill from this GitHub repo: https://github.com/ccrouse-mvc/build-skill
>
> Put `skills/build/SKILL.md` in `~/.claude/skills/build/`, and the three files in `agents/` in
> `~/.claude/agents/`. Walk me through anything you need from me.

### Option 2: Download the files and ask Claude to set them up

1. Download [skills/build/SKILL.md](./skills/build/SKILL.md) and the three files in
   [agents/](./agents).
2. Open Claude Code and paste this in:

> I just downloaded the /build skill (SKILL.md) and three agent files (coder.md, coder-ui.md,
> verifier.md). Can you install them for me?

### Where the files go

| File | Goes in |
| --- | --- |
| `skills/build/SKILL.md` | `~/.claude/skills/build/SKILL.md` |
| `agents/coder.md` | `~/.claude/agents/coder.md` |
| `agents/coder-ui.md` | `~/.claude/agents/coder-ui.md` |
| `agents/verifier.md` | `~/.claude/agents/verifier.md` |

Restart Claude Code after installing so it picks up the agents.

**Heads up:** this is the version I use every day, so it mentions my own setup (my name, my
projects, my `CLAUDE.md` rules). It works as is, and Claude will adapt those parts to yours. The
agents are pinned to Claude Opus 5.5, and `coder-ui` expects a `frontend-design-standards` skill,
which isn't in this repo. It runs without it.

---

## How to use it

Once installed, in any Claude Code session, type `/build` followed by the job, or say one of these:

- "orchestrate this"
- "delegate this"
- "run this as agents"
- "break this up"

Start big jobs in a fresh session. The orchestrator re-reads its whole conversation on every
turn, so a long session makes every step of the build cost more.

---

## What's in this repo

| Path | What it is |
| --- | --- |
| `skills/build/SKILL.md` | The skill: how the orchestrator plans, delegates, verifies and reports |
| `agents/coder.md` | Builds one scoped piece. No browser. |
| `agents/coder-ui.md` | The same as `coder`, plus a browser, for pieces that change a screen |
| `agents/verifier.md` | Checks the coders' claims. Can't edit anything. |
| `sync.ps1` | Copies my live copies from `~/.claude` into this repo so changes get committed |

---

## Credit

Built and tuned by Chuck Crouse, with Claude.
