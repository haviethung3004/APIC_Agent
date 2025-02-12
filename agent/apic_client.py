import os
import requests
from urllib3 import disable_warnings
from dotenv import load_dotenv, find_dotenv
from typing import Dict

# load environment variables OPEN API KEY
load_dotenv(find_dotenv())

class APICClient:
    """Manange APIC Connect interactions with automate token refresh"""
    def __init__(self):
      self.base_url = os.getenv('APIC_BASE_URL')
      self.username = os.getenv('APIC_USERNAME')
      self.password = os.getenv('APIC_PASSWORD')
      self.api_key = os.getenv('ALIBABA_API_KEY')
      self.session = requests.Session()
      self.session.verify = False
      self.cookie = None
      disable_warnings()
      self._authenticate()

    def _authenticate(self) -> None:
      """Obtain and set access tolken"""
      auth_url = f"{self.base_url}/api/aaaLogin.json"
      # print(auth_url)
      auth_payload = {
        "aaaUser": {
          "attributes": {
            "name": self.username,
            "pwd": self.password
          }
        }
      }
      response = self.session.post(auth_url, json=auth_payload)
      response.raise_for_status()
      self.cookie = response.cookies


    def get_resource(self, url: str) -> dict:
        """Make API call to APIC"""
        if not self.cookie:
            self._authenticate()
            
        full_url = f"{self.base_url}{url}"
        print(full_url)
        try:
            response = requests.get(full_url, cookies=self.cookie, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            return print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            return print(f"Error occurred: {err}")
        
    def post_resouce(self, url: str, payload: Dict) -> dict:
        """Make API call to APIC"""
        if not self.cookie:
            self._authenticate()
        
        full_url = f"{self.base_url}{url}"
        try:
            response = requests.post(full_url, cookies=self.cookie, json=payload, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            return print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            return print(f"Error occurred: {err}")


# Usage example
if __name__ == "__main__":
    apic_client = APICClient()
    apic_client._authenticate()
    # url  = "api/node/mo/uni/tn-Migrate1.json?query-target=children&target-subtree-class=fvBD"
    url = "/api/class/fvCtx.json?query-target-filter=eq(fvCtx.name,\"VRF_700\")"
    tenants = apic_client.get_resource(url)
    print(tenants)

    

    