from setuptools import setup
import os
import sys

EXTRA_FILES = "topo-extra-files"


def collect_files():
    return [
        (d, [os.path.join(d, f) for f in files])
        for d, folders, files in os.walk(EXTRA_FILES)
    ]


setup(
    name="docker-topo-ng",
    version="1.0.0-rc0",
    scripts=["bin/docker-topo"],
    data_files=collect_files(),
    python_requires=">=3.5",
    install_requires=["pyyaml", "docker", "netaddr", "packaging"] + (["pyroute2==0.5.3"] if 'linux' in sys.platform.lower() else []),
    url="https://github.com/Vista-Technology/docker-topo-ng",
    license="BSD3",
    author="Andrea Vivaldi",
    author_email="andrea.vivaldi@vistatech.it",
    description="Docker network topology builder (Next Generation)",
)
