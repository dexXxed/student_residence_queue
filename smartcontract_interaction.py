import json
import os

import base58
import requests
from dotenv import load_dotenv
from eth_account import Account
from transliterate import translit
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware

load_dotenv()


class MetaLogin:
    def __init__(self, str_access):
        self.contract, self.w3 = self.login(os.getenv(str_access))

    def get_abi(self):
        with open("abi.json", "r") as abi_file:
            abi = json.load(abi_file)
            return abi

    def login(self, private_key):
        account = Account.from_key(private_key)

        w3 = Web3(Web3.WebsocketProvider(os.getenv("INFURA_URL")))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
        w3.eth.default_account = account.address

        contract = w3.eth.contract(
            address=Web3.toChecksumAddress(os.getenv("CONTRACT_ADDRESS")), abi=self.get_abi()
        )
        return contract, w3


class User(MetaLogin):
    def __init__(self, str_access="PRIVATE_ETH_BOT_ADDRESS"):
        super().__init__(str_access)

    @staticmethod
    def convert_ipfs_bytes32(hash_string):
        bytes_array = base58.b58decode(hash_string)
        return bytes_array[2:]

    def create_record(self, filename, first_name, second_name, third_name, benefits):
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": os.getenv("PINATA_API_KEY"),
            "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
        }
        files = {"file": open(filename, "rb")}
        response = requests.post(url, files=files, headers=headers, verify=False)

        asset_ipfs_hash = json.loads(response.content)["IpfsHash"]

        tx_hash = self.contract.functions.createNode(
            translit(first_name, "uk"),
            translit(second_name, "uk"),
            translit(third_name, "uk"),
            benefits,
            asset_ipfs_hash
        ).transact({'from': os.getenv('PUBLIC_ETH_BOT_ADDRESS')})

        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(receipt['transactionHash'].hex())

    def queue_benefits_pub(self, identification):
        tx_hash = self.contract.functions.queue_benefits_pub(
            identification
        ).call({'from': os.getenv('PUBLIC_ETH_BOT_ADDRESS')})

        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(receipt['transactionHash'].hex())

    def queue_pub(self):
        tx_hash = self.contract.functions.queue_pub().call({'from': os.getenv('PUBLIC_ETH_BOT_ADDRESS')})

        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(receipt['transactionHash'].hex())

    def queue_count(self):
        tx_hash = self.contract.functions.queue_count().call({'from': os.getenv('PUBLIC_ETH_BOT_ADDRESS')})

        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(receipt['transactionHash'].hex())

    def queue_count_benefits(self):
        tx_hash = self.contract.functions.queue_count_benefits().call({'from': os.getenv('PUBLIC_ETH_BOT_ADDRESS')})

        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(receipt['transactionHash'].hex())


class Admin(MetaLogin):
    def __init__(self, str_access="PRIVATE_ADMIN_ETH_BOT_ADDRESS"):
        super().__init__(str_access)

    def get_student_from_queue(self, identification):
        tx_hash = self.contract.functions.getStudentFromQueue(
            identification
        ).transact({'from': os.getenv('PUBLIC_ADMIN_ETH_BOT_ADDRESS')})

        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(receipt['transactionHash'].hex())
        print(receipt)

    def get_student_from_queue_benefits(self, identification):
        tx_hash = self.contract.functions.getStudentFromQueueBenefits(
            identification
        ).transact({'from': os.getenv('PUBLIC_ADMIN_ETH_BOT_ADDRESS')})

        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(receipt['transactionHash'].hex())
        print(receipt)

    def toggle_completed_node(self, identification, room_number, queue):
        tx_hash = self.contract.functions.toffleCompletedNode(
            identification, room_number, queue
        ).transact({'from': os.getenv('PUBLIC_ADMIN_ETH_BOT_ADDRESS')})

        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print(receipt['transactionHash'].hex())
        print(receipt)


if __name__ == '__main__':
    user = User()
    user.queue_benefits_pub(0)
    # c_user, w_user = login(os.getenv("PRIVATE_ETH_BOT_ADDRESS"))
    # c_admin, w_admin = login(os.getenv("PRIVATE_ADMIN_ETH_BOT_ADDRESS"))
    # # create_record("files/1.rar", "Роман", "Вихристюк", "Сергійович", True, c_user, w_user)
    # get_student_from_queue_benefits(0, c_admin, w_admin)
