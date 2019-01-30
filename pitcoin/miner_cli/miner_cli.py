import cmd
import requests
import json
import re

status_codes = {
    "Transaction pull i empty": 101,
    "Node added": 102,
    "Cannot start mine mode": 103,
    "Transaction pended": 201,
    "Bad json format": 401,
    "Bad transaction": 402,
}

CRED = '\033[91m'
CGREEN = '\033[92m'
CEND = '\033[0m'

node_ip = 'http://127.0.0.1:5000'


class WrongIp(Exception):
    pass


class WalletCli(cmd.Cmd):
    intro = "\n\n   Welcome to the miner command line interface!\n" \
            "   Enter \"help\" to get the list of commands.\n   Enter" \
            " \"exit\" to exit\n\n"
    prompt = "miner_cli: "

    def help_add_node(self):
        print("\nadd_node help:\nAdding new trusted node\nExample: \"addnode 127.0.0.1:5000\"\n")

    def help_getchain(self):
        print("\ngetchain help:\nGet blockchain from node db\n")

    def help_endpoin(self):
        print("\nendpoint help:\nChange node\nExample: \"endpoint 127.0.0.1:5000\"\n")

    def help_getblock(self):
        print("\ngetblock help:\nGets block by id\nExample: \"getblock 456\"\n")

    def help_getchainlen(self):
        print("\ngetchainlen help:\nGet blockchain len from node db\n")

    def help_mine(self):
        print("\nmine help:\nStart producing blocks\n")

    def help_help(self):
        print("\nhelp help:\nList available commands with \"help\" or detailed help with \"help *command_name*\".\n")
        return True

    def emptyline(self):
        self.do_help(0)

    def do_exit(self, line):
        return True

    def do_getchainlen(self, line):
        global node_ip
        url = node_ip + '/chain/length'
        resp = requests.get(url=url, json=[''])
        resp = str(resp.json())
        print(resp)

    def do_getchain(self, line):
        global node_ip
        url = node_ip + '/chain'
        resp = requests.get(url=url, json=[''])
        resp = str(resp.json())
        print(resp)

    def do_endpoint(self, line):
        if len(line) < 1:
            self.help_endpoin()
            return False
        try:
            global node_ip

            line = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}\b", line)
            if len(line) < 1:
                raise WrongIp

            node_ip = 'http://' + line[0]
            url = node_ip + '/chain/length'
            requests.post(url=url, json='')
            print(CGREEN, "[from: cli]: connected", CEND, sep="")
        except WrongIp:
            print(CRED, "[from: cli]: wrong node ip", CEND, sep="")
            self.help_endpoin()
        except requests.exceptions.ConnectionError:
            print(CRED, "[from: cli]: cannot connect", CEND, sep="")

    def do_addnode(self, line):
        if len(line) < 1:
            self.help_add_node()
            return False
        try:
            global node_ip
            url = node_ip + '/addnode'

            line = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}\b", line)
            if len(line) < 1:
                raise WrongIp

            json = {'node_ip': line}
            requests.post(url=url, json=json)
            print(CGREEN, "[from: cli]: node ip added", CEND, sep="")
        except WrongIp:
            print(CRED, "[from: cli]: wrong node ip", CEND, sep="")
        except requests.exceptions.ConnectionError:
            print(CRED, "[from: cli]: cannot send request", CEND, sep="")


    def do_mine(self, line):
        global node_ip
        try:
            url = node_ip + '/mine'
            resp = requests.get(url=url, json=[''])
            if str(resp.json()).find('off') > 0:
                print(CRED, end="")
            else:
                print(CGREEN, end="")
        except requests.exceptions.ConnectionError:
            print(CRED, "[from: cli]: cannot send request", CEND, sep="")
            return False
        except json.decoder.JSONDecodeError:
            print(CRED, "[from: cli]: cannot decode request as json", CEND, sep="")
            return False
        print(resp.json(), CEND)

    def do_consensus(self, line):
        global node_ip
        try:
            url = node_ip + '/consensus'
            resp = requests.get(url=url, json=[''])
            if str(resp.json()).find('off') > 0:
                print(CRED, end="")
            else:
                print(CGREEN, end="")
        except requests.exceptions.ConnectionError:
            print(CRED, "[from: cli]: cannot send request", CEND, sep="")
            return False
        except json.decoder.JSONDecodeError:
            print(CRED, "[from: cli]: cannot decode request as json", CEND, sep="")
            return False
        print(resp.json(), CEND)

    def do_getblock(self, line):
        if len(line) < 1 or not line[0].isdigit():
            self.help_getblock()
            return False
        try:
            global node_ip
            url = node_ip + '/getblock'
            params = (('id', line[0]),)
            resp = requests.get(url=url, params=params)
            if str(resp.json()).find("error") == -1:
                print(CGREEN, "[from: cli]: ", resp.json(), CEND, sep="")
            else:
                print(CRED, "[from: cli]: ", resp.json(), CEND, sep="")
        except requests.exceptions.ConnectionError:
            print(CRED, "[from: cli]: cannot send request", CEND, sep="")


if __name__ == '__main__':
    WalletCli().cmdloop()
