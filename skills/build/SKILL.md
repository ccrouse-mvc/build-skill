---
name: build
description: Run a piece of work as an orchestrator — hold the plan and the model of the system yourself, hand the actual implementation to Opus 5.5 `coder` agents, and verify every claim they make before building on it. Use when Chuck types /build, or says orchestrate this, delegate this, run this as agents, break this up, or hands over a job big enough that one pass will not do it. Not for one-line fixes.
---

# build — you orchestrate, Opus 5.5 writes

Chuck's pattern: **one mind holds the plan, other minds do the work, and the one holding the
plan checks everything before it builds on it.**

Invoking this skill is the authorization to use the `Agent` tool. Outside it, the default
still stands: do not spawn agents unless asked.

## Opus 5.5 on every level (set 2026-09-22, "for now")

**Every seat runs Opus 5.5** — the orchestrator, every `coder`, `coder-ui` and `verifier`.
The three agents are pinned by
full ID in their frontmatter (`model: claude-opus-5-5`), not the `opus` alias, so a newer
alias target cannot quietly swap them out. That half is automatic.

**Effort (set 2026-09-22):** `coder` and `coder-ui` run at `medium`, Opus 5.5's own
default. The model thinks more per turn at a given effort than Opus 5 did, and at
`medium` it beats Opus 5 at `max` on Anthropic's own coding benchmark. `verifier` stays
at `high`, because thoroughness is the whole of its job. If coders start coming back
PARTIAL or REFUTED more than the 2026-09-18 run did, `high` is the first thing to restore.

The orchestrator is whatever model this session is running. **Do not pass `model:` on an
`Agent` call** — a per-call override beats the frontmatter pin and would undo it.

If you are not on Opus 5.5, say so in **one line** at the start — "running this on
Fable" — and then **carry on and do the work**. Do not stop, do not ask, do not make it a
decision.

**Never suggest a `/model` switch once the run is under way.** The prompt cache is
per-model, so a switch rewrites your entire context cold. Measured 2026-09-18: 23 of 26
mid-session switches did exactly that, at 330–510k tokens each. The model is chosen
before `/build`, in a fresh session, or not at all.

## When NOT to use this

A one-line fix. A question. Anything where reading the file and editing it is faster than
writing a brief. Delegation costs a full context load per agent and buys nothing on small
work — and Chuck's budget is real (his cathedral run was 40% of a week). If the job is
one file and one idea, just do it and say you did it directly.

---

## 1. Understand it yourself. Do not delegate this.

**This is the step that fails.** An orchestrator that farms out comprehension has no
model of the system, cannot write a decomposition that holds together, and cannot tell a
good report from a plausible one. Everything downstream is then guesswork wearing a
process.

Before any agent exists:

- **Re-read the project's `CLAUDE.md` — in your context, where it already is.** Conventions,
  the traps that already cost an hour, what looks wrong but is deliberate. Do not `Read`
  the file: that is a second copy you then pay for on every turn.
- **Read `ROADMAP.md` and any spec** the task belongs to, where the project has them.
- **Read the actual code** the change lands in. Enough to know what breaks.
- **Say the plan back in a few sentences** before spawning anything, so a wrong reading is
  caught while it is still cheap.

Use `Explore` agents for *breadth* — "where does X get set across this repo" — when a
sweep would otherwise dump twenty files into your context. Never use one to decide
anything.

## 2. Decompose so the pieces cannot collide

A good task for a `coder` is:

- **Independently verifiable.** There is a command whose output says whether it worked.
- **File-disjoint from anything running beside it.** Two agents in one file is how a
  parallel run corrupts itself. If two pieces share a file, they are sequential — or
  they are one piece.
- **Small enough to hold in one head**, big enough to be worth a context load. Roughly:
  it would take you thirty minutes — not three, and not ninety. **A piece that needs more
  than ~80 turns is two pieces** — the same unit as the coder's own budget and its
  `maxTurns`. A coder's cost per turn climbs the longer it runs; on 2026-09-23 the two
  coders past 90 turns cost 39% of all coder spend.
- **Written as a brief, not a title.** The agent sees your prompt and nothing else of
  this conversation. Name the files, the constraint, the acceptance check, and the things
  it must *not* touch.
- **Specific at the edges.** Say what happens when a dependency throws, the boundary
  values, any rounding, and which inputs are invalid or special. In the 2026-09-24 A/B
  test every non-UI defect, in all five versions, sat in a gap like that.

Write the whole decomposition down before you spawn anything — **in a file**,
`~/.claude/build-plans/<repo>-<job>.md`: the pieces, each brief, a status line per
piece that you keep current, and **the agent ID of every piece in flight** (the Agent
result gives it). A compact keeps the plan file and can lose the conversation; without the
ID written down you cannot `SendMessage` a running agent to resume or redirect it. The file is the plan, not the conversation, and it is what
makes a `/compact` or a fresh session safe mid-job. If you cannot write it, you do not
understand the task yet — go back to step 1.

## 3. Delegate

```
Agent(subagent_type: "coder", description: "...", prompt: <the brief>)
```

- **`coder` has no browser. `coder-ui` does** — plus the front-end standards preloaded —
  and pays for it in context on every turn. Use `coder-ui` only when the piece changes UI
  or its acceptance check has to run in a real browser. Everything else is `coder`.
- **Mechanical pieces go to `coder` too.** `coder-lite` (Sonnet 5) was trialed and retired
  on 2026-09-24: it saved under $0.10 a piece and shipped the A/B test's only hidden-test
  failure.
