# make_sonnet.py - generate /build-sonnet from the live /build, so the two cannot drift.
#   python make_sonnet.py
# Reads ~/.claude/skills/build/SKILL.md and ~/.claude/agents/{coder,coder-ui}.md and writes
#   ~/.claude/skills/build-sonnet/SKILL.md
#   ~/.claude/agents/coder-sonnet.md, coder-ui-sonnet.md
# The only differences: the two coder agents run claude-sonnet-5-5 under new names, and the
# skill text says so. The verifier and the orchestrator stay as they are.
# Edit /build, then rerun this. Never edit the generated files by hand.
import os, re

HOME = os.path.expanduser("~/.claude")
SONNET = "claude-sonnet-5-5"
DESCRIPTION = ("description: /build with Sonnet 5.5 coders (opt-in trial since 2026-10-02). The same "
               "orchestration: you hold the plan, `coder-sonnet` agents write, an Opus 5.5 `verifier` "
               "checks. Use ONLY when Chuck types /build-sonnet or asks for the Sonnet build; "
               "plain /build, orchestrate this and delegate this go to the build skill.")

# (old, new) pairs applied to SKILL.md before the agent renames. Each must match exactly once.
SKILL_EDITS = [
    ("# build — you orchestrate, Opus 5.5 writes", "# build-sonnet — you orchestrate, Sonnet 5.5 writes"),
    ("## Opus 5.5 on every level (set 2026-09-22, \"for now\")",
     "## Sonnet 5.5 writes, Opus 5.5 plans and checks (trial, 2026-10-02)"),
    ("**Every seat runs Opus 5.5** — the orchestrator, every `coder`, `coder-ui` and `verifier`.\nThe three agents are pinned by\nfull ID in their frontmatter (`model: claude-opus-5-5`), not the `opus` alias, so a newer\nalias target cannot quietly swap them out. That half is automatic.",
     "**`coder` and `coder-ui` run Sonnet 5.5; the orchestrator and `verifier` run Opus 5.5.**\nThe three agents are pinned by full ID in their frontmatter (`claude-sonnet-5-5` for the\ncoders, `claude-opus-5-5` for the verifier), not an alias, so a newer alias target cannot\nquietly swap them out. That half is automatic.\n\n**This is a trial.** In the 2026-10-02 test Sonnet coders cost about half as much per seat\nand the finished code matched all-Opus, but both Sonnet runs first shipped a lock bug that\nonly the verifier caught. So the verifier and probe rules in step 4 are not optional here.\nIn the report, give the run's verifier refutations and what your probes caught."),
    ("| `coder` | Opus 5.5 | yes |", "| `coder` | Sonnet 5.5 | yes |"),
    ("| `coder-ui` | Opus 5.5 | yes |", "| `coder-ui` | Sonnet 5.5 | yes |"),
]

def read(p): return open(p, encoding="utf-8", newline="").read()

def write(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="").write(text)

def rename_agents(text):
    text = re.sub(r"\bcoder-ui\b(?!-sonnet)", "coder-ui-sonnet", text)
    return re.sub(r"\bcoder\b(?![-.])", "coder-sonnet", text)

def once(text, pattern, repl, what):
    text, n = re.subn(pattern, repl, text, count=1, flags=re.M)
    assert n == 1, f"not found: {what}"
    return text

skill = read(f"{HOME}/skills/build/SKILL.md")
nl = "\r\n" if "\r\n" in skill else "\n"
for old, new in SKILL_EDITS:
    old, new = old.replace("\n", nl), new.replace("\n", nl)
    assert skill.count(old) == 1, f"SKILL.md edit does not match once: {old[:50]}"
    skill = skill.replace(old, new)
skill = rename_agents(skill)
skill = once(skill, r"^name: build$", "name: build-sonnet", "skill name")
skill = once(skill, r"^description: .*$", lambda m: DESCRIPTION, "skill description")
write(f"{HOME}/skills/build-sonnet/SKILL.md", skill)

for agent in ("coder", "coder-ui"):
    text = read(f"{HOME}/agents/{agent}.md")
    text = once(text, r"^model: claude-opus-5-5$", f"model: {SONNET}", f"{agent} model line")
    text = text.replace("Runs on Opus", "Runs on Sonnet 5.5")
    write(f"{HOME}/agents/{agent}-sonnet.md", rename_agents(text))

print("wrote skills/build-sonnet/SKILL.md, agents/coder-sonnet.md, agents/coder-ui-sonnet.md")
