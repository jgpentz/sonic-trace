import sys
from frr import get_routes
from kernel import get_kernel_routes
from redis import get_apply_db_routes
from correlate import format_trace_report, trace_route

def main():
    frr = get_routes()
    kernel = get_kernel_routes()
    appl_db = get_apply_db_routes()

    prefix = sys.argv[1]

    result = trace_route(prefix, frr, kernel, appl_db)
    print(format_trace_report(prefix, result), end="")

if __name__ == "__main__":
    main()