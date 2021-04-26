# docker-topo NG
Docker network topology builder, forked from the original project [networkop/docker-topo](https://github.com/networkop/docker-topo) 

# Supported images

* Arista cEOS-lab
* Arista vEOS-lab
* Arista CVP
* All [vrnetlab images][vrnetlab] - experimental support, currently only tested with CSR1k, vMX and XRv.
* User-defined docker images

# Installation

With Python virtualenv (recommended)

```bash
python3 -m pip install virtualenv
python3 -m virtualenv testdir; cd testdir
source bin/activate 
pip install git+https://github.com/Vista-Technology/docker-topo-ng.git@[VERSION]
```

Without virtualenv

````bash
python3 -m pip install --upgrade --user git+https://github.com/Vista-Technology/docker-topo-ng.git@[VERSION]
````

> Note: Python 2.x is not supported

# Usage

```bash
# docker-topo -h
usage: docker-topo [-h] [-d] [--create | --destroy] [-s] [-a] topology

Tool to create cEOS topologies

positional arguments:
  topology       Topology file

optional arguments:
  -h, --help     show this help message and exit
  -d, --debug    Enable Debug

Actions:
  Create or destroy topology

  --create       Create topology
  --destroy      Destroy topology

Save:
  Save or archive the topology

  -s, --save     Save topology configs
  -a, --archive  Archive topology file and configs
```

# Topology file

Topology file is a YAML file describing how docker containers are to be interconnected.
This information is stored in the `links` variable which 
contains a list of links. Each link is described by a unique set of connected interfaces. 
There are several versions of topology file formats. 

Each link in a `links` array is a dictionary with the following format:
```yaml
links:
  - endpoints:
      - "Device-A:Interface-2" 
      - "Device-B:Interface-1"
  - driver: macvlan
    driver_opts: 
      parent: wlp58s0
    endpoints: ["Device-A:Interface-1", "Device-B:Interface-2"]
```
Each link dictionary supports the following elements:

* **endpoints** - the only mandatory element, contains a list of endpoints to be connected to a link. 
* **driver** - defines the link driver to be used. Currently supported drivers are **veth, bridge, macvlan**. When driver is not specified, default **bridge** driver is used. The following limitations apply:
  * **macvlan** driver will require a mandatory **driver_opts** object described below
  * **veth** driver is talking directly to netlink (no libnetwork involved) and making changes to namespaces
* **internal** - bridge network will be isolated from Internet if True (dedault False)
* **driver_opts** - optional object containing driver options as required by Docker's libnetwork. Currently only used for macvlan's parent interface definition

Each link endpoint is encoded as "DeviceName:InterfaceName:IPPrefix" with the following contraints:

* **DeviceName** determines which docker image is going to be used by (case-insensitive) matching of the following strings:
  * **host** - [alpine-host](https://github.com/Vista-Technology/docker-topo-ng/tree/master/topo-extra-files/host) image is going to be used
  * **cvp** - [cvp](https://github.com/Vista-Technology/docker-topo-ng/tree/master/topo-extra-files/cvp) image is going to be used
  * **veos** - Arista vEOS image built according to the procedure described [here](https://github.com/Vista-Technology/docker-topo-ng/blob/master/topo-extra-files/veos)
  * **vmx** - Juniper vMX image built with [vrnetlab][vrnetlab]
  * **csr** - Cisco CSR1000v image built with [vrnetlab][vrnetlab]
  * **xrv** - Cisco IOS XRv image built with [vrnetlab][vrnetlab]
  * For anything else Arista cEOS image will be used 
* **InterfaceName** must match the exact name of the interface you expect to see inside a container. For example if you expect to connect a link to DeviceA interface eth0, endpoint definition should be "DeviceA:eth0"
* **IPPrefix** - Optional parameter that works **ONLY** for [alpine-host](https://github.com/Vista-Technology/docker-topo-ng/tree/master/topo-extra-files/host) devices and will attempt to configure a provided IP prefix inside a container.
* **RouteList** - Optional parameter, comma separated list of networks with mask in CIDR format (default value "default"), that works **ONLY** for [alpine-host](https://github.com/Vista-Technology/docker-topo-ng/tree/master/topo-extra-files/host) devices and will attempt to configure additional routes (different from default route) associated to that interface.

## Bridge vs veth driver caveats

Both bridge and veth driver have their own set of caveats. Keep them in mind when choosing a driver:

| Features | bridge | veth |
|--------|------|------|
| multipoint links | supported | not supported |
| sudo privileges | not required | required | 
| docker modifications | requires [patched][1] docker deamon | uses standard docker daemon |
| L2 multicast | only LLDP | supported | 
 
You can mix both **bridge** and **veth** drivers in the same topology, however make sure that **bridge** driver links always come first, followed by the **veth** links. For example:

```
driver: veth

links:
  - endpoints: ["Leaf1:eth1", "Leaf2:eth1"]
    driver: 'bridge'
  - endpoints: ["Leaf1:eth2", "Leaf2:eth2"]
  - endpoints: ["Leaf1:eth3", "Leaf2:eth3"]
```

__Note__: You also need to specify the default eth0 intefaces for all endpoints given docker-topo does not create said interface whereas normal docker create does create this interface without defining.

  ## macOS / OSX Support

  Pyroute2 supports BSD as of 0.5.2, but veth drivers will not work in topology files.
 >Pyroute2 runs natively on Linux and emulates some limited subset of RTNL netlink API on BSD systems on top of PF_ROUTE notifications and standard system tools.



## (Optional) Global variables
Along with the mandatory `link` array, there are a number of options that can be specified to override some of the default settings. Below are the list of options with their default values:

```yaml
CEOS_IMAGE: ceos:latest # cEOS docker image name
CONF_DIR: './config' # Config directory to store cEOS startup configuration files
PUBLISH_BASE: 8000 # Publish cEOS ports starting from this number
OOB_PREFIX: '192.168.100.0/24' # Only used when link contains CVP. This prefix is assinged to CVP's eth1
PREFIX: 'CEOS-LAB' # This will default to a topology filename (without .yml extension)
driver: None
```

All of the capitalised global variables can also be provided as environment variables with the following priority:

1. Global variables defined in a topology file
2. Global variables from environment variables
3. Defaults

The final **driver** variable can be used to specify the default link driver for **ALL** links at once. This can be used to create all links with non-default **veth** type drivers:

```yaml
driver: veth
links:
  - endpoints: ["host1:eth1", "host2:eth1"]
  - endpoints: ["host1:eth2", "host3:eth1"]
```


There should be several examples in the `./topo-extra-files/examples` directory

## (Optional) Exposing arbitrary ports

By default, `PUBLISH_BASE` will expose internal HTTPS (443/tcp) port of a container. It is possible to expose any number of internal ports for each container by defining `PUBLISH_BASE` in the following way:

```yaml
PUBLISH_BASE:
  443/tcp: None # Will expose inside 443 to a random outside port
  22/tcp: 2000 # All containers will get their ports exposed starting from outside port 2000
  161/tcp: [127.0.0.1, 1600] # Similar to the above but only exposes ports on the defined local IP address
```

**Note:** topology file must have at least one interface of type **bridge** in order for PUBLISH_BASE to work. Only devices of type cEOS. vEOS and Host can have published ports.

## (Optional) Saving and archiving network topologies

By default, `docker-topo` will pick up any files located in the `CONF_DIR` and, if the filename matches the `PREFIX_DEVICENAME`, will mount it inside the container as `/mnt/flash/startup-config`.

When the topology is running, there's a way to easily save the output of "show run" from each device inside the `CONF_DIR` to make them available on next reboot:

```
$ docker-topo -s topology.yml
Config directory exists, existing files may be overwritten. Continue? [y/n]:y
INFO:__main__:All configs saved in ./config
```

Archive option creates a `tar.gz` file with the `CONF_DIR` directory and the topology YAML file

```
$ docker-topo -a topology.yml
INFO:__main__:Archive file topo.tar.gz created
$ tar -tvf topo.tar.gz 
drwxr-xr-x root/root         0 2018-09-14 11:53 config/
-rw-r--r-- null/null       660 2018-09-11 15:08 topology.yml

```

## (Optional) User-defined docker images
It is possible to create topology with arbitrary docker images. One such example is the [openstack topology](https://github.com/networkop/docker-topo/blob/master/topo-extra-files/examples/v2/openstack.yml). Whenever a `CUSTOM_IMAGE` dictionary present, any device names that did not match against the well-known images (e.g. cEOS, vEOS, Host, VMX, CSR etc.), will be matched against the keys of this dictionary and, if match is found, the corresponding value will be used as an image. So in case the topology file has:

```yaml
CUSTOM_IMAGE:
  search_key: docker_image
```

The `docker-topo` image matching logic will try to see if `search_key in device_name.lower()` and if True, will build a `Generic` device type with `self.image == docker_image`.


# Examples
Example configuration topologies can be found [here](https://github.com/Vista-Technology/docker-topo-ng/tree/master/topo-extra-files/examples).

# Destroy a topology

```bash
docker-topo --destroy topo-extra-files/examples/3-node.yml
```

# Troubleshooting

* If you get the following error, try renaming the topology filename to a string [shorter than 15 characters](https://github.com/svinota/pyroute2/issues/452)

  ```
  pyroute2.netlink.exceptions.NetlinkError: (34, 'Numerical result out of range')
  ```

* CVP can't connect to cEOS devices - make sure that CVP is attached with at least two interfaces. The first one is always for external access and the second one if always for device management

[1]: https://networkop.co.uk/post/2018-03-03-docker-multinet/
[alpine-host]: https://github.com/networkop/docker-topo/tree/master/topo-extra-files/host
[vrnetlab]: https://github.com/plajjan/vrnetlab