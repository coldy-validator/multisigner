# multisigner

### basic operation

`config.toml` contains the user configuration. The config is preset for [Osmosis](https://github.com/osmosis-labs/osmosis). To sign transactions on Osmosis, only the user's individual address and the multisig address need to be supplied.

If no rpc is provided or the rpc is unavailable when signing, the account number should be supplied. This can be found using `osmosisd q account <address>` or `https://api.osmosis.interbloc.org/cosmos/auth/v1beta1/account/<address>`.

Transactions will be (ideally) named after the sequence number (ex. 0.json, 1.json), but if the name is not numeric, signer will be asked for a sequence number. The proper [file structure](https://github.com/coldy-validator/multisigner/blob/master/docs.md#transaction-repo-file-structure) can be found below. This can be a separate repo for "remote" mode, or under the `local` dir of this repo for "local" mode.

### setup
* copy config file: `cp ./multisigner/config.toml.sample ./multisigner/config.toml`
* edit config: `nano multisigner/config.toml`
* add command: `echo 'alias="python3 multisigner"' >> $HOME/.bash_aliases`

### remote mode
* requires gh installed and logged in, transaction repo set in config
* signatures will be uploaded to repo
* to-do - auto-broadcast, scheduled txs

Anyone with write access to the transaction repo can add and push an unsigned tx to the `transactions/unsigned` dir, which the signers can sign and upload using `multisign 0` for a single tx or `multisign 0 1 2` for multiple txs.



### local mode
* uses local directory in this repo
* signatures will be printed to console

The signer will add the unsigned tx to the `local/transactions/unsigned` dir, which can be signed and printed using `python3 multisigner 0-local` for a single tx or `python3 multisigner 0-local 1-local 2-local` for multiple txs.

### reqs:
* osmosis daemon
* python3, requests and [toml](https://pypi.org/project/toml/0.9.0) modules

### install scripts (WIP):
* [macos](scripts/macos-install.sh)
* [linux](scripts/linux-install.sh)

### transaction file structure
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
