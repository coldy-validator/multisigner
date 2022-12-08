#!/bin/bash

# osmosisd installation
function install_osmosisd {
#  install go
#   clone repo
#    go build
}


# install brew (needs sudo)
#/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
#brew install git gh python3 pip3
#pip3 install requests toml.py

# build osmosisd binary if not present, check for update
version=$(curl -s https://raw.githubusercontent.com/coldy-validator/chain-registry/master/osmosis/chain.json | jq -r '.codebase.recommended_version')
v_check=$(osmosisd version &> /tmp/osmosisd_version && cat /tmp/osmosisd_version)
if [ "$v_check" != "$version " ] ; then
  [ -z "$v_check" ] && { printf "osmosisd not found. installing..." ; install_osmosisd ; } || {
  printf "local osmsosid version $v_check found. upgrade to $version? [y/n]: "  ; read -r upgrade ; }
[ "$upgrade" == "y" ] && install_osmosisd
fi
