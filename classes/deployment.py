from exceptions.api_exceptions import ApiExceptions


class Deployment:
    def __init__(self):
        self.ns_list = {}
        self.deployment_resources = {
            "cpu_requests": 0,
            "memory_requests": 0,
            "storage": 0,
            "cpu_limits": 0,
            "memory_limits": 0,
            "sizeLimit": 0
        }
        self.check = {
            "cpu_requests": False,
            "memory_requests": False,
            "storage": False,
            "cpu_limits": False,
            "memory_limits": False,
            "sizeLimit": False
        }

    def add_service(self, network_service):
        self.ns_list[network_service.ns_name] = network_service

    def deploy_services(self, auth, vim_account):
        try:
            for ns_name, network_service in self.ns_list.items():
                network_service.upload_nfpkg(auth)
                network_service.upload_nspkg(auth)
                network_service.deploy_ns(auth, vim_account)
        except ApiExceptions.CnfPackageUploadException as e:
            print(f"Caught CnfPackageUploadException exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")
        except ApiExceptions.NsPackageUploadException as e:
            print(f"Caught NsPackageUploadException exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")
        except ApiExceptions.DeploymentException as e:
            print(f"Caught DeploymentException exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")
        except ApiExceptions.TokenExpiredException as e:
            print(f"Caught TokenExpiredException exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")

    def is_possible(self):
        print("\n")
        if self.check["cpu_requests"] and self.check["memory_requests"] and self.check["storage"]:
            if not self.check["cpu_limits"]:
                print("WARNING: Total cpu units limit is above total cpu units available")
            if not self.check["memory_limits"]:
                print("WARNING: Total memory limit is above total memory available")
            if not self.check["sizeLimit"]:
                print("WARNING: Storage size limit is above total storage available")
            return True
        else:
            if not self.check["cpu_requests"]:
                print(
                    "Deployment not possible because total cpu units requested are more than total cpu units available")
            if not self.check["memory_requests"]:
                print("Deployment not possible because total memory requested is more than total memory available")
            if not self.check["storage"]:
                print("Deployment not possible because total storage requested is more than total storage available")
            return False
