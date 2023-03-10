from classes.helm_chart import HelmChart
from classes.juju_bundle import JujuBundle
from classes.network_service import NetworkService
from classes.nsd import Nsd
from classes.prometheus_instance import PrometheusInstance
from classes.vnfd import Vnfd
from exceptions.service_exceptions import NotSol006, PackageNotValid, KduNotFound
from utils.file_utils import print_results_charts

prometheus_url = 'http://10.152.183.160:9090/api/v1/query'


def main():
    print("Test VNFDs using Helm Chart:\n"
          "network_services_test/ns1/ns1_cnf/ns1_vnfd.yaml\n"
          "network_services_test/ns2/ns2_cnf/ns2_vnfd.yaml\n"
          "network_services_test/ns3/ns3_cnf/ns3_vnfd.yaml\n")
    print("Test NSDs using Helm Chart:\n"
          "network_services_test/ns1/ns1_ns/ns1_nsd.yaml\n"
          "network_services_test/ns2/ns2_ns/ns2_nsd.yaml\n"
          "network_services_test/ns3/ns3_ns/ns3_nsd.yaml\n")
    vnfd = None
    nsd = None
    try:
        vnfd = Vnfd(input('Enter the path to the VNFD file: '))
        vnfd.validate_package()
        nsd = Nsd(input('Enter the path to the NSD file: '))
        nsd.validate_package()
        name, chart_or_bundle = vnfd.get_chart_or_bundle()
        if chart_or_bundle == 'helm-chart':
            # Helm Chart
            helm_chart = HelmChart(name)
            chart_resources, chart_persistence = helm_chart.get_requirements_helm()
            # Prometheus
            prometheus = PrometheusInstance(prometheus_url)
            # Output
            print_results_charts(helm_chart, chart_resources, chart_persistence, prometheus)
            # Deployment
            # What happens if the outcome is bad?
            ns_name = input('Enter the name of the Network Service: ')
            vim_account = input('Enter the VIM account: ')
            network_service = NetworkService(vnfd, nsd, ns_name, vim_account)
            network_service.upload_nfpkg()
            network_service.upload_nspkg()
            network_service.deploy_ns()
        elif chart_or_bundle == 'juju-bundle':
            juju_bundle = JujuBundle(name)
            print('To be implemented')
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


if __name__ == "__main__":
    main()
