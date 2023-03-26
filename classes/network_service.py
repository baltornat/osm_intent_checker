import json
import os
import string
import random
import requests
import yaml

from exceptions.api_exceptions import ApiExceptions
from utils.file_utils import create_zip_file


class NetworkService:
    def __init__(self, vnfd, nsd, ns_name):
        self.vnfd = vnfd
        self.nsd = nsd
        self.ns_name = ns_name
        self.ns_id = None

    def upload_nfpkg(self, auth):
        try:
            print(f"Uploading CNF package of NS {self.ns_name}")
            if auth.is_token_valid():
                zip_name = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
                print(f"Generating temporary file {zip_name}.zip to be uploaded to OSM")
                if not os.path.exists('tmp'):
                    os.makedirs('tmp')
                create_zip_file(self.vnfd.package_path, f"{zip_name}.zip", output_dir='tmp')
                headers = {
                    'Authorization': f"Bearer {auth.bearer_token}",
                    'Content-Type': 'application/zip'
                }
                with open(f"tmp/{zip_name}.zip", 'rb') as file:
                    response = requests.post(auth.nbi_hostname + 'vnfpkgm/v1/vnf_packages_content/', headers=headers,
                                             data=file)
                    parsed_data = yaml.safe_load(response.content.decode('utf-8'))
                    if all(key in parsed_data for key in ['code', 'detail', 'status']):
                        os.remove(f"tmp/{zip_name}.zip")
                        raise ApiExceptions.CnfPackageUploadException(parsed_data['code'], parsed_data['detail'],
                                                                      parsed_data['status'])
                    else:
                        os.remove(f"tmp/{zip_name}.zip")
                        self.vnfd.package_id = parsed_data['id']
            else:
                raise ApiExceptions.TokenExpiredException()
        except yaml.YAMLError as e:
            print(f"Caught YAMLError exception: {e}")
        except json.JSONDecodeError as e:
            print(f"Caught JSONDecodeError exception: {e}")
        except FileNotFoundError as e:
            print(f"Caught FileNotFound exception: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Caught RequestException exception: {e}")

    def upload_nspkg(self, auth):
        try:
            print(f"Uploading NS package of NS {self.ns_name}")
            if auth.is_token_valid():
                zip_name = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
                print(f"Generating temporary file {zip_name}.zip to be uploaded to OSM")
                if not os.path.exists('tmp'):
                    os.makedirs('tmp')
                create_zip_file(self.nsd.package_path, f"{zip_name}.zip", output_dir='tmp')
                headers = {
                    'Authorization': f"Bearer {auth.bearer_token}",
                    'Content-Type': 'application/zip'
                }
                with open(f"tmp/{zip_name}.zip", 'rb') as file:
                    response = requests.post(auth.nbi_hostname + 'nsd/v1/ns_descriptors_content/', headers=headers,
                                             data=file)
                    parsed_data = yaml.safe_load(response.content.decode('utf-8'))
                    if all(key in parsed_data for key in ['code', 'detail', 'status']):
                        os.remove(f"tmp/{zip_name}.zip")
                        raise ApiExceptions.NsPackageUploadException(parsed_data['code'], parsed_data['detail'],
                                                                     parsed_data['status'])
                    else:
                        os.remove(f"tmp/{zip_name}.zip")
                        self.nsd.package_id = parsed_data['id']
            else:
                raise ApiExceptions.TokenExpiredException()
        except yaml.YAMLError as e:
            print(f"Caught YAMLError exception: {e}")
        except json.JSONDecodeError as e:
            print(f"Caught JSONDecodeError exception: {e}")
        except FileNotFoundError as e:
            print("Caught FileNotFound exception: {}".format(e))
        except requests.exceptions.RequestException as e:
            print(f"Caught RequestException exception: {e}")

    def deploy_ns(self, auth, vim_account):
        try:
            print(f"Deploying NS {self.ns_name}")
            if auth.is_token_valid():
                headers = {
                    'Authorization': f"Bearer {auth.bearer_token}",
                    'Content-Type': 'application/json'
                }
                data = {
                    'nsName': self.ns_name,
                    'nsdId': self.nsd.package_id,
                    'vimAccountId': auth.get_vim_id(vim_account)
                }
                response = requests.post(auth.nbi_hostname + 'nslcm/v1/ns_instances_content/', data=json.dumps(data),
                                         headers=headers)
                parsed_data = yaml.safe_load(response.content.decode('utf-8'))
                if all(key in parsed_data for key in ['code', 'detail', 'status']):
                    raise ApiExceptions.DeploymentException(parsed_data['code'], parsed_data['detail'],
                                                            parsed_data['status'])
                else:
                    self.ns_id = parsed_data['id']
            else:
                raise ApiExceptions.TokenExpiredException()
        except yaml.YAMLError as e:
            print(f"Caught YAMLError exception: {e}")
        except json.JSONDecodeError as e:
            print(f"Caught JSONDecodeError exception: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Caught RequestException exception: {e}")
        except ApiExceptions.VimNotFound as e:
            print(f"Caught VimNotFound exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")
        except ApiExceptions.TokenExpiredException as e:
            print(f"Caught TokenExpiredException exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")
