import json

from utils import normalize_prefix
from frr import get_routes
from kernel import get_kernel_routes
from redis import get_apply_db_routes


def format_trace_report(prefix: str, result: dict) -> str:
    """Human-readable report matching main.py output plus trace_route JSON."""
    summary = (
        f"\nPrefix: {prefix}\n\n"
        f"FRR:       {'✔' if result['frr'] else '✘'}\n"
        f"KERNEL:    {'✔' if result['kernel'] else '✘'}\n"
        f"APPL_DB:   {'✔' if result['appl_db'] else '✘'}\n\n"
        f"Path: {result['path']}\n"
    )
    raw = json.dumps(result, indent=2)
    return f"{summary}\n\ntrace_route result:\n{raw}\n"


def trace_route(prefix, frr, kernel, appl_db):
    """
    Trace the route for a given prefix.
    """
    prefix = normalize_prefix(prefix)
    
    result = {
        "frr": prefix in frr,
        "kernel": prefix in kernel,
        "appl_db": prefix in appl_db,
    }

    # Classification
    if result["frr"] and result["kernel"] and not result["appl_db"]:
        result["path"] = "FRR → kernel (bypass SONiC)"
    elif result["frr"] and result["appl_db"]:
        result["path"] = "SONiC pipeline"
    elif result["frr"] and not result["kernel"]:
        result["path"] = "FRR not installed in kernel"
    else:
        result["path"] = "unknown"

    return result

if __name__ == "__main__":
    frr = get_routes()
    kernel = get_kernel_routes()
    appl_db = get_apply_db_routes()
    print(trace_route("10.10.10.1/32", frr, kernel, appl_db))