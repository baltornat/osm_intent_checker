import json
import os

from classes.auth import Auth
from classes.deployment import Deployment
from classes.helm_chart import HelmChart
from classes.juju_bundle import JujuBundle
from classes.network_service import NetworkService
from classes.nsd import Nsd
from classes.prometheus_instance import PrometheusInstance
from classes.vnfd import Vnfd
from exceptions.api_exceptions import ApiExceptions
from exceptions.service_exceptions import ServiceExceptions
from utils.file_utils import check_results

username = 'admin'
password = '42268d525e2fc9d5a3e599c8b4a524e1'

nbi_hostname = 'http://nbi.172.20.28.130.nip.io/osm/'
prometheus_url = 'http://10.152.183.160:9090/api/v1/query'

vim_account = "microstack-site"


def main():
    print("Testing path to deployments.json: network_services_test/deployments.json\n")
    try:
        path = input("Enter the path to deployment.json file: ")
        total_deployment = Deployment()
        with open(path, 'r') as file:
            deployments = json.load(file)
            auth = Auth(username, password, nbi_hostname)
            print(f"\nGenerating temporary Bearer Token for user {username}")
            auth.generate_bearer_token()
            for ns_name, ns_data in deployments.items():
                vnfd_path = os.path.dirname(path) + "/" + ns_name + "/" + ns_data['cnf']['base_directory'] + "/" + \
                            ns_data['cnf']['vnfd']
                nsd_path = os.path.dirname(path) + "/" + ns_name + "/" + ns_data['ns']['base_directory'] + "/" + \
                           ns_data['ns']['nsd']
                vnfd = Vnfd(vnfd_path)
                nsd = Nsd(nsd_path)
                name, chart_or_bundle = vnfd.get_chart_or_bundle()
                if chart_or_bundle == 'helm-chart':
                    helm_chart = HelmChart(name)
                    helm_chart.get_requirements_helm()
                    print("\nResources requested by the network service:",
                          json.dumps(helm_chart.total_resources, indent=4))
                elif chart_or_bundle == 'juju-bundle':
                    juju_bundle = JujuBundle(name)
                    print('To be implemented')
                # And for juju?
                for key, value in helm_chart.total_resources.items():
                    total_deployment.deployment_resources[key] += value
                # Create the instance for the network service
                network_service = NetworkService(vnfd, nsd, ns_name)
                total_deployment.add_service(network_service)
                print('\n---')
            prometheus = PrometheusInstance(prometheus_url)
            check_results(total_deployment, prometheus)
            # Deployment
            if total_deployment.is_possible():
                total_deployment.deploy_services(auth, vim_account)
            auth.logout()
    except ApiExceptions.CannotLogout as e:
        print(f"Caught CannotLogout exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")
    except ApiExceptions.TokenExpiredException as e:
        print(f"Caught TokenExpiredException exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")
    except ServiceExceptions.KduNotFound as e:
        print(f"Caught KduNotFound exception: Code: {e.code} - Detail: {e.detail} - Status: {e.status}")
    except FileNotFoundError as e:
        print(f"Caught FileNotFound exception: {e}")


if __name__ == "__main__":
    main()
