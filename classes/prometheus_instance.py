import requests


class PrometheusInstance:
    def __init__(self, url):
        self.url = url

    # Function that returns the number of cpus of the node
    def get_node_cpu_available(self):
        try:
            response = requests.get(self.url, params={"query": "node:node_num_cpu:sum"})
            # Raise an HTTPError if the status is not 200 OK
            response.raise_for_status()
            data = response.json()['data']['result'][0]['value']
            return float(data[1])
        except requests.exceptions.RequestException as e:
            print('Caught RequestException: ', e)

    # Function that returns the quantity (bytes) of memory available on the node
    def get_node_memory_available(self):
        try:
            response = requests.get(self.url, params={"query": "node_memory_MemAvailable_bytes"})
            # Raise an HTTPError if the status is not 200 OK
            response.raise_for_status()
            data = response.json()['data']['result'][0]['value']
            return float(data[1])
        except requests.exceptions.RequestException as e:
            print('Caught RequestException: ', e)

    # Function that returns the quantity (bytes) of storage available on the node
    def get_node_storage_available(self):
        try:
            response = requests.get(self.url, params={"query": "node_filesystem_avail_bytes"})
            # Raise an HTTPError if the status is not 200 OK
            response.raise_for_status()
            data = response.json()['data']['result'][0]['value']
            return float(data[1])
        except requests.exceptions.RequestException as e:
            print('Caught RequestException: ', e)