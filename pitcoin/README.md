# Pitcoin

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

Pitcoin is the coolest implementation of a Bitcoin node on python. In this file you will find:
  - Downloading
  - Setting the environment
  - Introduction to structure
  - Running and managing the node
  - Interface instructions
  - Run a local virtual test network


## Downloading

Cloning from git.

```
$ git clone https://xteams-gitlab.unit.ua/xteams/module-2-obaranni.git
```

## Setting the environment
Firs you need to install [python3 and pip](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04)

To create an environment:
```
$ cd module-2-obaranni
$ python3 -m venv venv_pitcoin
```
Environment activation:
```
$ source venv_pitcoin/bin/activate
```

Installation of modules in the environment:
```
$ pip install -r requirements.txt
```

## Introduction to structure

To see the project structure go to the Pitcoin folder:

```
$ cd pitcoin
```

Pitcoin folder consists of 4 parts:

| Directory | Content |
| ------ | ------ |
| wallet_cli | сommand line interface for working with keys and sending transactions to a node |
| miner_cli | сommand line interface for node configuration |
| node | node with network connectivity |
| testnet | several nodes with pre-configured configuration files and a startup script that simulate the operation of a decentralized network |

## Running and managing the node
#### Node configuration:
To configurate node:

```
$ cd node
$ cat config
{
    "host_ip": "127.0.0.1:5000",
    "mining_mode": "off",
    "consensus_mode": "off",
    "trusted_peers": [
        "127.0.0.1:5050",
        "127.0.0.1:5060"
    ]
}
```
If you want to change the ip or port of this node, change it in the **"host_ip"** field. You can also change the list of trusted nodes in the **"trusted_peers"** field.

To run the node:
```
$ python3 run_node.py
```

#### Node managing
To manage the node you will need one of two interfaces:
* **wallet_cli** - to work with keys and sending transactions to a node
* **miner_cli** - to enable and disable the mining mode and the consensus mode as well as adding trusted nodes


## Interface instructions
#### Wallet-CLI:
Runnig:
```
$ cd wallet_cli
$ python3 wallet_cli.py


   Welcome to the wallet command line interface!
   Enter "help" to get the list of commands.
   Enter "exit" to exit


wallet_cli:
```
To connect to the node enter the command **endpoint** with the node ip with which you want to connect (*remember to start the node first*):
```
wallet_cli: endpoint 127.0.0.1:5000
```

#### Miner-CLI:
