import subprocess
import json

def get_routes():
    """
    Get the routes from the FRRouting router.
    """
    try:
        cmd = [
            "docker", "exec", "clab-spine-leaf-leaf-1", "vtysh", "-c", "show ip route json"
        ]
        output = subprocess.check_output(cmd)

        # Scrape the output for the routes
        json_output = json.loads(output.decode("utf-8"))
        routes = {}
        for prefix, entries in json_output.items():
            routes[prefix] = {
                "protocol": entries[0].get("protocol"),
                "nexthops": entries[0].get("nexthops", []),
            }
        return routes
    except subprocess.CalledProcessError as e:
        print(f"Error getting BGP routes: {e}")
        return None

if __name__ == "__main__":
    routes = get_routes()
    print(routes)