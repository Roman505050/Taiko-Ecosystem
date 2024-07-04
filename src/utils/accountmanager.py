from src.data.data import CHAINS
from .proxy import check_proxy
from .files import encrypt_json, load_json, save_json, decrypt_json

import os
from web3 import Web3
from web3 import HTTPProvider
import getpass
import shutil

class AccountManager:
    def __init__(self, tag: str = "default"):
        if not self.if_folder_exists(tag):
            print("Tag does not exist. Creating a new tag")
            self.create_folder(tag)
        self.path = f"./program_data/{tag}/"
        
    def load_all_folders(self, path: str = "./program_data"):
        return os.listdir(f"{path}/")
    
    def if_folder_exists(self, name: str, path: str = "./program_data"):
        return name in self.load_all_folders(f"{path}/")
    
    def create_folder(self, name: str, path: str = "./program_data"):
        os.makedirs(f"{path}/{name}")

    def input_data(self):
        private_data = {
            "evm": {
                "private_key": None,
            },
            "proxy": None
        }
        print("Starting creating a new account...")
        print("For stop creating account press enter 'cancel'")
        while True:
            name = input("Enter the name of the account: ")
            if name == "cancel":
                return None, None, None
            if name == "":
                print("Invalid name. Please enter a valid name")
                continue 
            if not self.if_folder_exists(name, self.path):
                self.create_folder(name, self.path)
                break
            else:
                print("Account already exists. Please enter a new name")
        while True:
            print("Format: http://user:pass@ip:port")
            proxy = input("Enter the proxy or None: ")
            if proxy == "cancel":
                return None, None, None
            if proxy.lower() == "none":
                proxy_dict = {
                    'http': None,
                    'https': None
                }
                break
            if check_proxy(proxy):
                proxy_dict = {
                    'http': proxy,
                    'https': proxy
                }
                break
            else:
                print("Invalid proxy. Please enter a valid proxy")
        while True:
            private_key = input("Enter the private key: ")
            if private_key == "cancel":
                return None, None, None
            # if len(private_key) == 64:
            if proxy_dict["http"] is not None:
                w3 = Web3(HTTPProvider(CHAINS["bsc"]["rpc"], request_kwargs={"proxy": proxy_dict["http"]}))
            else:
                w3 = Web3(HTTPProvider(CHAINS["bsc"]["rpc"]))
            print(f"Your address is: {w3.eth.account.from_key(private_key).address}")
            break
            # else:
            #     print("Invalid private key. Please enter a valid private key")
        while True:
            password = getpass.getpass("Enter the password: ")
            password_confirm = getpass.getpass("Confirm the password: ")
            if password == "cancel" or password_confirm == "cancel":
                return None, None, None
            if password == password_confirm:
                break
            else:
                print("Passwords do not match. Please enter the same password")
        private_data["proxy"] = proxy_dict
        private_data["evm"]["private_key"] = private_key
        return private_data, name, password
    
    def run(self):
        while True:
            # Clear console
            os.system('cls' if os.name == 'nt' else 'clear')

            print("1. Add Account")
            print("2. List Accounts")
            print("3. Delete Account")
            print("4. Edit Proxy")
            print("0. Exit")
            print()

            input_option = input("Select an option: ")

            if input_option == "0":
                exit(1)
            
            if input_option == "1":
                data, name, password = self.input_data()
                if data is None:
                    continue
                encrypt_json(f"{self.path}{name}/edata.json", data, password)
                template_data = load_json("./program_data_EXAMPLE/template.json")
                save_json(f"{self.path}{name}/data.json", template_data)
                print("Account added successfully")
                input("Press Enter to continue...")
            
            if input_option == "2":
                print("Accounts:")
                for folder in self.load_all_folders(self.path):
                    print(folder)
                input("Press Enter to continue...")
            
            if input_option == "3":
                print("Deleting an account...")
                print("For stop deleting account press enter 'cancel'")
                name = input("Enter the name of the account: ")
                if name == "cancel":
                    continue
                if self.if_folder_exists(name, self.path):
                    shutil.rmtree(f"{self.path}{name}")
                    print("Account deleted successfully")
                else:
                    print("Account does not exist")
                input("Press Enter to continue...")
            
            if input_option == "4":
                print("Editing proxy...")
                print("For stop editing proxy press enter 'cancel'")
                name = input("Enter the name of the account: ")
                if name == "cancel":
                    continue
                if self.if_folder_exists(name, self.path):
                    while True:
                        password = getpass.getpass("Enter the password: ")
                        if password == "cancel":
                            break
                        try:
                            data = decrypt_json(f"{self.path}{name}/edata.json", password)
                            break
                        except:
                            print("Invalid password. Please enter a valid password")
                    if password == "cancel":
                        continue
                    print("Format: http://user:pass@ip:port")
                    print(f"Current proxy: {data['proxy']['http']}")
                    while True:
                        proxy = input("Enter the new proxy or None: ")
                        if proxy == "cancel":
                            break
                        if proxy.lower() == "none":
                            data['proxy'] = {
                                'http': None,
                                'https': None
                            }
                            break
                        else:
                            if check_proxy(proxy):
                                data['proxy'] = {
                                    'http': proxy,
                                    'https': proxy
                                }
                                break
                            else:
                                print("Invalid proxy. Please enter a valid proxy")
                                continue
                    if proxy == "cancel":
                        continue
                    encrypt_json(f"{self.path}{name}/edata.json", data, password)
                    print("Proxy edited successfully")
                    input("Press Enter to continue...")
    


