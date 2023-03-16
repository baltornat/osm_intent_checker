import json
import os

from classes.deployment import Deployment
from classes.helm_chart import HelmChart
from classes.juju_bundle import JujuBundle
from classes.network_service import NetworkService
from classes.nsd import Nsd
from classes.prometheus_instance import PrometheusInstance
from classes.vnfd import Vnfd
from exceptions.service_exceptions import NotSol006, PackageNotValid, KduNotFound
from utils.file_utils import print_results

prometheus_url = 'http://10.152.183.160:9090/api/v1/query'


def main():
    print("Testing path to deployments.json: network_services_test/deployments.json\n")
    vnfd = None
    nsd = None
    try:
        path = input("Enter the path to deployment.json file: ")
        complete_deployment = Deployment()
        with open(path, 'r') as file:
            deployments = json.load(file)
            for ns_name, ns_data in deployments.items():
                vnfd_path = os.path.dirname(path) + "/" + ns_name + "/" + ns_data['cnf']['base_directory'] + "/" + ns_data['cnf']['vnfd']
                nsd_path = os.path.dirname(path) + "/" + ns_name + "/" + ns_data['ns']['base_directory'] + "/" + ns_data['ns']['nsd']
                vnfd = Vnfd(vnfd_path)
                print("\nValidating VNFD {} for NS {}...".format(ns_data['cnf']['vnfd'], ns_name))
                vnfd.validate_package()
                nsd = Nsd(nsd_path)
                print("Validating NSD {} for NS {}...".format(ns_data['ns']['nsd'], ns_name))
                nsd.validate_package()
                name, chart_or_bundle = vnfd.get_chart_or_bundle()
                if chart_or_bundle == 'helm-chart':
                    helm_chart = HelmChart(name)
                    helm_chart.get_requirements_helm()
                    print("\nResources requested by the network service:", json.dumps(helm_chart.total_resources, indent=4))
                elif chart_or_bundle == 'juju-bundle':
                    juju_bundle = JujuBundle(name)
                    print('To be implemented')
                for key, value in helm_chart.total_resources.items():
                    complete_deployment.deployment_resources[key] += value
                # Create the instance for the network service
                vim_account = ns_data['ns']['vim_account']
                network_service = NetworkService(vnfd, nsd, ns_name, vim_account)
                complete_deployment.add_service(network_service)
            prometheus = PrometheusInstance(prometheus_url)
            print_results(complete_deployment.deployment_resources, prometheus)
            # Deployment
            # What happens if the outcome is bad?
            complete_deployment.deploy_services()
    except NotSol006 as e:
        print("Caught NotSol006 code {}: {}".format(e.code, e))
        if vnfd:
            vnfd.translate_package()
        if nsd:
            nsd.translate_package()
    except PackageNotValid as e:
        print("Caught PackageNotValid code {}: {}".format(e.code, e))
    except KduNotFound as e:
        print("Caught KduNotFound code {}: {}".format(e.code, e))
    except FileNotFoundError as e:
        print("Caught FileNotFound: {}".format(e))
    except json.JSONDecodeError as e:
        print("Caught JSONDecodeError: {}".format(e))


if __name__ == "__main__":
    main()
