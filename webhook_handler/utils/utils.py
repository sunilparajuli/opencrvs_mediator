import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress the InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)




import requests

def get_opencrvs_auth_token():
    url = 'http://localhost:4040/token'
    params = {
        'client_id': '91874daf-6389-4234-98a3-eabc83048764',
        'client_secret': '1ac4194a-4299-4f7b-bbd0-0c3401c4247b',
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(
        url,
        params=params,
        headers={'Content-Type': 'application/json'},
        verify=False  # Disable SSL verification
    )
    
    if response.status_code == 200:
        data = response.json()
        print(data.get('access_token'))
        return data.get('access_token')
    else:
        return None

