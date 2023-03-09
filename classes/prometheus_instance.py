import requests


class PrometheusInstance:
    def __init__(self, url):
        self.url = url

    # Function that returns the number of cpus of the node
    def get_node_cpu_available(self):
        request = requests.get(self.url, params={"query": "node:node_num_cpu:sum"})
        data = request.json()['data']['result'][0]['value']
        return float(data[1])

    # Function that returns the quantity (bytes) of memory available on the node
    def get_node_memory_available(self):
        request = requests.get(self.url, params={"query": "node_memory_MemAvailable_bytes"})
        data = request.json()['data']['result'][0]['value']
        return float(data[1])

    # Function that returns the quantity (bytes) of storage available on the node
    def get_node_storage_available(self):
        request = requests.get(self.url, params={"query": "node_filesystem_avail_bytes"})
        data = request.json()['data']['result'][0]['value']
        return float(data[1])