# multisigner

reqs:
* osmosis daemon
* python3, requests and [toml](https://pypi.org/project/toml/0.9.0) modules
* gh to commit to repo

to start:
* copy config file: `cp ./multisigner/config.toml ./multisigner/.config.toml`
* edit config: `nano multisigner/.config.toml`
* run: `python3 multisigner <transaction numbers>`

for example:

`python3 multisigner 42`

`python3 multisigner 4 5 6`

work in progress
