# cosmos sdk multisig helper

downloads from, signs, and uploads transactions to a git repo

to start:
* copy config file: `cp ./multisigner/config.toml ./multisigner/.config.toml`
* edit config : `nano multisigner/.config.toml`
* run: `python3 multisigner <transaction numbers>`

for example:

`python3 multisigner 42`

`python3 multisigner 4 5 6`

![signer1](https://user-images.githubusercontent.com/98429202/205882465-58ff455d-fd7c-458f-9f0a-f1cb53b116a7.png)
![signer2](https://user-images.githubusercontent.com/98429202/205882148-b9fff0b1-a74a-48ff-9ba4-6fc3ce18f2b3.png)
