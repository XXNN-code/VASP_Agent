# VASP Agent

This repository is the public companion repository for the manuscript:

**VASP Agent: An Agentic Framework for Autonomous First-principles Calculations**

It contains the VASP Agent runtime code, the skill library, the inputs of all
reported experiments, and for each experiment its scripts and results. Raw
VASP outputs and agent session logs are available from the corresponding
authors upon reasonable request.

> **This repository is a modified fork of
> [Phoinikas03/VASP_Agent](https://github.com/Phoinikas03/VASP_Agent).**
> It keeps the agent runtime, skill library, and experiment data unchanged and
> only adapts the front end for headless, terminal-only deployment. See
> [Fork: what changed](#fork-what-changed) for the full list.

## Fork: what changed

- **Upstream**: [Phoinikas03/VASP_Agent](https://github.com/Phoinikas03/VASP_Agent),
  base commit `a40b734` ("VASP Agent public repository").
- **Goal**: run the agent on a machine without a desktop environment — no
  browser, no GUI, optionally no interactive TTY (SSH scripts, cron, batch
  schedulers).

Changes, all confined to the entry point and its documentation:

1. **CLI-first usage.** `--mode cli` was and remains the default; the web UI is
   only imported when `--mode web` is passed explicitly, and `aiohttp` is loaded
   lazily, so nothing GUI-related is required on a headless host.
2. **`--prompt` one-shot mode** (`src/main.py: _run_prompt_once`). Submits a
   single instruction, prints the reply, and exits on the first `ResultMessage`.
   Useful from SSH one-liners, cron jobs, and workflow engines where no
   interactive stdin exists. Mutually exclusive with `--mode web` (exit code 2).
3. **Claude Code CLI resolution** (`src/main.py: resolve_claude_cli`). Resolution
   order: (1) explicit override via `VASP_AGENT_CLI_PATH` / `CLAUDE_CODE_PATH`;
   (2) a working system-wide `claude` on `PATH` or in a well-known install
   location, verified with `claude --version`; (3) on-demand installation via
   `install.sh` (curl/wget) with an `npm install -g @anthropic-ai/claude-code`
   fallback; (4) the CLI bundled with `claude-agent-sdk` as a last resort. The
   result is resolved once per process and passed through `cli_path`.
4. **Documentation.** README gained a headless/CLI section describing the
   interactive REPL, session resume with `--dir`, and `--prompt` usage.

Not changed: `src/scheduler`, `src/tool_wrapper`, the `.claude/skills` library,
`webui/`, `experiments/`, and `data/`. Results remain reproducible against
upstream.

## Repository Layout

```text
main.py             CLI/Web entry point
batch_runner.py     Batch runner for the structural-relaxation and band-gap tasks
src/                Agent runtime, tools, scheduler, and LiteLLM bridge
webui/              Local web interface
tools/              Repository export helper
.claude/skills/     VASP Agent skill library
data/               Experiment inputs: task tables, initial structures, reference values
experiments/        One directory per experiment: scripts and results
```

## Experiments

`experiments/README.md` maps every experiment to its manuscript tables and
figures and to the scripts that regenerate its results. Experiments 01–05 were
reported in the original submission; experiments 06–09 were added in the
revision:

| Directory | Experiment |
| --- | --- |
| `01_structural_relaxation` | 40 relaxations vs. LLM-based workflow baselines |
| `02_bandgap` | 24 PBE-to-HSE band gaps vs. LLM-based workflow baselines |
| `03_sol27lc_dreams` | Sol27LC lattice constants vs. DREAMS |
| `04_co_pt111_adsorption` | CO/Pt(111) site preference |
| `05_failure_recovery` | Failure taxonomy and LiFePO4 recovery case |
| `06_sol27lc_deepseek_v4_repeats` | Three repeated Sol27LC runs with DeepSeek v4 |
| `07_atomate2_comparison` | Comparison with atomate2 and custodian |
| `08_skill_ablation` | Sol27LC with and without domain skills |
| `09_mgo_phonon` | MgO phonon workflow and generation of `workflow-phonon` |

## Installation

```bash
conda create -n vasp-agent python=3.10 -y
conda activate vasp-agent
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` for the model endpoint and local scientific resources. VASP
pseudopotentials are not redistributed; set `PMG_VASP_PSP_DIR` to a local
licensed POTCAR library before running VASP tasks.

## Running Tasks

List the structural-relaxation and band-gap tasks:

```bash
python batch_runner.py --tasks relax bandgap --dry-run
```

Run selected tasks after configuring the model endpoint, VASP executable, and
POTCAR path:

```bash
python batch_runner.py --tasks relax --materials Al AlN
python batch_runner.py --tasks bandgap --materials Si GaN
```

Interactive runs can be launched with:

```bash
python main.py --mode web
```

### Headless / CLI usage (no GUI required)

The default mode is the interactive terminal REPL — no browser or display needed.
The web UI is only loaded when `--mode web` is passed explicitly, so on headless
servers (SSH, no GUI) simply run:

```bash
python main.py
```

You get a `You> / Agent>` conversation loop in the terminal; tool calls and results
are printed inline. Type `quit` / `exit` / `q` to leave (the trajectory is archived
and the consolidation flow is offered on exit; use `quit!` to skip it, Ctrl-C to
leave immediately). Re-enter an existing workspace and resume the previous session:

```bash
python main.py --dir runs/mytask
```

For non-interactive use (scripts, cron, remote SSH one-liners), pass a single
instruction with `--prompt`; the agent replies once and the process exits:

```bash
python main.py --prompt "Build the INCAR/KPOINTS/POSCAR for a PBE relaxation of Si and run it"
python main.py --dir runs/mytask --prompt "Check the OSZICAR of the last run and tell me if it converged"
```

Model endpoint configuration (`.env`) is identical for both modes.

### Claude Code CLI resolution (fork addition)

At startup the agent looks for a system-wide `claude` binary first, installs one
on demand if nothing is found, and only then falls back to the CLI bundled with
`claude-agent-sdk`:

| Order | Source |
| --- | --- |
| 1 | `VASP_AGENT_CLI_PATH` / `CLAUDE_CODE_PATH` environment variable |
| 2 | `claude` on `PATH`, or at `~/.local/bin/claude`, `/usr/local/bin/claude`, `/usr/bin/claude`, Homebrew prefixes (verified with `claude --version`) |
| 3 | On-demand install: `install.sh` via curl/wget, then `npm install -g @anthropic-ai/claude-code` |
| 4 | The CLI bundled inside the `claude-agent-sdk` wheel |

The resolved path is printed once at startup (`[claude-code] system CLI OK: ...`).
On an offline or restricted host, pre-install Claude Code (or set the override
variable) so step 2 succeeds and no download is attempted.

Drivers for the other experiments are documented in the corresponding
`experiments/` directories.

