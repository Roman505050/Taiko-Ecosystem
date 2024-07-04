from src.utils.web3manager import Web3Manager
from src.utils.tools import int_to_decimal
from settings import Params_KodoExchange
from src.data.abi import KODO_EXCHANGE_ABI
from src.data.contracts import WETH_CONTRACTS

from web3 import Web3
import random

class KodoExchange:
    def __init__(self, params: Params_KodoExchange):
        self.contract_address = '0xd04d75E1CDe512b195E70C6c18Cf7Ec4b2B12f41'  # Replace with your contract address
        self.private_key = params.private_key   
        
        # Parameters
        self.from_token_address = params.from_token_address
        self.to_token_address = params.to_token_address
        self.slippage = params.slippage
        self.amount_from = params.amount_from
        self.amount_to = params.amount_to
        self.swap_all_balance = params.swap_all_balance
        self.keep_value_from = params.keep_value_from
        self.keep_value_to = params.keep_value_to
        self.keep_value_gas_from = params.keep_value_gas_from
        self.keep_value_gas_to = params.keep_value_gas_to

        # Initialize Web3 manager
        self.manager = Web3Manager(params.private_key, 'taiko', params.proxy)
    
    async def _calculate_deadline(self):
        latest_block = await self.manager.web3.eth.get_block('latest')
        deadlines = [180, 240, 300, 360, 420, 480, 540, 600]
        return latest_block['timestamp'] + random.randint(
            random.choice(deadlines), 1200
        )

    async def initialize(self):
        # Initialize many things
        self.from_token_info = await self.manager.get_token_info(self.from_token_address)
        self.to_token_info = await self.manager.get_token_info(self.to_token_address)
        self.amount = await self.manager.get_amount_in(
            self.amount_from, self.amount_to,
            self.keep_value_gas_from, self.keep_value_gas_to,
            self.from_token_address, self.swap_all_balance,
            self.keep_value_from, self.keep_value_to
            )
        self.value = int_to_decimal(self.amount, self.from_token_info['decimal'])

    async def get_amounts_out(self, contract, amount_in, routes):
        # Call the getAmountsOut function
        tx = await contract.functions.getAmountsOut(
            amount_in,
            routes
        ).call()
        return int(tx[1] * (1 - self.slippage / 100))
    
    async def get_amount_out(self, contract, amount_in, token_in, token_out) -> tuple[int, bool]:
        # Call the getAmountOut function
        tx = await contract.functions.getAmountOut(
            amount_in,
            token_in,
            token_out
        ).call()
        return tx[0], tx[1]

    async def get_tx(self):
        await self.initialize()

        contract = self.manager.web3.eth.contract(address=self.contract_address, abi=KODO_EXCHANGE_ABI)

        if self.from_token_address != '':
            await self.manager.approve(self.value, self.from_token_address, self.contract_address)

        # WETH >>> Token
        if self.from_token_address == '':
            from_token = Web3.to_checksum_address(WETH_CONTRACTS[self.manager.chain])
            to_token = self.to_token_info['address']
 
            _, stable = await self.get_amount_out(contract, self.value, from_token, to_token)
            
            routes = [{
                'from': from_token,
                'to': to_token,  
                'stable': stable  # Set to True or False based on your needs
            }]
         
            amount_out_min = await self.get_amounts_out(contract, self.value, routes)
            deadline = await self._calculate_deadline()

            tx = await contract.functions.swapExactETHForTokens(
                self.manager.web3.to_int(amount_out_min),
                routes,
                self.manager.public_key,
                deadline
            ).build_transaction({
                'from': self.manager.public_key,
                'value': self.value, 
                'gas': 0, 
                'gasPrice':0,  
                'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.public_key)
            })
        
        # Token >>> WETH
        if self.to_token_address == '':
            from_token = self.from_token_info['address']
            to_token = Web3.to_checksum_address(WETH_CONTRACTS[self.manager.chain])

            _, stable = await self.get_amount_out(contract, self.value, from_token, to_token)

            routes = [{
                'from': from_token,
                'to': to_token,  
                'stable': stable  # Set to True or False based on your needs
            }]

            amount_out_min = await self.get_amounts_out(contract, self.value, routes)
            deadline = await self._calculate_deadline()

            tx = await contract.functions.swapExactTokensForETH(
                self.manager.web3.to_int(self.value),
                amount_out_min,
                routes,
                self.manager.public_key,
                deadline
            ).build_transaction({
                'from': self.manager.public_key,
                'value': 0, 
                'gas': 0, 
                'gasPrice':0,  
                'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.public_key)
            })
        
        # Tokens >>> Tokens
        if self.from_token_address != '' and self.to_token_address != '' and self.from_token_address not in [
            '0x19e26B0638bf63aa9fa4d14c6baF8D52eBE86C5C'
            ]:
            from_token = self.from_token_info['address']
            to_token = self.to_token_info['address']

            _, stable = await self.get_amount_out(contract, self.value, from_token, to_token)

            routes = [{
                'from': from_token,
                'to': to_token,  
                'stable': stable  # Set to True or False based on your needs
            }]

            amount_out_min = await self.get_amounts_out(contract, self.value, routes)
            deadline = await self._calculate_deadline()

            tx = await contract.functions.swapExactTokensForTokens(
                self.manager.web3.to_int(self.value),
                amount_out_min,
                routes,
                self.manager.public_key,
                deadline
            ).build_transaction({
                'from': self.manager.public_key,
                'value': 0, 
                'gas': 0, 
                'gasPrice':0,  
                'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.public_key)
            })
        
        # Tokens >>> Tokens SIMPLE
        if self.from_token_address != '' and self.to_token_address != '' and self.from_token_address in [
            '0x19e26B0638bf63aa9fa4d14c6baF8D52eBE86C5C'
            ]:
            from_token = self.from_token_info['address']
            to_token = self.to_token_info['address']

            _, stable = await self.get_amount_out(contract, self.value, from_token, to_token)

            routes = [{
                'from': from_token,
                'to': to_token,  
                'stable': stable  # Set to True or False based on your needs
            }]

            amount_out_min = await self.get_amounts_out(contract, self.value, routes)
            deadline = await self._calculate_deadline()

            tx = await contract.functions.swapExactTokensForTokensSimple(
                self.manager.web3.to_int(self.value),
                amount_out_min,
                from_token,
                to_token,
                stable,
                self.manager.public_key,
                deadline
            ).build_transaction({
                'from': self.manager.public_key,
                'value': 0, 
                'gas': 0, 
                'gasPrice':0,  
                'nonce': await self.manager.web3.eth.get_transaction_count(self.manager.public_key)
            })

        tx = await self.manager.add_gas_price(tx)
        tx = await self.manager.add_gas_limit_layerzero(tx)
            
        return tx, None
        
            

