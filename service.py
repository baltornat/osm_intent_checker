# Development VNFD path: test/test_vnf/test_vnfd.yaml
# Development Prometheus url: http://10.152.183.160:9090/api/v1/query
# This is the LoadBalancer's IP of the service where Prometheus is running

import yaml
import requests
import subprocess
import os
import re

PROMETHEUS_URL = "http://10.152.183.160:9090/api/v1/query"
# https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu
SUFFIXES = {
        'Ki': 2**10,
        'Mi': 2**20,
        'Gi': 2**30,
        'Ti': 2**40,
        'Pi': 2**50,
        'Ei': 2**60,
        'm': 10**-3,
        'k': 10**3,
        'M': 10**6,
        'G': 10**9,
        'T': 10**12,
        'P': 10**15,
        'E': 10**18
        }

def normalize(string):
	# Extract the numerical value and suffix from the input string
	match = re.match(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]*)', string)
	value = float(match.group(1))
	suffix = match.group(2)
	# Convert the numerical value
	if suffix in SUFFIXES:
		multiplier = SUFFIXES[suffix]
		new_value = float(value * multiplier)
	else:
		new_value = float(value)
	return new_value	

# Check if the package is valid
vnfdPath = input("Enter the path to the VNFD file: ")
# Retrieve VNF package path
vnfPackagePath = os.path.dirname(vnfdPath)
print("Checking the validity of the corresponding VNF package...\n")
output = subprocess.check_output(['osm', 'package-validate', '--recursive', '--old', vnfPackagePath], text=True)
print(output)

# Open VNFD
with open(vnfdPath, "r") as vnfd:
	try:
		# Load data from vnfd
		data=yaml.safe_load(vnfd)
	except yaml.YAMLError as exception:
		print(exception)

# Read Helm Chart of the Network Service
print("Reading Helm Chart from VNFD {}...".format(os.path.basename(vnfdPath)))
helmChart = data['vnfd']['kdu'][0]['helm-chart']
print("Found Helm Chart {}".format(helmChart))
# Check the Helm Chart to find resources requirements
output = subprocess.check_output(['helm', 'template', helmChart], text=True)
# Split the output into separate documents
documents = output.split('---\n')
# Parse each document separately
for document in documents:
	parsed_document = yaml.safe_load(document)
	# If the parsed document has the tag "kind" set to the value "StatefulSet"
	if parsed_document is not None and parsed_document.get('kind') == 'StatefulSet':
		# Get the resources requirements
		resources = parsed_document.get('spec', {}).get('template', {}).get('spec',{}).get('containers', [{}])[0].get('resources', {})
		# Stop after the first found
		break
		
# Split cpu/memory limits from cpu/memory requests
cpuLimit = normalize(resources['limits']['cpu'])
print("Chart cpu limit: {}".format(cpuLimit))
cpuRequest = normalize(resources['requests']['cpu'])
print("Chart cpu request: {}".format(cpuRequest))
memoryLimit = normalize(resources['limits']['memory'])
print("Chart memory limit: {}".format(memoryLimit))
memoryRequest = normalize(resources['requests']['memory'])
print("Chart memory request: {}".format(memoryRequest))

# Read metrics from Prometheus
# Prometheus Cpu available
request = requests.get(PROMETHEUS_URL, params={"query": "node:node_num_cpu:sum"})
data = request.json()['data']['result'][0]['value']
promCpuAvailable = float(data[1])
print("Node cpu available: {}".format(promCpuAvailable))
# Prometheus Memory available
request = requests.get(PROMETHEUS_URL, params={"query": "node_memory_MemAvailable_bytes"})
data = request.json()['data']['result'][0]['value']
promMemoryAvailable = float(data[1])
print("Node memory available: {}".format(promMemoryAvailable))
# Prometheus Storage available
'''
request = requests.get(PROMETHEUS_URL, params={"query": "node_filesystem_avail_bytes"})
data = request.json()['data']['result'][0]['value']
promStorageAvailable = float(data[1])
print("Node storage available: {}".format(promStorageAvailable))
'''

# Check if the deployment is possible
print("Checking if the deployment is possible...")
if cpuLimit <= promCpuAvailable:
	print("Cpu OK")
else:
	print("Cpu NOT OK")
if memoryLimit <= promMemoryAvailable:
	print("Memory OK")
else:
	print("Memory NOT OK")

# DEPLOYMENT TO BE IMPLEMENTED    
print("Trying to deploy the Network Service")

''' TO DO
If the package is old (SOL-005) it should be translated to SOL-006. The command to do so:

osm package-translate --recursive foo_knf/
osm package-translate --recursive foo_ns/
  
The storage request isn't present. Where should I look for it?  

I found the command: helm show values stable/hadoop
Should I need to extract the resources requirements from here? It shows the content of the file 
"values.yaml". Here is the link of the example: https://git.app.uib.no/caleno/helm-charts/tree/0cf77f9c1bfeca58f78b142e1186534c3de84b6c/stable/hadoop
'''        

