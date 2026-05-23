#!/bin/bash
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest > micromamba.tar.bz2
tar -xvjpf micromamba.tar.bz2 bin/micromamba
rm micromamba.tar.bz2
./bin/micromamba create -p ./env311 python=3.11 -c conda-forge -y
