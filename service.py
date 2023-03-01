# Development VNFD path: test/test_vnf/test_vnfd.yaml
# Development Prometheus url: http://127.0.0.1:30000/api/v1/query
# Port forwaring is necessary: kubectl -n monitoring port-forward services/prometheus-operated 38173:9090

import yaml
import requests
import subprocess
import os

PROMETHEUS_URL = "http://127.0.0.1:30000/api/v1/query"

# Check if the package is valid
vnfdPath = input("Enter the path to the VNFD file: ")
# Retrieve VNF package path
vnfPackagePath = os.path.dirname(vnfdPath)
print("Checking the validity of the VNF package...")
bashCommand = "osm package-validate --recursive --old {}".format(vnfPackagePath)
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
try:
    output_str = output.decode('utf-8')
    print('=== OUTPUT ===')
    print(output_str)
except AttributeError:
    output_str = ''
try:
    error_str = error.decode('utf-8')
    print('=== ERROR ===')
    print(error_str)
except AttributeError:
    error_str = ''

# Open VNFD
with open(vnfdPath, "r") as vnfd:
    try:
        # Load data from vnfd
        data=yaml.safe_load(vnfd)
        # Read resources requirements of the Network Service
        print("Reading resources requirements from VNFD {}...".format(os.path.basename(vnfdPath)))
        virtualCpu = data['vnfd']['virtual-compute-desc'][0]['virtual-cpu']['num-virtual-cpu']
        virtualMemory = data['vnfd']['virtual-compute-desc'][0]['virtual-memory']['size'] * 1024 * 1024
        storage = data['vnfd']['virtual-storage-desc'][0]['size-of-storage'] * 1024 * 1024 * 1024
        # Read metrics from Prometheus
        # Prometheus Cpu available
        request = requests.get(PROMETHEUS_URL, params={"query": "node:node_num_cpu:sum"})
        data = request.json()['data']['result'][0]['value']
        promCpuAvailable = data[1]
        #promCpuAvailable = data[1]
        # Prometheus Memory available
        request = requests.get(PROMETHEUS_URL, params={"query": "node_memory_MemAvailable_bytes"})
        data = request.json()['data']['result'][0]['value']
        promMemoryAvailable = data[1]
        # Prometheus Storage available
        request = requests.get(PROMETHEUS_URL, params={"query": "node_filesystem_avail_bytes"})
        data = request.json()['data']['result'][0]['value']
        promStorageAvailable = data[1]
        # Basic check
        if int(promCpuAvailable) >= virtualCpu:
            print("Cpu OK")
        else:
            print("Cpu NOT OK")
        if int(promMemoryAvailable) >= virtualMemory:
            print("Memory OK")
        else:
            print("Memory NOT OK")
        if int(promStorageAvailable) >= storage:
            print("Storage OK")
        else:
            print("Storage NOT OK")
        print("Trying deployment...")
        # DEPLOYMENT TO BE IMPLEMENTED
    except yaml.YAMLError as exception:
        print(exception) 
