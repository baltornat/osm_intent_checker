import re


# Function that converts values with suffixes to the corresponding value in bytes
def convert(string):
    suffixes = {
        'Ki': 2 ** 10,
        'Mi': 2 ** 20,
        'Gi': 2 ** 30,
        'Ti': 2 ** 40,
        'Pi': 2 ** 50,
        'Ei': 2 ** 60,
        'm': 10 ** -3,
        'k': 10 ** 3,
        'M': 10 ** 6,
        'G': 10 ** 9,
        'T': 10 ** 12,
        'P': 10 ** 15,
        'E': 10 ** 18
    }
    # Extract the numerical value and suffix from the input string
    match = re.match(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]*)', string)
    value = float(match.group(1))
    suffix = match.group(2)
    # Convert the numerical value
    if suffix in suffixes:
        multiplier = suffixes[suffix]
        new_value = float(value * multiplier)
    else:
        new_value = float(value)
    return new_value


def check_results(total_deployment, prometheus):
    prom_cpu_available = prometheus.get_node_cpu_available()
    prom_memory_available = prometheus.get_node_memory_available()
    prom_storage_available = prometheus.get_node_storage_available()
    print("\nTotal resources requested by all network services")
    print("(Outcome)\t(Metric)\t\t\t(Chart/Node)")
    if total_deployment.deployment_resources["cpu_requests"] <= prom_cpu_available:
        total_deployment.check["cpu_requests"] = True
        print("[OK]\t\tTotal cpu requested:\t\t{}/{} cpu unit(s)".format(total_deployment.deployment_resources["cpu_requests"],
                                                                         prom_cpu_available))
    else:
        print("[X]\t\tTotal cpu requested:\t\t{}/{} cpu unit(s)".format(total_deployment.deployment_resources["cpu_requests"],
                                                                        prom_cpu_available))
    if total_deployment.deployment_resources["memory_requests"] <= prom_memory_available:
        total_deployment.check["memory_requests"] = True
        print("[OK]\t\tTotal memory requested:\t\t{}/{} bytes".format(total_deployment.deployment_resources["memory_requests"],
                                                                      prom_memory_available))
    else:
        print("[X]\t\tTotal memory requested:\t\t{}/{} bytes".format(total_deployment.deployment_resources["memory_requests"],
                                                                     prom_memory_available))
    if total_deployment.deployment_resources["storage"] <= prom_storage_available:
        total_deployment.check["storage"] = True
        print(
            "[OK]\t\tTotal storage requested:\t{}/{} bytes".format(total_deployment.deployment_resources["storage"], prom_storage_available))
    else:
        print("[X]\t\tTotal storage requested:\t{}/{} bytes".format(total_deployment.deployment_resources["storage"], prom_storage_available))
    if total_deployment.deployment_resources["cpu_limits"] <= prom_cpu_available:
        total_deployment.check["cpu_limits"] = True
        print("[OK]\t\tTotal cpu limit:\t\t{}/{} cpu unit(s)".format(total_deployment.deployment_resources["cpu_limits"], prom_cpu_available))
    else:
        print("[X]\t\tTotal cpu limit:\t\t{}/{} cpu unit(s)".format(total_deployment.deployment_resources["cpu_limits"], prom_cpu_available))
    if total_deployment.deployment_resources["memory_limits"] <= prom_memory_available:
        total_deployment.check["memory_limits"] = True
        print("[OK]\t\tTotal memory limit:\t\t{}/{} bytes".format(total_deployment.deployment_resources["memory_limits"],
                                                                  prom_memory_available))
    else:
        print(
            "[X]\t\tTotal memory limit:\t\t{}/{} bytes".format(total_deployment.deployment_resources["memory_limits"], prom_memory_available))
    if total_deployment.deployment_resources["sizeLimit"] <= prom_storage_available:
        total_deployment.check["sizeLimit"] = True
        print(
            "[OK]\t\tTotal storage limit:\t\t{}/{} bytes".format(total_deployment.deployment_resources["sizeLimit"], prom_storage_available))
    else:
        print("[X]\t\tTotal storage limit:\t\t{}/{} bytes".format(total_deployment.deployment_resources["sizeLimit"], prom_storage_available))
