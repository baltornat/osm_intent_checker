import requests
import json
import yaml
import time

from exceptions.api_exceptions import ApiExceptions


class Auth:
    def __init__(self, username, password, nbi_hostname):
        self.username = username
        self.password = password
        self.nbi_hostname = nbi_hostname
        self.bearer_token = None
        self.issued_at = None
        self.expires = None

    def generate_bearer_token(self):
        try:
            headers = {
                'Content-type': 'application/json'
            }
            data = {
                'username': self.username,
                'password': self.password
            }
            response = requests.post(self.nbi_hostname + 'admin/v1/tokens/', data=json.dumps(data), headers=headers)
            parsed_data = yaml.safe_load(response.content.decode('utf-8'))
            self.bearer_token = parsed_data['id']
            self.issued_at = parsed_data['issued_at']
            self.expires = parsed_data['expires']
        except yaml.YAMLError as e:
            print(f"Caught YAMLError exception: {e}")
        except json.JSONDecodeError as e:
            print(f"Caught JSONDecodeError exception: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Caught RequestException exception: {e}")

    def is_token_valid(self):
        current_time = time.time()
        if self.issued_at <= current_time < self.expires:
            return True
        else:
            return False

    def logout(self):
        try:
            print(f"\nLogging out user {self.username}")
            if self.is_token_valid():
                headers = {
                    'Authorization': f"Bearer {self.bearer_token}"
                }
                response = requests.delete(self.nbi_hostname + 'admin/v1/tokens/', headers=headers)
                parsed_data = yaml.safe_load(response.content.decode('utf-8'))
                if 'deleted' in parsed_data.lower():
                    print('Bearer Token removed successfully')
                else:
                    raise ApiExceptions.CannotLogout()
            else:
                raise ApiExceptions.TokenExpiredException()
        except yaml.YAMLError as e:
            print(f"Caught YAMLError exception: {e}")
        except json.JSONDecodeError as e:
            print(f"Caught JSONDecodeError exception: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Caught RequestException exception: {e}")

    def get_vim_id(self, vim_account):
        try:
            if self.is_token_valid():
                headers = {
                    'Authorization': f"Bearer {self.bearer_token}"
                }
                response = requests.get(self.nbi_hostname + 'admin/v1/vim_accounts/', headers=headers)
                parsed_data = yaml.load(response.content.decode('utf-8'), Loader=yaml.SafeLoader)
                for element in parsed_data:
                    if '_id' in element:
                        if 'name' in element:
                            if element['name'] == vim_account:
                                return element['_id']
                            else:
                                raise ApiExceptions.VimNotFound()
            else:
                raise ApiExceptions.TokenExpiredException()
        except yaml.YAMLError as e:
            print(f"Caught YAMLError exception: {e}")
        except json.JSONDecodeError as e:
            print(f"Caught JSONDecodeError exception: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Caught RequestException exception: {e}")
