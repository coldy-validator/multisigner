#!/bin/bash

# osmosisd installation
function install_osmosisd {
#  install go
  git clone https://github.com/osmosis-labs/osmosis /tmp/osmosis
  cd /tmp/osmosis
  git checkout $1
  make build
  c=$(which osmosis)
  [ ! -z "$c" ] && { rm $c ; mv /tmp/osmosis/build/osmosisd $c ; } || mv /tmp/osmosis/build/osmosisd /usr/local/bin/
}


# install brew (needs sudo)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install coreutils git gh python3 pip3 jq
pip3 install requests toml.py

# build osmosisd binary if not present, check for update
version=$(curl -s https://raw.githubusercontent.com/coldy-validator/chain-registry/master/osmosis/chain.json | jq -r '.codebase.recommended_version')
v_check=$(osmosisd version &> /tmp/osmosisd_version && cat /tmp/osmosisd_version)
if [ "$v_check" != "$version " ] ; then
  [ -z "$v_check" ] && { printf "osmosisd not found. installing..." ; install_osmosisd $version ; } || {
  printf "local osmsosid version $v_check found. upgrade to $version? [y/n]: "  ; read -r upgrade ; }
[ "$upgrade" == "y" ] && install_osmosisd $version
fi
