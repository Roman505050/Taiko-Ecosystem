from src.utils.web3manager import Web3Manager
from src.utils.tools import int_to_decimal
from settings import Params_ETHWraps
from src.data.abi import WETH_ABI
from src.data.contracts import WETH_CONTRACTS


class ETHWraps:
    def __init__(self, params: Params_ETHWraps):
        self.contract_address = WETH_CONTRACTS[params.chain]
        self.private_key = params.private_key   
        
        # Parameters
        self.from_token_address = '' if params.from_token_address == 'ETH' else WETH_CONTRACTS[params.chain]
        self.to_token_address = '' if params.to_token_address == 'ETH' else WETH_CONTRACTS[params.chain]
        self.amount_from = params.amount_from
        self.amount_to = params.amount_to
        self.wrap_all_balance = params.wrap_all_balance
        self.keep_value_from = params.keep_value_from
        self.keep_value_to = params.keep_value_to

        # Initialize Web3 manager
        self.manager = Web3Manager(params.private_key, params.chain, params.proxy)
    
    async def initialize(self):
        # Initialize many things
        self.from_token_info = await self.manager.get_token_info(self.from_token_address)
        self.to_token_info = await self.manager.get_token_info(self.to_token_address)
        self.amount = await self.manager.get_amount_in(
            self.amount_from, self.amount_to,
            self.from_token_address, self.wrap_all_balance,
            self.keep_value_from, self.keep_value_to
            )
        self.value = int_to_decimal(self.amount, self.from_token_info['decimal'])
    
    async def get_tx(self):
        await self.initialize()
    
        if self.value == 0:
            return None, 'The amount is too low'

        contract = self.manager.web3.eth.contract(address=self.contract_address, abi=WETH_ABI)

        # ETH >>> WETH
        if self.from_token_address == '':
            tx = await contract.functions.deposit().build_transaction({
                'value': self.value,
                'from': self.manager.public_key,
                'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.public_key),
                'gas': 0,
                'gasPrice': 0
            })
        
        # WETH >>> ETH
        elif self.to_token_address == '':
            tx = await contract.functions.withdraw(self.value).build_transaction({
                'from': self.manager.public_key,
                'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.public_key),
                'gas': 0,
                'gasPrice': 0
            })
        
        tx = await self.manager.add_gas_price(tx)
        tx = await self.manager.add_gas_limit_layerzero(tx)

        return tx, None
