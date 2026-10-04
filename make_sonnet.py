# make_sonnet.py - generate /build-sonnet from the live /build, so the two cannot drift.
#   python make_sonnet.py
# Reads ~/.claude/skills/build/SKILL.md and ~/.claude/agents/{coder,coder-ui}.md and writes
#   ~/.claude/skills/build-sonnet/SKILL.md
#   ~/.claude/agents/coder-sonnet.md, coder-ui-sonnet.md
# Since 2026-10-03 /build itself runs Sonnet for `coder` and Opus for `coder-ui`; this is the
# all-Sonnet variant. The only differences: both coder agents run claude-sonnet-5-5 under new names, and the
# skill text says so. The verifier and the orchestrator stay as they are.
# Edit /build, then rerun this. Never edit the generated files by hand.
import os, re

HOME = os.path.expanduser("~/.claude")
SONNET = "claude-sonnet-5-5"
DESCRIPTION = ("description: /build with Sonnet 5.5 on every coder seat, UI included (plain /build keeps the UI coder on Opus). The same "
               "orchestration: you hold the plan, `coder-sonnet` agents write, an Opus 5.5 `verifier` "
               "checks. Use ONLY when Chuck types /build-sonnet or asks for the Sonnet build; "
               "plain /build, orchestrate this and delegate this go to the build skill.")

# (old, new) pairs applied to SKILL.md before the agent renames. Each must match exactly once.
SKILL_EDITS = [
    ("# build — you orchestrate, the coders write", "# build-sonnet — you orchestrate, Sonnet 5.5 writes"),
    ("## Sonnet 5.5 writes logic, Opus 5.5 writes UI, plans and checks (set 2026-10-03)",
     "## Sonnet 5.5 writes everything, Opus 5.5 plans and checks"),
    ("**`coder` runs Sonnet 5.5; `coder-ui`, `verifier` and the orchestrator run Opus 5.5.**",
     "**`coder` and `coder-ui` run Sonnet 5.5; `verifier` and the orchestrator run Opus 5.5.** This is the all-Sonnet variant of /build, which keeps `coder-ui` on Opus."),
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
    text = once(text, r"^model: claude-(opus|sonnet)-5-5$", f"model: {SONNET}", f"{agent} model line")
    text = text.replace("Runs on Opus", "Runs on Sonnet 5.5")
    write(f"{HOME}/agents/{agent}-sonnet.md", rename_agents(text))

print("wrote skills/build-sonnet/SKILL.md, agents/coder-sonnet.md, agents/coder-ui-sonnet.md")
