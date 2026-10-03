---
name: build-sonnet
description: /build with Sonnet 5.5 coders (opt-in trial since 2026-10-02). The same orchestration: you hold the plan, `coder-sonnet` agents write, an Opus 5.5 `verifier` checks. Use ONLY when Chuck types /build-sonnet or asks for the Sonnet build; plain /build, orchestrate this and delegate this go to the build skill.
---

# build-sonnet — you orchestrate, Sonnet 5.5 writes

Chuck's pattern: **one mind holds the plan, other minds do the work, and the one holding the
plan checks everything before it builds on it.**

Invoking this skill is the authorization to use the `Agent` tool. Outside it, the default
still stands: do not spawn agents unless asked.

## Sonnet 5.5 writes, Opus 5.5 plans and checks (trial, 2026-10-02)

**`coder-sonnet` and `coder-ui-sonnet` run Sonnet 5.5; the orchestrator and `verifier` run Opus 5.5.**
The three agents are pinned by full ID in their frontmatter (`claude-sonnet-5-5` for the
coders, `claude-opus-5-5` for the verifier), not an alias, so a newer alias target cannot
quietly swap them out. That half is automatic.

**This is a trial.** In the 2026-10-02 test Sonnet coders cost about half as much per seat
and the finished code matched all-Opus, but both Sonnet runs first shipped a lock bug that
only the verifier caught. So the verifier and probe rules in step 4 are not optional here.
In the report, give the run's verifier refutations and what your probes caught.

**Effort (set 2026-09-22):** `coder-sonnet` and `coder-ui-sonnet` run at `medium`, Opus 5.5's own
default. The model thinks more per turn at a given effort than Opus 5 did, and at
`medium` it beats Opus 5 at `max` on Anthropic's own coding benchmark. `verifier` stays
at `high`, because thoroughness is the whole of its job. If coders start coming back
PARTIAL or REFUTED more often, `high` is the first thing to restore.

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
- **Have the plan checked for holes, then settle them.** Once you have read the spec, spawn
  one `verifier` on the spec alone, before any code exists: "list every place where coders
  working from this spec would have to guess. For each pair of things that meet at runtime
  (an effect on an enemy that moves itself, an option against the base case, one input on
  different screens, a limit and whatever creates things under it), does the spec say what
  happens? Also contradictions, limits with exceptions, and any option that could make the
  base case worse. Top 15 by how badly a user would notice, each with a proposed decision;
  about 30 tool calls." Decide every hole it lists, and every one you see yourself, and write
  the decisions into the plan file. On 2026-10-02 this took 2 minutes and under $1 and found
  38 holes in one game spec, including the ones behind two shipped bugs; it missed others,
  so it does not replace the checks in steps 4 and 5.
- **Say the plan back in a few sentences** before spawning anything, so a wrong reading is
  caught while it is still cheap.

Use `Explore` agents for *breadth* — "where does X get set across this repo" — when a
sweep would otherwise dump twenty files into your context. Never use one to decide
anything.

## 2. Decompose so the pieces cannot collide

A good task for a `coder-sonnet` is:

- **Independently verifiable.** There is a command whose output says whether it worked.
- **File-disjoint from anything running beside it.** Two agents in one file is how a
  parallel run corrupts itself. If two pieces share a file, they are sequential — or
  they are one piece.
- **Small enough to hold in one head**, big enough to be worth a context load. Roughly:
  it would take you thirty minutes — not three, and not ninety. **A piece that needs more
  than ~80 turns is two pieces** — the same unit as the coder-sonnet's own budget and its
  `maxTurns`. A coder-sonnet's cost per turn climbs the longer it runs; on 2026-09-23 the two
  coders past 90 turns cost 39% of all coder-sonnet spend.
- **Written as a brief, not a title.** The agent sees your prompt and nothing else of
  this conversation. Name the files, the constraint, the acceptance check, and the things
  it must *not* touch.
