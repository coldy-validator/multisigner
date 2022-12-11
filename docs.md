# multisigner

to-do:
* document online vs offline modes

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

install scripts:
* [macos](scripts/macos-install.sh)
* [linux](scripts/linux-install.sh)

### transaction repo file structure
<pre>
└── transactions
    ├── unsigned
    │   ├── 0.json
    │   └── 1.json
    ├── signatures
    │   ├── 0-name1-sig.json
    │   ├── 0-name2-sig.json
    │   ├── 1-name1-sig.json
    │   └── 1-name3-sig.json
    └── signed
        ├── 0-signed.json
        └── 1-signed.json
</pre>
