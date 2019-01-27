import cmd
import requests
import json

status_codes = {
    "Transaction pull i empty": 101,
    "Transaction pended": 201,
    "Bad json format": 401,
    "Bad transaction": 402,
}

CRED = '\033[91m'
CGREEN = '\033[92m'
CEND = '\033[0m'

class WalletCli(cmd.Cmd):
    intro = "\n\n   Welcome to the miner command line interface!\n" \
            "   Enter \"help\" to get the list of commands.\n   Enter" \
            " \"exit\" to exit\n\n"
    prompt = "miner_cli: "

    def help_add_node(self):
        print("\nadd_node help:\nAdding new trusted node\nExample: \"add-node 127.0.0.1:5000\"\n")

    def help_mine(self):
        print("\nmine help:\nStart producing blocks\n")

    def help_help(self):
        print("\nhelp help:\nList available commands with \"help\" or detailed help with \"help *command_name*\".\n")
        return True

    def emptyline(self):
        self.do_help(0)

    def do_exit(self, line):
        return True

    def do_add_node(self, line):
        pass

    def do_mine(self, line):
        url = 'http://127.0.0.1:5000/mine'
        resp = requests.post(url=url, json=[''])
        resp = str(resp.json())
        if resp.find('off') > 0:
            print(CRED)
        else:
            print(CGREEN)
        print(resp, CEND)


if __name__ == '__main__':
    WalletCli().cmdloop()