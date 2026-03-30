# sonic-trace

Correlate an IP prefix across **FRR**, the **Linux kernel routing table**, and **SONiC’s APPL_DB** (`ROUTE_TABLE`) so you can see whether traffic is going through the normal SONiC pipeline or bypassing it.

Designed for a **Containerlab**-style setup where FRR and the kernel live in one container and Redis runs in another (see [Prerequisites](#prerequisites)).

## What it reports

For a given prefix, the tool checks presence in each layer and assigns a **path** label:

| Path | Meaning |
|------|--------|
| **SONiC pipeline** | Prefix is in FRR and in APPL_DB (typical managed route). |
| **FRR → kernel (bypass SONiC)** | In FRR and kernel, but not in APPL_DB. |
| **FRR not installed in kernel** | In FRR but missing from the kernel table. |
| **unknown** | Anything else (e.g. only in one unexpected layer). |

## Requirements

- Python **3.12+**
- **Docker**, with your lab containers running
- Container names and commands must match what the code expects (see below)

### Prerequisites (hardcoded lab)

The fetchers assume:

| Source | How it’s read |
|--------|----------------|
| FRR | `docker exec clab-spine-leaf-leaf-1 vtysh -c "show ip route json"` |
| Kernel | `docker exec clab-spine-leaf-leaf-1 ip route` |
| APPL_DB | `ROUTE_TABLE:*` keys via `redis-cli` on `clab-spine-leaf-leaf-1`, hashes read from the `database` container |

Adjust `frr.py`, `kernel.py`, and `redis.py` if your topology uses different container names or Redis layout.

## Install

Using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
cd sonic-trace
uv sync
```

Or with pip:

```bash
pip install -e .
```

## Usage

### CLI — trace one prefix

```bash
uv run python main.py 10.0.0.1/32
```

Prints a short summary (FRR / KERNEL / APPL_DB checks and path) plus the full `trace_route` JSON.

### TUI — browse all FRR prefixes

```bash
uv run python tui.py
```

- Lists prefixes from FRR; selecting one shows the same report as the CLI.
- **r** reloads data, **q** quits.

## Project layout

| Module | Role |
|--------|------|
| `correlate.py` | `trace_route`, `format_trace_report` |
| `frr.py` | FRR JSON routes |
| `kernel.py` | Parsed `ip route` output |
| `redis.py` | APPL_DB `ROUTE_TABLE` keys and hashes |
| `utils.py` | Prefix normalization (e.g. host routes as `/32`) |
| `main.py` | Single-prefix CLI |
| `tui.py` | Textual browser UI |
