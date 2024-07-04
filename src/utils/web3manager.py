from . import console
from .proxy import check_proxy
from src.data.data import CHAINS
from src.data.abi import ERC721_ABI, ERC20_ABI
from src.utils.tools import int_to_decimal, decimal_to_int, get_decimal_places

from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import random
import time
import asyncio


max_time_check_tx_status = 240

class Web3Manager:

    BSC_GAS_PRICE = 1000000000

    def __init__(self, private_key, chain: str, proxy: str = None):
        """
        Initialize Web3Manager

        :param private_key: str: Private key of the wallet
        :param chain: str: Chain name
        :param proxy: str: Proxy address: http://username:password@ip:port. Default is None
        """
        self.private_key = private_key
        self.chain = chain
        self.chain_id = self._get_chain_id()
        self.web3 = self._initilize_web3(chain, proxy)

    def _initilize_web3(self, chain: str, proxy: dict):
        rpc = CHAINS[chain]['rpc']
        if proxy is not None:
            if not check_proxy(proxy):
                console.clog(f"Proxy is not working", 'red')
                raise Exception("Proxy is not working")
            web3 = Web3(AsyncHTTPProvider(rpc, request_kwargs={"proxy": proxy}), modules={"eth": (AsyncEth)}, middlewares=[])
            console.clog(f'Connected to Web3 using proxy', 'green') 
        else:

            web3 = Web3(AsyncHTTPProvider(rpc), modules={'eth': (AsyncEth)}, middlewares=[])
            console.clog(f'Connected to Web3 without proxy', 'red')
        return web3
    
    def _get_chain_id(self):
        return CHAINS[self.chain]['chain_id']
    
    async def add_gas_limit(self, contract_txn) -> dict:
        value = contract_txn['value']
        contract_txn['value'] = 0
        gasLimit = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gasLimit * random.uniform(1.02, 1.05))

        contract_txn['value'] = value
        return contract_txn
    
    async def add_gas_limit_layerzero(self, contract_txn) -> dict:
        pluser = [1.05, 1.07]
        gasLimit = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
        return contract_txn

    async def add_gas_price(self, contract_txn) -> dict:
        if self.chain == 'bsc':
            contract_txn['gasPrice'] = self.BSC_GAS_PRICE 
        else:
            gas_price = await self.web3.eth.gas_price
            contract_txn['gasPrice'] = int(gas_price * random.uniform(1.01, 1.02))
        return contract_txn

    async def get_status(self, tx_hash: str):
        start_time_stamp = int(time.time())

        while True:
            try:
                receipt = await self.web3.eth.get_transaction_receipt(tx_hash)
                status = receipt["status"]
                if status in [0, 1]:
                    return status
            except:
                time_stamp = int(time.time())
                if time_stamp - start_time_stamp > max_time_check_tx_status:
                    console.clog(f'Did not receive tx_status for {max_time_check_tx_status} sec, assuming that tx is a success', 'red')
                    return 1
                await asyncio.sleep(1)

    async def send_tx(self, tx: dict):
        try:
            if tx['value'] >= 0:
                signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
                tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                console.seclog(f"Transaction sent. Tx: {CHAINS[self.chain]['scan']}/{tx_hash.hex()}", tx_hash.hex())
                status = await self.get_status(tx_hash.hex())
                if status == 1:
                    console.clog(f"Transaction is successful", 'green')
                else:
                    console.clog(f"Transaction is failed", 'red')  
                return status, tx_hash.hex()
        except Exception as e:
            console.clog(f"Error: {e}", 'red')
            return 0, None
                
    def balance_of_erc721(self, address, contract_address):
        contract = self.web3.eth.contract(address=self.web3.to_checksum_address(contract_address), abi=ERC721_ABI)
        return contract.functions.balanceOf(address).call()

    async def get_data_token(self, token_address: str):
        try:
            token_contract = self.web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            decimals = await token_contract.functions.decimals().call()
            symbol = await token_contract.functions.symbol().call()
            return token_contract, decimals, symbol
        except Exception as error:
            console.clog(f"Error: {error}", 'red')

    async def get_token_info(self, token_address: str) -> dict:
        if token_address == '': 
            address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
            decimal = 18
            symbol = CHAINS[self.chain]['token']
            token_contract = ''
        else:
            address = Web3.to_checksum_address(token_address)
            token_contract, decimal, symbol = await self.get_data_token(address)

        return {'address': address, 'symbol': symbol, 'decimal': decimal, 'contract': token_contract}

    async def get_allowance(self, token_address: str, spender: str) -> int:
        try:
            contract = self.web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            amount_approved = await contract.functions.allowance(self.public_key, spender).call()
            return amount_approved
        except Exception as error:
            console.clog(f"Error: {error}", 'red')
            return 0

    @property
    def public_key(self):
        return self.web3.eth.account.from_key(self.private_key).address

    async def approve(self, amount: int, token_address: str, spender: str):
        spender = Web3.to_checksum_address(spender)
        token_data = await self.get_token_info(token_address)

        allowance_amount = await self.get_allowance(token_address, spender)
        if amount <= allowance_amount: return 1

        tx = await token_data["contract"].functions.approve(
            spender,
            amount
            ).build_transaction(
            {
                "chainId": self.chain_id,
                "from": self.public_key,
                "nonce": await self.web3.eth.get_transaction_count(self.public_key),
                'gasPrice': 0,
                'gas': 0,
                "value": 0
            }
        )

        tx = await self.add_gas_price(tx)
        tx = await self.add_gas_limit(tx)

        status, tx_hash = await self.send_tx(tx)

        if status == 1:
            console.clog(f"Approved {decimal_to_int(amount, token_data['decimal'])} {token_data['symbol']} to {spender}.", 'green')
            await asyncio.sleep(5)
            return 1
        else:
            console.clog(f"Failed to approve {decimal_to_int(amount, token_data['decimal'])} {token_data['symbol']} to {spender}.", 'red')
            return 0
    
    async def get_amount_in(
            self, amount_from: int | float, 
            amount_to: int | float, address_token: str,
            swap_all_balance: bool, keep_value_from: int | float, keep_value_to: int | float
            ) -> int | float:
        
        def random_round(value, min_decimals, max_decimals):
            """Округлює значення до випадкової кількості десяткових знаків"""
            return round(value, random.randint(min_decimals, max_decimals))

        # Визначаємо мінімальну кількість десяткових знаків для amount і keep_value
        min_amount_decimals = max(1, len(str(amount_from).split('.')[-1]) if '.' in str(amount_from) else 0)
        min_keep_value_decimals = max(1, len(str(keep_value_from).split('.')[-1]) if '.' in str(keep_value_from) else 0)

        if isinstance(amount_from, int) and isinstance(amount_to, int):
            amount = random_round(random.randint(amount_from, amount_to), 0, 4)
        else: 
            amount = random_round(random.uniform(amount_from, amount_to), min_amount_decimals, 9)

        if isinstance(keep_value_from, int) and isinstance(keep_value_to, int):
            keep_value = random_round(random.randint(keep_value_from, keep_value_to), 0, 4)
        else:
            keep_value = random_round(random.uniform(keep_value_from, keep_value_to), min_keep_value_decimals, 9)

        balance_amount = await self.get_balance(address_token)
        

        if swap_all_balance:
            amount = random_round(balance_amount - keep_value, 7, 9)
            if amount < 0:
                amount = 0
            return amount
        
        if address_token == '' and amount > balance_amount:
            amount = random_round(balance_amount - keep_value, 7, 9)
            if amount < amount_from:
                amount = amount_from

        if amount > balance_amount:
            amount = balance_amount 

        return amount


    async def get_balance(self, token_address: str) -> float | int:
        while True:
            try:
                token_data = await self.get_token_info(token_address)
                if token_address == '':
                    balance = await self.web3.eth.get_balance(self.web3.to_checksum_address(self.public_key))
                else:
                    balance = await token_data['contract'].functions.balanceOf(self.web3.to_checksum_address(self.public_key)).call()

                return decimal_to_int(balance, token_data['decimal'])

            except Exception as error:
                console.clog(f"Error getting balance: {error}", 'red')
                await asyncio.sleep(1)

