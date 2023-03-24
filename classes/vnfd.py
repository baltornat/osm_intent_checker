import os
import yaml

from exceptions.service_exceptions import ServiceExceptions


class Vnfd:
    def __init__(self, path):
        self.path = path
        self.package_path = os.path.dirname(path)
        self.package_id = None

    # Function that returns the Helm Chart or the Juju Bundle name inside the KDU (Kubernetes Deployment Unit)
    def get_chart_or_bundle(self):
        try:
            with open(self.path, 'r') as vnfd:
                data = yaml.safe_load(vnfd)
                if 'kdu' in data['vnfd']:
                    if 'helm-chart' in data['vnfd']['kdu'][0]:
                        name = data['vnfd']['kdu'][0]['helm-chart']
                        print(f"\nFound helm-chart {name}\n")
                        return name, 'helm-chart'
                    elif 'juju-bundle' in data['vnfd']['kdu'][0]:
                        name = data['vnfd']['kdu'][0]['juju-bundle']
                        print("Found juju-bundle {}".format(name))
                        return name, 'juju-bundle'
                else:
                    raise ServiceExceptions.KduNotFound()
        except FileNotFoundError as e:
            print('Caught FileNotFoundError exception: ', e)
        except yaml.YAMLError as e:
            print('Caught YAMLError exception: ', e)
