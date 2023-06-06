# OSM Intent Checker

Università degli Studi di Milano - Department of Computer Science

## The project

Existing NFV orchestrators are not able to understand at first glance whether the deployment of a network service or a set of network services required by an intent is possible or not. The OSM orchestrator tries to deploy the network services and if the deployment fails for the lack of available resources on the target machine it just prints errors. This is inefficient because trying the deployment of one or more network services costs time and needs computational effort. Our approach aims to add a layer between the intent management system and the orchestrator OSM by implementing checks to verify if the intent is feasible or not before trying to deploy the services and thus saving time and resources.

## Directory Tree

- `osm_intent_checker/`
    - `classes/`: contains classes definitions
    - `exceptions/`: contains a class to manage custom exceptions
    - `network_services_test/`: contains preset VNFDs/NSDs to run tests
    - `utils/`: contains global functions

## Installation

Before running OSM Intent Checker you have to install the required dependencies:
`pip install -r requirements.txt`

### config.py

You also have to generate a `config.py` file inside the main folder. This file must contain the following constants:
- `USERNAME`: a valid ETSI OSM username
- `PASSWORD`: a valid ETSI OSM password
- `NBI_HOSTNAME`: the hostname related to the North Bound Interface of OSM (e.g. http://nbi.your_machine_ip.nip.io/osm/)
- `PROMETHEUS_URL`: the hostname of a valid Prometheus Operator instance on your Kubernetes cluster (e.g. http://prom_operator_ip:port/api/v1/query)
- `VIM_ACCOUNT`: the name of a valid VIM account
