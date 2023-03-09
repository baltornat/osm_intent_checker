import subprocess
import os
import yaml


class Vnfd:
    def __init__(self, path):
        self.path = path
        self.package_path = os.path.dirname(path)

    # Function that validates the package
    def validate(self):
        output = subprocess.check_output(['osm', 'package-validate', '--recursive', '--old', self.package_path], text=True)
        # Check on the correctness
        print(output)

    # Function that translates the package from SOL-005 to SOL-006
    def translate(self):
        return

    # Function that returns the Helm Chart name inside the kdu (Kubernetes Deployment Unit)
    def get_helm_chart(self):
        with open(self.path, "r") as vnfd:
            data = yaml.safe_load(vnfd)
            helm_chart = data['vnfd']['kdu'][0]['helm-chart']
        return helm_chart

    # Function that returns the Juju Charm name inside the kdu (Kubernetes Deployment Unit)
    def get_juju_charm(self):
        return