# cosmos sdk multisig helper

downloads from, signs, and uploads transactions to a git repo

to start:
* copy config file: `cp ./multisigner/config.toml ./multisigner/.config.toml`
* edit config : `nano multisigner/.config.toml`
* run: `python3 multisigner <transaction numbers>`

for example:

`python3 multisigner 42`

`python3 multisigner 4 5 6`
