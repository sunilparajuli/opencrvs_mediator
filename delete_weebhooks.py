import requests
import json

# Define constants
BASE_URL = "http://localhost:2525/webhooks"
AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJ3ZWJob29rIiwiZGVtbyJdLCJpYXQiOjE3MzQwMjg4MjYsImV4cCI6MTczNDAyOTQyNiwiYXVkIjpbIm9wZW5jcnZzOmF1dGgtdXNlciIsIm9wZW5jcnZzOnVzZXItbWdudC11c2VyIiwib3BlbmNydnM6aGVhcnRoLXVzZXIiLCJvcGVuY3J2czpnYXRld2F5LXVzZXIiLCJvcGVuY3J2czpub3RpZmljYXRpb24tdXNlciIsIm9wZW5jcnZzOndvcmtmbG93LXVzZXIiLCJvcGVuY3J2czpzZWFyY2gtdXNlciIsIm9wZW5jcnZzOm1ldHJpY3MtdXNlciIsIm9wZW5jcnZzOmNvdW50cnljb25maWctdXNlciIsIm9wZW5jcnZzOndlYmhvb2tzLXVzZXIiLCJvcGVuY3J2czpjb25maWctdXNlciIsIm9wZW5jcnZzOmRvY3VtZW50cy11c2VyIl0sImlzcyI6Im9wZW5jcnZzOmF1dGgtc2VydmljZSIsInN1YiI6IjY3NDViZDM0Yzc2MzkwODFkNThmNGI3NiJ9.V-gbKOvA1jFlvMT0NotUFOs6VN4O4Q47fb_g0c7aalTkggT9evvbUjuKf8IOhP5EAuaZs6eCU5NTSQLkLn-0lMZd-1jdxzmmvlqb77lsqJtdxsrctTV3uw62dlTeX9844SvCUAee-8K9DaKA5-A5qaSMKDGFdfhYyo0JxuxzO2HZjcrgxQ_7EQqZ4GnYeIPJjacKWDRAyCO1KQOSJpc5ZsnP1kYRbol_Kmj_5if7cTk_Iu1Lp9dyL5oBB8OoWE-6Z4NpdbLKWzTZmX_0UXoF1zTmpNxoFlmekg5LLp6S94rSvPeyu7jgjSyW0YNmnuq0qCH5pzhucRFayfudvdN6Qg"  # Replace with your actual token
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}
HUB_PAYLOAD = {
    "hub": {
        "callback": "http://localhost:8000/api/webhooks/",
        "mode": "subscribe",
        "topic": "BIRTH_REGISTERED",
        "secret": "b15e2dab-6362-408b-b3b9-e8d76e77ac22"
    }
}

# Fetch all webhook entries
def get_webhook_entries():
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get("entries", [])
    else:
        print(f"Failed to fetch entries: {response.status_code}, {response.text}")
        return []

# Delete a specific webhook entry
def delete_webhook_entry(entry_id):
    url = f"{BASE_URL}/{entry_id}"
    response = requests.delete(url, headers=HEADERS, json=HUB_PAYLOAD)
    if response.status_code == 200:
        print(f"Successfully deleted webhook entry with id: {entry_id}")
    else:
        print(f"Failed to delete entry {entry_id}: {response.status_code}, {response.text}")

# Main script
if __name__ == "__main__":
    entries = get_webhook_entries()
    if not entries:
        print("No webhook entries to delete.")
    else:
        for entry in entries:
            delete_webhook_entry(entry["id"])

