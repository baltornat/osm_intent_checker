class Deployment:
    def __init__(self):
        self.ns_list = {}
        self.deployment_resources = {
            "cpu_requests": 0,
            "memory_requests": 0,
            "cpu_limits": 0,
            "memory_limits": 0,
            "storage": 0,
            "sizeLimit": 0
        }

    def add_service(self, network_service):
        self.ns_list[network_service.ns_name] = network_service

    def deploy_services(self):
        for ns_name, network_service in self.ns_list.items():
            print("\nDeploying {} network service...".format(ns_name))
            network_service.upload_nfpkg()
            network_service.upload_nspkg()
            network_service.deploy_ns()
