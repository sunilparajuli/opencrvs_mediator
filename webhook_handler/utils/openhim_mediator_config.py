import requests
from django.conf import settings
import json
from uptime import uptime


def register_mediator():
    config = settings.OPENHIM_CONFIG
    auth = (config["username"], config["password"])
    headers = {"Content-Type": "application/json"}

    # Define mediator registration details
    mediator_definition = {
        "urn": f"urn:mediator:{config['mediator_name']}",
        "version": "1.0.0",
        "name": config["mediator_name"],
        "description": "openIMIS-openCRVS-Mediator",
        "defaultChannelConfig": [
            {
                "name": "Default Channel",
                "urlPattern": "^/api/crvs/patient/$",
                "routes": [
                    {
                        "name": "django fetch openCrvs",
                        "host": config["host"],
                        "path": "/api/crvs/patient/$",
                        "port": config["port"],
                        "primary": True,
                        "methods": ["GET"],
                        "type": "http",
                    }
                ],
            }
        ],
        # Ensure at least one endpoint is defined
        "endpoints": [
            {
                "name": "Bootstrap Scaffold Mediator Endpoint",
                "host": config["host"],
                "path": "/api/crvs/opencrvs/",
                "port": config["port"],
                "primary": False,
                "type": "http",
                "methods": ["POST"],
            },
        ],
        "configDefs": [
            {
                "param": "target-scheme",
                "displayName": "Target Server Scheme",
                "type": "option",
                "values": ["http", "https"],
            },
            {
                "param": "target-host",
                "displayName": "Target Server Host",
                "type": "string",
            },
            {
                "param": "target-port",
                "displayName": "Target Server Port",
                "type": "number",
            },
            {
                "param": "mappings-datasets",
                "displayName": "Data Set Mappings",
                "type": "map",
            },
            {
                "param": "mappings-dataelements",
                "displayName": "Data Element Mappings",
                "type": "map",
            },
            {
                "param": "mappings-orgunits",
                "displayName": "OrgUnit Mappings",
                "type": "map",
            },
            {
                "param": "mappings-programs",
                "displayName": "Program Mappings",
                "type": "map",
            },
        ],
        "config": {
            "target-scheme": "http",
            "target-host": "localhost",
            "target-port": 8080,
        },
    }

    config = settings.OPENHIM_CONFIG
    response = requests.post(
        f"{config['openhim_core_url']}/mediators",
        auth=auth,
        headers=headers,
        data=json.dumps(mediator_definition),
        verify=config.get("verify_ssl", True),  # Use SSL config setting
    )

    # Check response and print for debugging
    if response.status_code in [200, 201]:  # Success codes
        print("Mediator registered successfully with OpenHIM!")
    else:
        print("Failed to register mediator:", response.status_code, response.text)


def send_heartbeat():
    """Sends a heartbeat signal to OpenHIM."""
    config = settings.OPENHIM_CONFIG
    auth = (config["username"], config["password"])
    headers = {"Content-Type": "application/json"}
    body = {"uptime": uptime()}
    urn = f"urn:mediator:{config['mediator_name']}"
    mediators_url = f"{config['url']}/mediators/{urn}/heartbeat"
    print("mediator_url", mediators_url)
    response = requests.post(
        url=mediators_url,
        auth=auth,
        headers=headers,
        json=body,
        verify=False,  # config.get('verify_ssl', True)
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            f"Heartbeat unsuccessful, received status code: {response.status_code}"
        )
    print("Heartbeat sent successfully!")