- **Parallel by default** when the pieces are file-disjoint: send them in **one message
  with multiple tool calls** so they actually run concurrently.
- **Sequential** when one piece's output is the next one's input, or when they share a
  file.
- **Background them** unless your very next action truly depends on the result. Chuck can
  interject while they run; a blocking call takes that away.
- **Never predict a pending agent's result.** If he asks before it lands, say it is still
  running. The notification is not something you write.

Keep it to a handful at a time. Ten agents on one repo is not ten times the throughput,
it is ten chances to collide.

No progress pulse. A cron-driven five-minute update was tried and removed on 2026-09-23:
created 18 times in one run, it fired once. Do not recreate it.

## Your own context is the multiplier

You hold the biggest context in the run, and every turn re-reads all of it. Measured
2026-09-23: five builds in one session over 27 hours put the orchestrator at 22% of the
bill with 10 cold rewrites; the one-build 2026-09-18 run after a compact was 9%.

- **One job per session.** Do not start a `/build` on top of a day of other work, and do
  not let one run for days. **If this session already holds a lot — earlier work, a
  resume, anything past roughly 100k tokens — make it the first line of your reply,
  before the plan:** "This session is already long; every turn of this build re-reads
  it. Start `/build` in a fresh session, or type `/compact` first." Then carry on. The
  2026-09-18 run started at 226k, and it is re-read on every orchestrator turn.
- **Trim your own shell output** — `| tail -n 15`, `| grep`. It is the biggest thing in
  your context and it is re-read on every turn that follows.
- **Between waves of a long run, tell Chuck he can compact — in exactly these terms:**
  "You can type `/compact` now; the plan file has everything." You cannot run it
  yourself, and "a compact is safe here" left him unsure whether you were doing it. Only
  say it when the plan file is current, in-flight agent IDs included. The 2026-09-18
  compact cut the orchestrator from 348k to 131k.

## 4. Verify. Never trust the report.

**A `coder` saying "tests pass" is a claim, not evidence** — written by the mind that just
wrote the code, at the least reliable moment there is.

**Hand the claims to a `verifier`.** It runs on Opus 5.5 and has no edit tools, so it cannot
quietly fix what it is judging:

```
Agent(subagent_type: "verifier", description: "...", prompt:
  <the original brief> + <the coder's report verbatim> + <what specifically to attack>)
```

Give it the report **verbatim**. It cannot see the coder's transcript either, and a
paraphrase is where the interesting discrepancy goes missing.

It answers CONFIRMED / REFUTED / **UNPROVEN** per claim. Treat UNPROVEN as its own
outcome, not a soft pass — it means nobody has checked, and that is the state most bugs
ship in.

**You still run the headline check yourself.** The verifier is a second pair of eyes, not
a delegation of your judgement — one `npm test` and a look at the diff costs you almost
nothing and it is the run you will be quoting in the report.

**A verifier is required — no judgement call — when the piece:**

- claims a *fix* rather than an addition, or
- touches locks, concurrency, transactions, migrations, or anything that runs on a schedule.

The measured catches were in that set (an ABBA deadlock, a write past a lock).
Otherwise spawn one when the change is subtle, spans files,
or touches UI, and skip it when the coder's evidence is a test that plainly exercises the
new path and you have read it.

If a piece came back PARTIAL or BLOCKED, or a verifier says REFUTED, **you** decide what
happens: send it back with the verifier's finding attached, take it on yourself, or cut it
and say so. Do not re-spawn the identical brief and hope.

## 5. Close it out the project's way

Every project here has its own end-of-work ritual and `CLAUDE.md` states it. Common shape:

- Tests green, with new assertions for new behavior.
- `ROADMAP.md` and `CHANGELOG.md` updated **in the same commit** — CineFile makes this
  explicit for every commit, one-line fixes included.
- Deploy where the project's dev loop is a deploy (CineFile runs only on the Pi).
- Commit **and push** — "commit" always means both.

**You do the commit, not the agents.** They were told not to, precisely because the commit
carries doc updates only you can see the shape of.

## 6. Report

**Brief, per his global `CLAUDE.md`**: what changed and what the result was, in a few
lines, with the numbers in them. The old "What I did / Caveats / What we should do next"
format was retired on 2026-09-08 — do not reconstruct it.

Two things an orchestrated run still has to say, a line or two each:

- **Say what each agent actually delivered**, including anything that came back partial.
  A run where two of five pieces needed a second pass is a more useful report than one
  that reads as if it all went cleanly.
- **Say what you verified yourself versus what you took on report.** That distinction is
  the whole point of step 4, and burying it makes the verification worthless.

---

## The agents

| Agent | Model | Can edit | For |
| --- | --- | --- | --- |
| `coder` | Opus 5.5 | yes | building one scoped, file-disjoint piece — no browser |
| `coder-ui` | Opus 5.5 | yes | the same, when the piece is UI or must be checked in a real browser |
| `verifier` | Opus 5.5 | **no** | attacking a claim the coder made |

`coder` and `coder-ui` share one body and differ only in tools. Both carry a `tools:`
whitelist on purpose: without one an agent inherits every tool schema in the session and
starts at ~88k tokens instead of ~35k, re-read on every turn.

The split is the point. `verifier` has no edit tools *by construction*, not by
instruction — a verifier that can fix what it finds stops verifying the first time it is
tempted, and starts colliding with whoever else is in that file.

Adding another is one more file in `~/.claude/agents/`, same frontmatter shape,
`model: claude-opus-5-5` (full ID, not the alias), **with a `tools:` line**. Keep the count low: every agent type is another
brief that can go stale.
