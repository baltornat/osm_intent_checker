# Development VNFD path: test/test_vnf/test_vnfd.yaml
# Development Prometheus url: http://127.0.0.1:30000/api/v1/query
# Port forwarding is necessary: kubectl -n monitoring port-forward services/prometheus-operated 30000:9090

import yaml
import requests
import subprocess
import os

PROMETHEUS_URL = "http://127.0.0.1:30000/api/v1/query"

# Check if the package is valid
vnfdPath = input("Enter the path to the VNFD file: ")
# Retrieve VNF package path
vnfPackagePath = os.path.dirname(vnfdPath)
print("Checking the validity of the corresponding VNF package...")
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
        # Read Helm Chart of the Network Service
        print("Reading Helm Chart from VNFD {}...".format(os.path.basename(vnfdPath)))
        helmChart = data['vnfd']['kdu'][0]['helm-chart']
        
        # Read resources requirements from the Helm Chart template
        bashCommand = "helm template {}".format(helmChart)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        parsed_output = yaml.safe_load(output)
        # Do something with the parsed output
        print(parsed_output)

        # Read metrics from Prometheus
        # Prometheus Cpu available
        request = requests.get(PROMETHEUS_URL, params={"query": "node:node_num_cpu:sum"})
        data = request.json()['data']['result'][0]['value']
        promCpuAvailable = data[1]
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
        
''' TO DO
If the package is old (SOL-005) it should be translated to SOL-006. The command to do so:

osm package-translate --recursive foo_knf/
osm package-translate --recursive foo_ns/

Change the retrieval of the metrics from the VNFD. You need to read the metrics from the corresponding
Helm Chart (we are considering just Helm Charts in this phase). The Helm Chart is found under: 

kdu:
- name: bar
  helm-chart: foo/bar

Inside the VNFD.yaml. Once read the repository name, the metrics should be extracted from the file 
obtained with the command:

helm template foo/bar

The metrics are inside:

containers:
- name: ...
  image: ...
  ...
  resources:
    limits:
      cpu: 2000m
      memory: 2048Mi
    requests:
      cpu: 10m
      memory: 256Mi
  
The storage request isn't present. Where should I look for it?  
'''        

