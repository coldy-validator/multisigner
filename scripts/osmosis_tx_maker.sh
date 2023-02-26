#!/bin/bash

[ -z "$(which osmosisd)"] && { printf "osmosisd not found int \$PATH" ; exit 1 }
[ -z "$(which jq)"] && { printf "please install jq\n\n`sudo apt update \&\& sudo apt install jq`" ; exit 1 }

printf "enter "from" address: "
read -r key

function build_tx {
  [ -z "$1" ] && tx_error "$2"
  message=$(jq '.body.messages' <<<$1 2> /dev/null)
  [ -z "$2" ] && tx="$1" || tx=$(jq ".body.messages += $message" <<<$2 2> /dev/null)
  add_message "$tx"
}

function add_message {
  printf "add another message? [y/n]: "
  read -r choice
  while [ "$choice" != "y" ] && [ "$choice" != "n" ] ; do
    printf "error - choose "y" or "n": "
    read -r choice
  done
  if [ "$choice" == "y" ] ; then
    printf "enter your next message: "
    read -r n_message
    create_message "$n_message" "$1"
  else
    print_tx "$1"
  fi
}

function create_message {
    case "$1" in "send"*)
  x=${1#"send"}
  tx=$(osmosisd tx bank send $key $x  --from $key --generate-only)
    ;; "grant"*)
  tx=$(osmosisd tx authz $1 --from $key --generate-only)
    ;; "vote"*)
  tx=$(osmosisd tx gov $1 --from $key --generate-only)
    ;; esac
  build_tx "$tx" "$2"
}

function tx_error {
  printf "error - last input invalid - try again: "
  read -r again
  create_message "$again" "$1"
}

function print_tx {
  printf "\nyour completed tx:\n\n"
  jq . <<<$1
  # printf "\nenter a file name to write to file: "
  # read -r file
  # cat $tx > $file
  exit
}

printf "enter the first tx message in an abreviated manner like such:\n\nsend tx:\nsend <to> <amount>\nfor a vote tx:\nvote 69 yes\n\nsupported messages:\nsend, vote, \n\nyour message: "
read -r u_message
if [ ! -z "$u_message" ] ; then
  create_message "$u_message"
else
  printf "error - no input\n"
fi
