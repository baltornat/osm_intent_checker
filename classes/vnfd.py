import os
import subprocess

import yaml

from exceptions.service_exceptions import NotSol006, PackageNotValid, KduNotFound


class Vnfd:
    def __init__(self, path):
        self.path = path
        self.package_path = os.path.dirname(path)
        self.package_id = None

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
            print('Caught CalledProcessError exception: ', e)

    def translate_package(self):
        try:
            print('Translating the package to SOL006')
            output = subprocess.check_output(['osm', 'package-translate', '--recursive', self.package_path],
                                             text=True)
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError exception: ', e)

    # Function that returns the Helm Chart or the Juju Bundle name inside the KDU (Kubernetes Deployment Unit)
    def get_chart_or_bundle(self):
        try:
            with open(self.path, 'r') as vnfd:
                data = yaml.safe_load(vnfd)
                if 'kdu' in data['vnfd']:
                    if 'helm-chart' in data['vnfd']['kdu'][0]:
                        name = data['vnfd']['kdu'][0]['helm-chart']
                        print("Found helm-chart {}".format(name))
                        return name, 'helm-chart'
                    elif 'juju-bundle' in data['vnfd']['kdu'][0]:
                        name = data['vnfd']['kdu'][0]['juju-bundle']
                        print("Found juju-bundle {}".format(name))
                        return name, 'juju-bundle'
                else:
                    # KDU not found in YAML
                    raise KduNotFound('KDU tag not found inside given YAML')
        except FileNotFoundError as e:
            print('Caught FileNotFoundError exception: ', e)
        except yaml.YAMLError as e:
            print('Caught YAMLError exception: ', e)
