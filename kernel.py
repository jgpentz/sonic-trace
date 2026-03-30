import subprocess
from utils import normalize_prefix

def get_kernel_routes():
    """
    Get the routes from the kernel.
    """
    try:
        cmd = [
            "docker", "exec", "clab-spine-leaf-leaf-1", "ip", "route"
        ]
        output = subprocess.run(cmd, capture_output=True, text=True)

        routes = {}
        for line in output.stdout.strip().split("\n"):
            parts = line.split()
            prefix = parts[0]
            route = {
                "raw": line, 
                "protocol": None,
                "nexthop": None,
                "interface": None
            }

            if "proto" in parts:
                route["protocol"] = parts[parts.index("proto") + 1]

            if "via" in parts:
                route["nexthop"] = parts[parts.index("via") + 1]

            if "dev" in parts:
                route["interface"] = parts[parts.index("dev") + 1]

            routes[normalize_prefix(prefix)] = route

        return routes
    except subprocess.CalledProcessError as e:
        print(f"Error getting kernel routes: {e}")

if __name__ == "__main__":
    routes = get_kernel_routes()
    print(routes)