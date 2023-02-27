#!/usr/bin/env python
from os import path
from sys import argv
from glob import glob
from time import sleep
from json import dumps,load,loads
from importlib import import_module
from getopt import getopt,GetoptError
from __init__ import bcolors, __location__
from subprocess import check_output,CalledProcessError

def print_sig(signed):  # print signatures to console
    print(f"\nprinting signatures now. you can copy and paste this output")
    sleep(1)
    for sig in signed:
        with open(sig["file"]) as f:
            print(
                f"{bcolors.magenta}\n----------------------sig {bcolors.blue}{sig['tx']}{bcolors.magenta} begins----------------------\n{bcolors.grey}"
                + dumps(load(f), indent=1)
                + f"{bcolors.magenta}\n----------------------sig {bcolors.blue}{sig['tx']}{bcolors.magenta} ends------------------------{bcolors.nc}")

def main():
    config_file = "config"  # default config file
    arg_list = argv[1:]  # check command line args
    try:
        args,values = getopt(arg_list, "hac:s:")
        for arg,value in args:
            if arg in "-h":
                print("help menu")  # to do
                exit()
            elif arg in "-c":  # custom config
                if value.endswith(".py"):
                    config_file = value[:-3]
                else:
                    config_file = value
            elif arg in "-s":
                tx_list = value.split(" ")
                if len(tx_list) != 2:
                    print(f"{bcolors.red}error{bcolors.nc}: must provide exactly two transactions (first and last) to sign in sequence")
                    exit()
                else:
                    txs = {"mode":"seq", "txs": [ tx_list[0], tx_list[1] ]}
