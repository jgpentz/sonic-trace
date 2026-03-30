import subprocess
def get_apply_db_routes():
    """
    Get the routes from the apply database.
    """
    try:
        result = subprocess.run(
            ["docker", "exec", "clab-spine-leaf-leaf-1", "redis-cli", "-n", "0", "KEYS", "ROUTE_TABLE:*"],
            capture_output=True,
            text=True
        )

        keys = result.stdout.strip().split("\n")

        routes = {}

        for key in keys:
            prefix = key.replace("ROUTE_TABLE:", "")

            data = subprocess.run(
                ["docker", "exec", "database", "redis-cli", "-n", "0", "HGETALL", key],
                capture_output=True,
                text=True
            )

            routes[prefix] = data.stdout

        return routes
    except subprocess.CalledProcessError as e:
        print(f"Error getting apply database routes: {e}")
        return None

if __name__ == "__main__":
    routes = get_apply_db_routes()
    print(routes)