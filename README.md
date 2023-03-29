# OSM Intent Checker

Università degli Studi di Milano - Department of Computer Science

## The project

The thesis work consists in the creation of a network service which, once integrated, allows to negotiate the
configurations of the network infrastructure with a 5G Core Network. Specifically, the service to be created must be
integrated with a monitoring and analysis framework present in a 5G Core Network and must allow for the deployment of
services within Kubernetes based on their configurations. These configurations will be defined by particular contracts
called "intent"; the network service object of the thesis will have to try to understand if a received intent is
feasible or not. If the intent is not feasible, the service to be implemented must be able to suggest an alternative
solution to allow the deployment of the service to which the intent refers

## Directory Tree

- `osm_intent_controller/`
    - `classes/`: contains classes definitions
    - `exceptions/`: contains a class to manage custom exceptions
    - `network_services_test/`: contains presetted VNFDs/NSDs to run tests
    - `utils/`: contains global functions
