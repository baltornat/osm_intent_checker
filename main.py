from classes.helm_chart import HelmChart
from classes.prometheus_instance import PrometheusInstance
from classes.vnfd import Vnfd

prometheus_url = "http://10.152.183.160:9090/api/v1/query"


def main():
    vnfd = Vnfd(input("Enter the path to the VNFD file: "))
    vnfd.validate()
    # Need translation?
    # vnfd.translate()
    # If the kdu uses helm then
    helm_chart = HelmChart(vnfd.get_helm_chart())
    chart_resources, chart_persistence = helm_chart.get_requirements_helm()
    requests_cpu_sum = helm_chart.sum_resources(chart_resources, 'cpu', 'requests')
    limits_cpu_sum = helm_chart.sum_resources(chart_resources, 'cpu', 'limits')
    requests_memory_sum = helm_chart.sum_resources(chart_resources, 'memory', 'requests')
    limits_memory_sum = helm_chart.sum_resources(chart_resources, 'memory', 'limits')
    storage_sum = helm_chart.sum_persistence(chart_persistence)

    prometheus = PrometheusInstance(prometheus_url)
    prom_cpu_available = prometheus.get_node_cpu_available()
    prom_memory_available = prometheus.get_node_memory_available()
    prom_storage_available = prometheus.get_node_storage_available()

    print("(Outcome)\t(Metric)\t\t\t(Chart/Node)")
    if requests_cpu_sum <= prom_cpu_available:
        print("[OK]\t\tTotal cpu requested:\t\t{}/{} cpu unit(s)".format(requests_cpu_sum, prom_cpu_available))
    else:
        print("[X]\t\tTotal cpu requested:\t\t{}/{} cpu unit(s)".format(requests_cpu_sum, prom_cpu_available))
    if requests_memory_sum <= prom_memory_available:
        print("[OK]\t\tTotal memory requested:\t\t{}/{} bytes".format(requests_memory_sum, prom_memory_available))
    else:
        print("[X]\t\tTotal memory requested:\t\t{}/{} bytes".format(requests_memory_sum, prom_memory_available))
    if storage_sum <= prom_storage_available:
        print("[OK]\t\tTotal storage requested:\t{}/{} bytes".format(storage_sum, prom_storage_available))
    else:
        print("[X]\t\tTotal storage requested:\t{}/{} bytes".format(storage_sum, prom_storage_available))
    if limits_cpu_sum <= prom_cpu_available:
        print("[OK]\t\tTotal cpu limit:\t\t{}/{} cpu unit(s)".format(limits_cpu_sum, prom_cpu_available))
    else:
        print("[X]\t\tTotal cpu limit:\t\t{}/{} cpu unit(s)".format(limits_cpu_sum, prom_cpu_available))
    if limits_memory_sum <= prom_memory_available:
        print("[OK]\t\tTotal memory limit:\t\t{}/{} bytes".format(limits_memory_sum, prom_memory_available))
    else:
        print("[X]\t\tTotal memory limit:\t\t{}/{} bytes".format(limits_memory_sum, prom_memory_available))


if __name__ == "__main__":
    main()
