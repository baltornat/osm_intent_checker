import os
import yaml


class Nsd:
    def __init__(self, path):
        self.path = path
        self.package_path = os.path.dirname(path)
        self.package_id = None

    def get_nsd_name(self):
        try:
            with open(self.path, 'r') as nsd:
                data = yaml.safe_load(nsd)
                return data['nsd']['nsd'][0]['name']
        except FileNotFoundError as e:
            print('Caught FileNotFoundError exception: ', e)
        except yaml.YAMLError as e:
            print('Caught YAMLError exception: ', e)
