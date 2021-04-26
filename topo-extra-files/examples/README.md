# Topology examples

## Simple 3-nodes Spine/Leaf

```yaml
driver: veth
PREFIX: lab
CONF_DIR: ./configs
CEOS_IMAGE: ceos:4.25.1F
links:
  - endpoints:
     - Leaf-1:eth0
     - Leaf-2:eth0
     - Spine-1:eth0
    driver: bridge
  - endpoints: ["Leaf-1:eth1", "Spine-1:eth1"]
  - endpoints: ["Leaf-2:eth1", "Spine-1:eth2"]
PUBLISH_BASE:
  443/tcp: 8000
  22/tcp: [127.0.0.1, 2200]
```

## 3-nodes Spine/Leaf, with internal-only network

```yaml
driver: veth
PREFIX: lab
CONF_DIR: ./configs
CEOS_IMAGE: ceos:4.25.1F
links:
  - endpoints:
     - Leaf-1:eth0
     - Leaf-2:eth0
     - Spine-1:eth0
    driver: bridge
    internal: True
  - endpoints: ["Leaf-1:eth1", "Spine-1:eth1"]
  - endpoints: ["Leaf-2:eth1", "Spine-1:eth2"]
```

As you can see, we have to specify the parameter **Internal: True** to create a bridge network that is completely isolated from the Internet

## 3-nodes Spine/Leaf, with Hosts

```yaml
driver: veth
PREFIX: lab
CONF_DIR: ./configs
CEOS_IMAGE: ceos:4.25.1F
links:
  - endpoints:
     - Leaf-1:eth0
     - Leaf-2:eth0
     - Spine-1:eth0
    driver: bridge
  - endpoints: ["Leaf-1:eth1", "Spine-1:eth1"]
  - endpoints: ["Leaf-2:eth1", "Spine-1:eth2"]
  - endpoints: ["Leaf-1:eth10", "Host-1:eth1:192.168.10.10/24"]
  - endpoints: ["Leaf-2:eth10", "Host-2:eth1:192.168.20.20/24"]
PUBLISH_BASE:
  443/tcp: 8000
  22/tcp: [127.0.0.1, 2200]
```

In this configuration we add 2 Hosts (1 per Leaf) and we specify the IP address associated to the interfaces connected with the device:
* **Host-1:eth1:192.168.10.10/24** - eth1 of Host-1 is connected with eth10 of Leaf-1, and its IP address wil be 192.168.10.10
* **Host-2:eth1:192.168.10.10/24** - eth1 of Host-2 is connected with eth10 of Leaf-2, and its IP address wil be 192.168.20.20

## 3-nodes Spine/Leaf, with Hosts that are exposed

```yaml
driver: veth
PREFIX: lab
CONF_DIR: ./configs
CEOS_IMAGE: ceos:4.25.1F
links:
  - endpoints:
     - Leaf-1:eth0
     - Leaf-2:eth0
     - Spine-1:eth0
    driver: bridge
  - endpoints:
     - Host-1:eth0
    driver: bridge
  - endpoints:
     - Host-2:eth0
    driver: bridge
  - endpoints: ["Leaf-1:eth1", "Spine-1:eth1"]
  - endpoints: ["Leaf-2:eth1", "Spine-1:eth2"]
  - endpoints: ["Leaf-1:eth10", "Host-1:eth1:192.168.10.10/24:192.168.10.0/24,192.168.20.0/24"]
  - endpoints: ["Leaf-2:eth10", "Host-2:eth1:192.168.20.20/24:192.168.0.0/16"]
PUBLISH_BASE:
  443/tcp: 8000
  22/tcp: [127.0.0.1, 2200]
```

In this example we want to expose SSH port also for the Hosts. We can do this by adding endpoints link of type bridge also for the Hosts (1 per host, separated from devices network).
If we want routing works we have to consider the default routing on eth0 interfaces of tghe Hosts and then indicates specific routes for the remaining interfaces:
* Host-1:eth1:192.168.10.10/24:**192.168.10.0/24,192.168.20.0/24** - these 2 networks (comma separated) will have route fixed via eth1
* Host-2:eth1:192.168.10.10/24:**192.168.0.0/16** - this network will have route fixed via eth1