- **Specific at the edges.** Say what happens when a dependency throws, the boundary
  values, any rounding, and which inputs are invalid or special. In the 2026-09-24 A/B
  test every non-UI defect, in all five versions, sat in a gap like that.
- **Named, where the spec is loose.** A brief for look, feel, sound or copy lists every
  effect it wants by name, not the category. That is where two runs of one spec differed
  most.

**Write down the seams.** The plan file gets a Seams table: one row per place where one
piece's output is another's input, or new code meets existing code. Each row names the
producer, the consumer, the exact names that cross (event kinds, keys, hook names), and one
command that runs the real producer into the real consumer. A test that feeds a hand-made
stand-in for another piece's output does not count. On 2026-10-02 a build shipped with every
weapon silent: the game emitted `w_bullet`, the audio was keyed `bullet`, and the audio test
fed itself `bullet`.

Write the whole decomposition down before you spawn anything — **in a file**,
`~/.claude/build-plans/<repo>-<job>.md`: the pieces, the Seams table, a status line per
piece that you keep current, the test count before wave 1 (pass, fail, skip), and **the
agent ID of every piece in flight** (the Agent result gives it). **Write each brief once,
to its own file** beside the plan (`<repo>-<job>.briefs/<piece>.md`), and make the Agent
prompt one line: read the brief at that path. A brief pasted into both the plan and the
prompt is paid for twice, and briefs were the biggest thing in the orchestrator's context. A compact keeps the plan file and can lose the conversation; without the
ID written down you cannot `SendMessage` a running agent to resume or redirect it. The file is the plan, not the conversation, and it is what
makes a `/compact` or a fresh session safe mid-job. If you cannot write it, you do not
understand the task yet — go back to step 1.

## 3. Delegate

```
Agent(subagent_type: "coder-sonnet", description: "...", prompt: <the brief>)
```

- **`coder-sonnet` has no browser. `coder-ui-sonnet` does** — plus the front-end standards preloaded —
  and pays for it in context on every turn. Use `coder-ui-sonnet` only when the piece changes UI
  or its acceptance check has to run in a real browser. Everything else is `coder-sonnet`.
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

## Your own context is the multiplier

You hold the biggest context in the run, and every turn re-reads all of it.

- **One job per session.** Do not start a `/build` on top of a day of other work, and do
  not let one run for days. **If this session already holds a lot — earlier work, a
  resume, anything past roughly 100k tokens — make it the first line of your reply,
  before the plan:** "This session is already long; every turn of this build re-reads
  it. Start `/build` in a fresh session, or type `/compact` first." Then carry on.
- **Trim your own shell output** — `| tail -n 15`, `| grep`. It is re-read on every turn
  that follows.
- **Between waves of a long run, tell Chuck he can compact — in exactly these terms:**
  "You can type `/compact` now; the plan file has everything." You cannot run it
  yourself, and "a compact is safe here" left him unsure whether you were doing it. Only
  say it when the plan file is current, in-flight agent IDs included.

## 4. Verify. Never trust the report.

**A `coder-sonnet` saying "tests pass" is a claim, not evidence** — written by the mind that just
wrote the code, at the least reliable moment there is.

**Hand the claims to a `verifier`.** It runs on Opus 5.5 and has no edit tools, so it cannot
quietly fix what it is judging:

```
Agent(subagent_type: "verifier", description: "...", prompt:
  <the spec section the piece implements> + <the brief's path> + <the coder-sonnet's report verbatim>
  + <what specifically to attack>)
```

Give it the report **verbatim**. It cannot see the coder-sonnet's transcript either, and a
paraphrase is where the interesting discrepancy goes missing. Give it the spec too: it
judges the code against the spec first and the report second. On 2026-10-02 a verifier
given only the report confirmed a rule that matched the code and contradicted the spec.

It answers CONFIRMED / REFUTED / **UNPROVEN** per claim. Treat UNPROVEN as its own
outcome, not a soft pass — it means nobody has checked, and that is the state most bugs
ship in.

