# multisigner

🚧 may not be up-to-date, stay tuned 🚧

### basic operation

* `config.py` is the default user configuration file. The config is preset for [Osmosis](https://github.com/osmosis-labs/osmosis). To sign transactions on Osmosis, only the user's name, individual address and the multisig address need to be supplied.
* Other config files located in the `multisigner/` dir can be used with the `-c` flag (ex. `python3 multisigner -c config_test.py`)
* If no rpc is provided or the rpc is unavailable when signing, the account number should be supplied. This can be found using `osmosisd q account <address>` or `https://api.osl.zone/cosmos/auth/v1beta1/account/<address>`.

### setup
* install dependencies (git, osmosisd, python3)
* configure git email address (`git config --global user.email <email>`)
* add ssh key to github (hint: [deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys#deploy-keys) can be used for security. needs write access)
* copy config file: `cp ./multisigner/config.py.sample ./multisigner/config.py`
* edit config: `nano multisigner/config.py`
* (optional) add alias: `echo 'alias multisigner="python3 $HOME/multisigner"' >> $HOME/.bash_aliases`

### remote mode
* requires git ssh key set up
* signatures will be uploaded to repo
* to-do - auto-broadcast, scheduled txs

Anyone with write access to the transaction repo can add and push an unsigned tx to the `transactions/unsigned` dir, which the signers can sign and upload using `multisign 0` for a single tx or `multisign 0 1 2` for multiple txs.

~~### local mode~~ not currently working
* ~~uses local directory in this repo~~
* ~~signatures will be printed to console~~

~~The signer will add the unsigned tx to the `local/transactions/unsigned` dir, which can be signed and printed using `python3 multisigner 0-local` for a single tx or `python3 multisigner 0-local 1-local 2-local` for multiple txs.~~

### transaction file structure
<pre>
└── transactions
    ├── unsigned
    │   ├── 0-*
    │   └── 1-*
    ├── signatures
    │   ├── 0-name1-*
    │   ├── 0-name2-*
    │   ├── 1-name1-*
    │   └── 1-name3-*
    └── signed
        ├── 0-signed-*
        └── 1-signed-*
</pre>
