import subprocess
import yaml

from utils.file_utils import convert


class HelmChart:
    def __init__(self, name):
        self.name = name
        self.total_resources = {
            "cpu_requests": 0,
            "memory_requests": 0,
            "cpu_limits": 0,
            "memory_limits": 0,
            "storage": 0,
            "sizeLimit": 0
        }

    # Function that returns 2 lists. The first contains cpu and memory requirements of the chart and the second contains
    # storage requirements of the chart
    def get_requirements_helm(self):
        try:
            output = subprocess.check_output(["helm", "template", self.name], text=True)
            documents = output.split('---\n')
            for doc in documents:
                parsed_doc = yaml.safe_load(doc)
                if parsed_doc is not None and "kind" in parsed_doc and parsed_doc["kind"] in ["StatefulSet", "Deployment", "PersistentVolumeClaim"]:
                    replicas = parsed_doc.get("spec", {}).get("replicas")
                    if replicas is None:
                        replicas = 1
                    # Extract cpu/memory requests and cpu/memory limits if kind == "StatefulSet" or "Deployment"
                    containers = parsed_doc.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
                    for container in containers:
                        resources = container.get("resources", {})
                        requests = resources.get("requests", {})
                        limits = resources.get("limits", {})
                        if not requests:
                            print("WARNING: Requests not defined for CPU/Memory in {} - {}".format(parsed_doc["kind"], parsed_doc["metadata"]["name"]))
                        if not limits:
                            print("WARNING: Limits not defined for CPU/Memory in {} - {}".format(parsed_doc["kind"], parsed_doc["metadata"]["name"]))
                        for key in self.total_resources.keys():
                            if "cpu" in key:
                                if key.endswith("_requests") and "cpu" in requests:
                                    self.total_resources[key] += convert(requests["cpu"]) * int(replicas)
                                elif key.endswith("_limits") and "cpu" in limits:
                                    self.total_resources[key] += convert(limits["cpu"]) * int(replicas)
                            elif "memory" in key:
                                if key.endswith("_requests") and "memory" in requests:
                                    self.total_resources[key] += convert(requests["memory"]) * int(replicas)
                                elif key.endswith("_limits") and "memory" in limits:
                                    self.total_resources[key] += convert(limits["memory"]) * int(replicas)
                    # Extract sizeLimit if kind == "Deployment"
                    volumes = parsed_doc.get("spec", {}).get("template", {}).get("spec", {}).get("volumes", [])
                    if volumes is not None:
                        for volume in volumes:
                            sizes = volume.get("emptyDir", {})
                            if not sizes:
                                print("WARNING: Sizes not defined for Storage in {} - {}".format(parsed_doc["kind"], parsed_doc["metadata"]["name"]))
                            for key in self.total_resources.keys():
                                if key == "sizeLimit" and key in sizes:
                                    self.total_resources[key] += convert(sizes[key]) * int(replicas)
                    # Extract storage requests if kind == "StatefulSet"
                    if parsed_doc["kind"] == "StatefulSet":
                        volume_claim_template = parsed_doc.get("spec", {}).get("volumeClaimTemplates", [])
                        for volume_claim in volume_claim_template:
                            resources = volume_claim.get("spec", {}).get("resources", {})
                            requests = resources.get("requests", {})
                            if not requests:
                                print("WARNING: Requests not defined for Storage in {} - {}".format(parsed_doc["kind"], parsed_doc["metadata"]["name"]))
                            for key in self.total_resources.keys():
                                if key == "storage" and key in requests:
                                    self.total_resources[key] += convert(requests[key]) * int(replicas)
                    # Extract storage requests if kind == "PersistentVolumeClaim"
                    elif parsed_doc["kind"] == "PersistentVolumeClaim":
                        requests = parsed_doc["spec"]["resources"]["requests"]
                        if not requests:
                            print("WARNING: Requests not defined for Storage in {} - {}".format(parsed_doc["kind"], parsed_doc["metadata"]["name"]))
                        for key in self.total_resources.keys():
                            if key == "storage" and key in requests:
                                self.total_resources[key] += convert(requests[key]) * int(replicas)
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError: ', e)
        except yaml.YAMLError as e:
            print('Caught YAMLError: ', e)
