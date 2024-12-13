import requests
import json

# Define constants
BASE_URL = "http://localhost:2525/webhooks"
AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJ3ZWJob29rIiwiZGVtbyJdLCJpYXQiOjE3MzQwNjk0NzMsImV4cCI6MTczNDA3MDA3MywiYXVkIjpbIm9wZW5jcnZzOmF1dGgtdXNlciIsIm9wZW5jcnZzOnVzZXItbWdudC11c2VyIiwib3BlbmNydnM6aGVhcnRoLXVzZXIiLCJvcGVuY3J2czpnYXRld2F5LXVzZXIiLCJvcGVuY3J2czpub3RpZmljYXRpb24tdXNlciIsIm9wZW5jcnZzOndvcmtmbG93LXVzZXIiLCJvcGVuY3J2czpzZWFyY2gtdXNlciIsIm9wZW5jcnZzOm1ldHJpY3MtdXNlciIsIm9wZW5jcnZzOmNvdW50cnljb25maWctdXNlciIsIm9wZW5jcnZzOndlYmhvb2tzLXVzZXIiLCJvcGVuY3J2czpjb25maWctdXNlciIsIm9wZW5jcnZzOmRvY3VtZW50cy11c2VyIl0sImlzcyI6Im9wZW5jcnZzOmF1dGgtc2VydmljZSIsInN1YiI6IjY3NDViZDM0Yzc2MzkwODFkNThmNGI3NiJ9.Knkb2NYoIKwZ61-70LaIxEaegVes4Gz7vIFIitt7pTtXCLtFPk0OBo8PhspsDzqX6JZ4ghEl55tooGB0zcGEQ0hmAm1JZL7YtIX0IqcMcNwhvNyfBNY2AFdJTfKofDEbHT2kCxyrwCU_qS9e_aQZ6iSY7_iJDG_NLDNDZiNvEFv_vn9jLig3UitAjPTBk9eLzbESk7HG356bcse9ZZIqgV7vSJOY3UAzY7H6elvw1UAn2Zro7OjvMeunvMnX2o9iA8IoQofb5J8AeglPuyMLYtpEJmR-32QcxLXGAwi6DQP6Mttcsnf7UXUETe5tNv44Hz64Wp5hLp7Hbvar_ssUAQ"  # Replace with your actual token
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