**You still run the headline check yourself.** The verifier is a second pair of eyes, not
a delegation of your judgement — one `npm test` and a look at the diff costs you almost
nothing and it is the run you will be quoting in the report.

**A verifier is required — no judgement call — when the piece:**

- claims a *fix* rather than an addition,
- touches locks, concurrency, transactions, migrations, or anything that runs on a schedule, or
- is the piece every other piece builds on (the core model, the shared engine).

The measured catches were in that set (an ABBA deadlock, a write past a lock, rule breaks
in a game's core). Everything else gets your probe, and the whole product gets one
verifier at close-out (step 5).

**Every piece without a verifier gets a probe from you.** Read its diff, then run one
quick check that would fail if the piece were wrong at an edge: a boundary value, a
half-cent rounding, `1` against `"1"`. Seconds, not a verifier. On 2026-10-02 two
orchestrators that ran a one-line rounding probe caught a bug that two who only read the
same code shipped.

If a piece came back PARTIAL or BLOCKED, or a verifier says REFUTED, **you** decide what
happens, under one rule: **fix it yourself only when it is one file and one rule**, then run
the test that covers it. Your edits get no verifier, so keep them that small. Anything
bigger goes back to the same coder-sonnet by `SendMessage`, with the finding attached. Or cut it
and say so. Do not re-spawn the identical brief and hope. On 2026-10-02 an orchestrator that
fixed nine refutations itself created the run's worst bug in one of those edits.

## 5. Close it out the project's way

**First, one whole-product verifier.** After the last piece lands, spawn one `verifier`
with the spec, the plan's Seams table and the build: no briefs, no coder-sonnet reports. Tell it to
attack three things by running code: every seam (the real producer into the real consumer),
every rule no single piece owns (limits, performance budgets, skipped tests), and the
product as a user (every control on every screen, every option against its own
description). On an existing codebase, scope it to the diff and whatever calls into it.
**Give it a budget of about 30 tool calls.** On 2026-10-02 that cost $1.12 and 11 minutes
per build and found 4 of 7 major bugs that six per-piece verifiers had missed, plus two
nobody had found; runs without a budget took 63-80 calls, $3-4 and up to 31 minutes, and
found the same bugs.

Its findings get **one** fix wave, under the rule in step 4. Then rerun only its failing
probes, not a second verifier. Whatever still fails goes in the report.

**Green means 0 fail, 0 todo, 0 skip**, and nothing that passed before wave 1 now fails. A
`todo` parked over a real failure is a failure. **Every item you would report as "taken on
report" gets a probe now**, or the report's first line says PARTIAL. On 2026-10-02 both
builds' reports named, as taken on report, exactly the areas their major bugs were in.

Then the project's own end-of-work ritual, which its `CLAUDE.md` states. Common shape:

- Tests green, with new assertions for new behavior.
- `ROADMAP.md` and `CHANGELOG.md` updated **in the same commit** — CineFile makes this
  explicit for every commit, one-line fixes included.
- Deploy where the project's dev loop is a deploy (CineFile runs only on the Pi).
- Commit **and push** — "commit" always means both.

**You do the commit, not the agents.** They were told not to, precisely because the commit
carries doc updates only you can see the shape of.

## 6. Report

**Brief, per his global `CLAUDE.md`**: what changed and what the result was, in a few
lines, with the numbers in them.

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
| `coder-sonnet` | Sonnet 5.5 | yes | building one scoped, file-disjoint piece — no browser |
| `coder-ui-sonnet` | Sonnet 5.5 | yes | the same, when the piece is UI or must be checked in a real browser |
| `verifier` | Opus 5.5 | **no** | attacking a piece against the spec, and the whole product before commit |

Adding another is one more file in `~/.claude/agents/`, same frontmatter shape,
`model: claude-opus-5-5` (full ID, not the alias), **with a `tools:` line**. Keep the count low: every agent type is another
brief that can go stale.
