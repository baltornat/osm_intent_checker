# Development VNFD path: test/test_vnf/test_vnfd.yaml
# Development Prometheus url: http://10.152.183.160:9090/api/v1/query
# This is the LoadBalancer's IP of the service where Prometheus is running

import yaml
import requests
import subprocess
import os
import re
import pprint

###################################################################################################
# GLOBAL VARIABLES
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
        
###################################################################################################
# FUNCTIONS
def convert(string):
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

def find_nested_tags(data, tag_name):
	result = []
	# If data is of type dict then True
	if isinstance(data, dict):
		for key, value in data.items():
			if key == tag_name:
				# Append to the list the value
				result.append(value)
			else:
				# Concat to the list the nested result
				result += find_nested_tags(value, tag_name)
	# If data is of type list then True
	elif isinstance(data, list):
		for item in data:
			result += find_nested_tags(item, tag_name)
	return result

###################################################################################################
# MAIN
# Check if the package is valid
vnfdPath = input("Enter the path to the VNFD file: ")
# Retrieve VNF package path
vnfPackagePath = os.path.dirname(vnfdPath)
print("\n-.- Checking the validity of the corresponding VNF package...\n")
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
print("-.- Reading Helm Chart from VNFD {}...".format(os.path.basename(vnfdPath)))
helmChart = data['vnfd']['kdu'][0]['helm-chart']
print("Found Helm Chart {}".format(helmChart))

# Check the Helm Chart to find resources requirements (METHOD 1: helm template foo)
'''
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
cpuLimit = convert(resources['limits']['cpu'])
print("Chart cpu limit: {}".format(cpuLimit))
cpuRequest = convert(resources['requests']['cpu'])
print("Chart cpu request: {}".format(cpuRequest))
memoryLimit = convert(resources['limits']['memory'])
print("Chart memory limit: {}".format(memoryLimit))
memoryRequest = convert(resources['requests']['memory'])
print("Chart memory request: {}".format(memoryRequest))
'''

# Check the Helm Chart to find resources requirements (METHOD 2: helm show values foo)
output = subprocess.check_output(['helm', 'show', 'values', helmChart], text=True)
data = yaml.safe_load(output)
resources = find_nested_tags(data, 'resources')
persistence = find_nested_tags(data, 'persistence')
print("\n-.- Recursively looking for tags 'resources' and 'persistence' inside the file 'values.yaml' of the Helm Chart {}...".format(helmChart))
print("\n-.- Listing all 'resources' tags encountered...")
pprint.pprint(resources)
print("\n-.- Listing all 'persistence' tags encountered...")
pprint.pprint(persistence)
print("\n-.- Calculating the total cpu request and the total cpu limit...")
requestsCpuSum = sum([convert(r['requests']['cpu']) for r in resources if 'requests' in r and 'cpu' in r['requests']])
limitsCpuSum = sum([convert(r['limits']['cpu']) for r in resources if 'limits' in r and 'cpu' in r['limits']])
print("Total cpu requested: {} cpu unit(s)".format(requestsCpuSum))
print("Total cpu limit: {} cpu unit(s)".format(limitsCpuSum))
print("\n-.- Calculating the total memory request and the total memory limit...")
requestsMemorySum = sum([convert(r['requests']['memory']) for r in resources if 'requests' in r and 'memory' in r['requests']])
limitsMemorySum = sum([convert(r['limits']['memory']) for r in resources if 'limits' in r and 'memory' in r['limits']])
print("Total memory requested: {} bytes".format(requestsMemorySum))
print("Total memory limit: {} bytes".format(limitsMemorySum))
print("\n-.- Calculating the total storage size requested...")
storageSum = sum([convert(size) for item in persistence for size in find_nested_tags(item, 'size')])
print("Total storage size requested: {} bytes".format(storageSum))

# Read metrics from Prometheus
# Prometheus Cpu available
print("\n-.- Reading metrics from Prometheus at the following url: {}...".format(PROMETHEUS_URL))
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
request = requests.get(PROMETHEUS_URL, params={"query": "node_filesystem_avail_bytes"})
data = request.json()['data']['result'][0]['value']
promStorageAvailable = float(data[1])
print("Node storage available: {}".format(promStorageAvailable))

# Check if the deployment is possible
print("\n-.- Checking if the deployment is possible...")
print("REQUESTS: ")
print("(Outcome)\t(Metric)\t\t\t(Chart/Node)")
if requestsCpuSum <= promCpuAvailable:
	print("[OK]\t\tTotal cpu requested:\t\t{}/{} cpu unit(s)".format(requestsCpuSum, promCpuAvailable))
else:
	print("[X]\t\tTotal cpu requested:\t\t{}/{} cpu unit(s)".format(requestsCpuSum, promCpuAvailable))
if requestsMemorySum <= promMemoryAvailable:
	print("[OK]\t\tTotal memory requested:\t\t{}/{} bytes".format(requestsMemorySum, promMemoryAvailable))
else:
	print("[X]\t\tTotal memory requested:\t\t{}/{} bytes".format(requestsMemorySum, promMemoryAvailable))
if storageSum <= promStorageAvailable:
	print("[OK]\t\tTotal storage requested:\t{}/{} bytes".format(storageSum, promStorageAvailable))
else:
	print("[X]\t\tTotal storage requested:\t{}/{} bytes".format(storageSum, promStorageAvailable))
print("LIMITS: ")
print("(Outcome)\t(Metric)\t\t\t(Chart/Node)")
if limitsCpuSum <= promCpuAvailable:
	print("[OK]\t\tTotal cpu limit:\t\t{}/{} cpu unit(s)".format(limitsCpuSum, promCpuAvailable))
else:
	print("[X]\t\tTotal cpu limit:\t\t{}/{} cpu unit(s)".format(limitsCpuSum, promCpuAvailable))
if limitsMemorySum <= promMemoryAvailable:
	print("[OK]\t\tTotal memory limit:\t\t{}/{} bytes".format(limitsMemorySum, promMemoryAvailable))
else:
	print("[X]\t\tTotal memory limit:\t\t{}/{} bytes".format(limitsMemorySum, promMemoryAvailable))

# DEPLOYMENT TO BE IMPLEMENTED    
print("\n-.- Trying to deploy the Network Service...")

''' TO DO
If the package is old (SOL-005) it should be translated to SOL-006. The command to do so:

osm package-translate --recursive foo_knf/
osm package-translate --recursive foo_ns/

I found the command: helm show values stable/hadoop
Should I need to extract the resources requirements from here? It shows the content of the file 
"values.yaml". Here is the link of the example: https://git.app.uib.no/caleno/helm-charts/tree/0cf77f9c1bfeca58f78b142e1186534c3de84b6c/stable/hadoop

List of charts: https://github.com/helm/charts

What if the chart isn't known? Should I add the repo?
'''        

