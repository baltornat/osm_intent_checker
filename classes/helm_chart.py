import subprocess
import yaml
from utils.file_utils import find_nested_tags, convert


class HelmChart:
    def __init__(self, name):
        self.name = name

    # Function that returns 2 lists. The first contains cpu and memory requirements of the chart and the second contains
    # storage requirements of the chart
    def get_requirements_helm(self):
        output = subprocess.check_output(['helm', 'show', 'values', self.name], text=True)
        data = yaml.safe_load(output)
        resources = find_nested_tags(data, 'resources')
        persistence = find_nested_tags(data, 'persistence')
        return resources, persistence

    # Function that returns the sum of values with the same key in a dictionary to calculate total requests/limits
    # requirements for cpu and memory
    # resources: list
    # component: 'cpu'/'memory'
    # choice: 'requests'/'limits'
    def sum_resources(self, resources, component, choice):
        return sum([convert(r[choice][component]) for r in resources if choice in r and component in r[choice]])

    # Nested version of the function above to calculate total storage size requested
    # presistence: list
    def sum_persistence(self, persistence):
        return sum([convert(size) for item in persistence for size in find_nested_tags(item, 'size')])
