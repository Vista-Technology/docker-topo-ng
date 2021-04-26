# Adding linux Hosts in the topology
A good reason to add simple basic Linux Hosts in the topology will be to testing pourpose.

Before adding Host-related syntax in the topology endpoints, you have to build a custom Alpne-based docker image, using file in this folder.

## Add your public SSH KEY for login withut password

```
$ cd docker-topo-ng/topo-extra-files/host
$ cp <my_pub_key_location/key_name.pub> key.pub
```

## Build the image

```
$ cd docker-topo-ng/topo-extra-files/host
$ ./build.sh
```