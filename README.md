# Pitcoin

Pitcoin is the coolest implementation of a Bitcoin node on python. In this file you will find:
  - Downloading
  - Setting the environment
  - Introduction to structure
  - Running and managing the node
  - Interface instructions
  - Running a local virtual test network


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
```
```
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

#### Node managing:
To manage the node you will need one of two interfaces:
* **wallet_cli** - to work with keys and sending transactions to a node
* **miner_cli** - to enable and disable the mining mode and the consensus mode as well as adding trusted nodes


## Interface instructions
Type **help** in any of the interfaces for a complete list of commands.
#### Wallet-CLI:
* ##### Runnig:
```
$ cd wallet_cli
$ python3 wallet_cli.py
```
```


   Welcome to the wallet command line interface!
   Enter "help" to get the list of commands.
   Enter "exit" to exit


wallet_cli:
```
* ##### Connecting:
To connect to the node enter the command **endpoint** with the node ip with which you want to connect (*remember to start the node first*):
```
wallet_cli: endpoint 127.0.0.1:5000
```

```
[from: cli]: connected
```
If ip is wrong or node is turned off:
```
[from: cli]: cannot connect
```

* ##### Getting key pair:
Now you can get a new key pair or import a private key from a file.

* Getting new key pair:
```
wallet_cli: new
```
```
Private key: "3abb08ca3710108d2d2f219cd6d_DO_NOT_USE_ME_280d22ea61feddd1dbc741993306c51517da0"
Look for your public key at storage/address.txt line 843
```
* Imporing key pair from private key in WIF format:
```
wallet_cli: import storage/wifKey
```
```
Private key: "72c72f8bdccd8ec314cf85b68b_DO_NOT_USE_ME_09a2c0057cf476f6c1b56a7147b85693f586bb"
Look for your public key at storage/address.txt line 844
```
*  ##### Transactions:

* To create transaction use **send** command, specify recipient and amount:
```
send 131SA4U4YAXuJrntwyHg3NXxbhVvs5P8nF 256
```
```
Your raw transaction:
0a0001GRLHQybcgTh9AtQwnJZ6cgRrkjxa5oGSZ0131SA4U4YAXuJrntwyHg3NXxbhVvs5P8nF89ba5d4dc6ea2300a9e579869f705d547619f5115a2caecf1a15d0b1243d17cfbc1993417cc9f9738cfc632dac749a8f4a7c3c20459a088c45cd52371679240fa2eede53e37ea88ef47f111cd1274c7bbf5e201c92cffeec9d577159a4e2c76e322143ca63ab316813522cb67c06d76ce1a523e58fa0f10a390b7880770a9cc5
```
* Now you can send your transaction to the network for validation:
```
wallet_cli: broadcast
```
```
[from: node]: Transaction pended
```
* Very useful command to simulate sending transactions to different addresses is **random**, specify the number of transactions to be sent:
```
wallet_cli: random 3
```
```
[from: node]: Transaction pended
[from: node]: Transaction pended
[from: node]: Transaction pended
```
* ##### To exit:
```
wallet_cli: exit
```
#### Miner-CLI:
* ##### Runnig:
```
$ cd miner_cli
$ python3 miner_cli.py
```
```


   Welcome to the miner command line interface!
   Enter "help" to get the list of commands.
   Enter "exit" to exit


miner_cli:
```
* ##### Connecting:

* To connect to the node enter the command **endpoint** with the node ip with which you want to connect (*remember to start the node first*):
```
miner_cli: endpoint 127.0.0.1:5000
```

```
[from: cli]: connected
```
If ip is wrong or node is turned off:
```
[from: cli]: cannot connect
```
* To turn on/off mining mode:
```
miner_cli: mine
```
```
[from: node]: mining mode on
```
or:
```
[from: node]: mining mode off
```
* To turn on/off consensus mode:
```
miner_cli: consensus
```
```
[from: node]: consensus mode on
```
or:
```
[from: node]: consensus mode off
```

* Adding new trusted peer, specify ip of trusted peer:
```
miner_cli: addnode 127.0.0.1:5005
```
```
[from: cli]: node ip added
```
* ##### To exit:
```
miner_cli: exit
```
## Running a local virtual test network
In order to run a virtual testnet, you need to start each node in the testnet folder. In order for a node to receive and send blocks to other nodes, enable consensus mode. In order for new blocks to appear, start the mining mode. Fill nodes with transactions using the random command. For convenience, you can divide the terminal into several parts:
![example img](https://xteams-gitlab.unit.ua/xteams/module-2-obaranni.git/README_IMGS/example_img_1.png)
