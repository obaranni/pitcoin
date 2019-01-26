import cmd
import requests

status_codes = {
    "Transaction pull i empty": 101,
    "Transaction pended": 201,
    "Bad json format": 401,
    "Bad transaction": 402,
}


class WalletCli(cmd.Cmd):
    intro = "\n\n   Welcome to the miner command line interface!\n" \
            "   Enter \"help\" to get the list of commands.\n   Enter" \
            " \"exit\" to exit\n\n"
    prompt = "wallet_cli: "

    def help_new(self):
        print("\nnew help:\nCreates a new key pair\n")

    def help_help(self):
        print("\nhelp help:\nList available commands with \"help\" or detailed help with \"help *command_name*\".\n")
        return True

    def emptyline(self):
        self.do_help(0)

    def do_exit(self, line):
        return True

    def do_new(self, line):
        private_key, public_key, address = wallet_utils.newKeyPair()
        PRIVATE_KEYS.append(private_key)
        wallet_utils.saveKeyToFile(address)
        print_keys_info(private_key)


def print_keys_info(private_key):
    print("Private key: \"", private_key, "\"", sep="")
    print("Look for your public key at storage/address.txt line %d" % int(wallet_utils.getFileLines()))


if __name__ == '__main__':
    WalletCli().cmdloop()