#            elif arg in "-a":  # to do: must be mutually exclusive with -s
#                txs = {"mode":"all"}
        try:
            if txs["mode"] == "seq" or txs["mode"] == "all": pass
        except UnboundLocalError:
            if values == []:
                print(f"{bcolors.red}error: no txs provided {bcolors.nc}")
                exit()
            else:
                txs = {"mode":"std", "txs": values}
    except GetoptError as err:
        print(f"{bcolors.yellow}error - {str(err)}{bcolors.nc}")
        exit()
    try:
        config = import_module(config_file)
    except ModuleNotFoundError:
        print(
            f"{bcolors.red}error{bcolors.nc}: config file not found.\n\n"
            f"quick setup:\n\n  1. {bcolors.blue}`cp ./multisigner/config.py.sample ./multisigner/config.py`{bcolors.nc}\n"
            f"  2. {bcolors.blue}`nano multisigner/config.py`{bcolors.nc} and fill in your info\n")
        exit()
    if not config.client["binary"]:
        print(f"{bcolors.red}error: no binary name in config{bcolors.nc}")
        exit()
    else:
        binary = config.client["binary"]
    try:
        check_output(["which", binary])
    except CalledProcessError:
        print(f"{bcolors.red}error: {binary} not installed or not in path.{bcolors.nc} please see <link> for a guide")
        exit()
    if not config.multisig["signer_address"] or not config.multisig["multisig_address"]:
        print(f"{bcolors.red}error: signer and/or multisig address not configured{bcolors.nc}")
        exit()
    try:
        check_output(["git", "config", "user.email"])  # check if git email configured
        if config.multisig["repo"]:
            repo = config.multisig["repo"]
            repo_dir = path.join(__location__, repo.split('/')[1])
            if not path.exists(repo_dir):  # if the repo exists in config, make sure we have it and pull changes
                check_output(
                    ["git", "clone", "git@github.com:" + repo, repo_dir, "--quiet"])
            check_output(
                ["git", "--git-dir", f"{repo_dir}/.git",
                "--work-tree", repo_dir, "pull", "--quiet"])
        else:
            repo = "null"  # if no repo in config, we will print the signatures later as they can't be pushed
    except (CalledProcessError,FileNotFoundError):
        print(f"{bcolors.yellow}warn: git not configured{bcolors.nc}")
        repo = "null"
    if config.multisig["signer_name"]:
        name = config.multisig["signer_name"]
    else:
        name = "null"
    if not config.client["rpc"]:
        RPC = "null"
    else:
        RPC = config.client["rpc"]
    if config.multisig["account_number"]:
        acct = config.multisig["account_number"]  # get the account number from config or rpc call
    else:
        if RPC == "null":
            print("no rpc or account number in config. you need one or the other")
            exit()
        else:
            try:
                acct = loads(
                    check_output([binary, "q", "account", config.multisig["multisig_address"], "--node", RPC, "--output", "json"]).decode("utf-8"))["account_number"]
            except CalledProcessError:
                print(f"{bcolors.red}rpc error.{bcolors.nc} please check your connection, try a different node, or wait and try again - or add your account number to config for offline mode")
                exit()
    if name == "null":
        print("\ngit not installed/configured. txs will be printed, not uploaded")
    signed = []
    if txs["mode"] == "seq":
        for file in txs["txs"]:
            if not path.exists(path.join(repo_dir, "transactions", "unsigned", file)):
                print(f"{bcolors.red}error{bcolors.nc}: {file} - file not found")
                exit()
        tx_list = []
        sequence = range(int(txs["txs"][0].split("-")[0]),int(txs["txs"][1].split("-")[0]) + 1)
        for tx in sequence:
            tx_list = tx_list + (glob(f"{tx}-*",root_dir= path.join(repo_dir, "transactions", "unsigned")))
    elif txs["mode"] == "std":
        tx_list = txs["txs"]
    for tx in tx_list:  # fetch designated txs
        if tx.endswith("-local"):
            name = "null"  # if we get a local tx force print
            tx = tx.split("-")[0]
            tx_file = path.join(__location__, "local", "transactions", "unsigned", tx)
            sig_file = path.join(__location__, "local", "transactions", "signatures", tx)
        else:
            if repo == "null":
                print("error - no repo in config and git signing attempted.")
                exit()
            tx_file = path.join(repo_dir, "transactions", "unsigned", tx)
            sig_file = path.join(repo_dir, "transactions", "signatures", f"{tx[:-5]}-{name}.json")
        if not path.exists(tx_file):
            print(f"{bcolors.red}error{bcolors.nc}: {tx} - file not found")
            exit()
        print(f"\n{bcolors.blue}{tx}{bcolors.nc}:")  # print the "messages" to console for review
        with open(tx_file) as f:
            body = load(f)['body']
        print(f"{bcolors.yellow}{dumps(body['messages'], indent=1)}{bcolors.nc}")
        print(f"{bcolors.magenta}memo: {dumps(body['memo'], indent=1)}\n{bcolors.nc}")
        if tx.split('-')[0].isnumeric():  # if the tx begins with a number and a dash, we assume its the sequence number, if not we ask for one
            seq = tx.split('-')[0]
        else:
            seq = input("error - sequence number not provided. input sequence number if known, or 'n' to check rpc for next seq number: ")
            if seq == "n":
                if RPC == "null":
                    print("error - no rpc in config")
                else:
                    try:
                        seq = loads(check_output([binary, "q", "account", config.multisig["signer_address"], "--node", RPC, "--output", "json"]).decode("utf-8"))["sequence"]
                    except CalledProcessError:
                        print(f"{bcolors.red}rpc error. please check your connection, try a different node, or wait and try again - or enter sequence number")
            while not seq.isnumeric():
                seq = input("error - sequence number invalid. input sequence number if known: ")
        try:
            check_output(  #  sign the txs
                    [binary, "tx", "sign", tx_file, "--from", config.multisig["signer_address"],
                    "--multisig", config.multisig["multisig_address"], "--keyring-backend", config.client["keyring"], "--account-number", acct, "--sequence", seq,
                    "--chain-id", config.client["chain_id"], "--offline", "--output-document", sig_file])
            if path.isfile(sig_file):
                signed.append({"tx": tx, "file": sig_file})
        except CalledProcessError:
            print(f"sig {tx} {bcolors.red}failed{bcolors.nc}. please check the tx or your config")
    if signed != []:  # choose to print or upload, or skip if not logged in
        if name == "null" or repo == "null":
            choice = "2"
        else:
            choice = input("signatures completed\n\n   1) upload signatures to repo\n   2) print signatures to console\n\nyour choice: ")
            while choice != "1" and choice != "2":
                sleep(0.1)
                choice = input("invalid input. please enter 1 to upload or 2 to print signatures: ")
    else:
        print(f"{bcolors.red}error{bcolors.nc}: no signatures found")
        exit()
    if choice == "1":  # add signatures to repo and push to remote
        try:
            check_output(["git", "--git-dir", f"{repo_dir}/.git", "--work-tree", repo_dir, "pull", "--quiet"])
            check_output(["git", "--git-dir", f"{repo_dir}/.git", "--work-tree", repo_dir, "add", "./transactions/signatures/*"])
            check_output([ "git", "--git-dir", f"{repo_dir}/.git", "--work-tree", repo_dir, "commit", "-m" f"{name} signed {' '.join([x['tx'] for x in signed])}"])
            check_output(["git", "--git-dir", f"{repo_dir}/.git", "--work-tree", repo_dir, "push", "--quiet"])
            print(f"\n{bcolors.green}signatures uploaded to repo{bcolors.nc}")
        except CalledProcessError:
            print(f"\n{bcolors.red}error uploading signatures to repo{bcolors.nc}")
            print_sig(signed)
    elif choice == "2":
        print_sig(signed)
    else:
        print("fatal error")
        exit()

if __name__ == "__main__":
    main()
