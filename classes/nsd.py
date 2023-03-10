import os
import subprocess
import yaml

from exceptions.service_exceptions import NotSol006, PackageNotValid


class Nsd:
    def __init__(self, path):
        self.path = path
        self.package_path = os.path.dirname(path)

    # Function that validates the package
    def validate_package(self):
        try:
            output = subprocess.check_output(['osm', 'package-validate', '--recursive', self.package_path],
                                             text=True)
            # Cannot handle errors in another way. If the output contains "ok" the package is valid
            if 'ok' in output.lower():
                print(output)
            elif 'not sol006 format' in output.lower():
                # Does the package need to be translated to SOL006?
                raise NotSol006('Package is not a SOL006 package')
            else:
                raise PackageNotValid('Package is not valid')
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError: ', e)

    def translate_package(self):
        try:
            print('Translating the package to SOL006')
            output = subprocess.check_output(['osm', 'package-translate', '--recursive', self.package_path],
                                             text=True)
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError: ', e)

    def get_nsd_name(self):
        try:
            with open(self.path, 'r') as nsd:
                data = yaml.safe_load(nsd)
                return data['nsd']['nsd'][0]['name']
        except FileNotFoundError as e:
            print('Caught FileNotFoundError: ', e)
        except yaml.YAMLError as e:
            print('Caught YAMLError: ', e)
