import os
from dotenv import load_dotenv
from src.utils.files import load_json, decrypt_json
load_dotenv()

TAG = "test"
HIDE = False # Hide secret data in console. Log file will contain secret data anyway

class Params:
    name = 'test'
    path_to_data = f'./program_data/{TAG}/{name}/data.json'
    private_key = os.getenv('PRIVATE_KEY')

    # user_agent = None
    proxy = None

    def load(self, password):
        secret_data = decrypt_json(f'./program_data/{TAG}/{self.name}/edata.json', password)
        # data = load_json(f'./program_data/{TAG}/{self.name}/data.json')
        self.private_key = secret_data['evm']['private_key']
        self.proxy = secret_data['proxy']['http']
        # self.user_agent = data['user_agent']

class Params_KodoExchange(Params):

    """
    Swaps tokens via Kodo Exchange on Taiko Network
    App: https://app.kodo.exchange/
    Docs: https://docs.kodo.exchange/overview
    Chains: Taiko

    ETH: ''
    WETH: 0xA51894664A773981C6C112C43ce576f315d5b1B6
    USDC: 0x07d83526730c7438048D55A4fc0b850e2aaB6f0b
    USDT: 0x2DEF195713CF4a606B49D07E520e22C17899a736
    KODO: 0x7e91F29F8a213c8311712A8FC8c61219fb9477CB
    LRC: 0xd347949F8C85d9f3d6B06bfc4F8c2E07c161f064
    TAIKO: 0xA9d23408b9bA935c230493c40C73824Df71A0975
    USDC.e: 0x19e26B0638bf63aa9fa4d14c6baF8D52eBE86C5C
    rETH: 0x473C58b748156D3249cA31Baa3cAd9781EB6d97e
    """

    def __init__(self) -> None:
        super().__init__()

    # ETH (or native tokens) have null address => ''
    from_token_address = '0x19e26B0638bf63aa9fa4d14c6baF8D52eBE86C5C'
    to_token_address = '0x07d83526730c7438048D55A4fc0b850e2aaB6f0b'
    
    # Recommended to use 0.0001 minimum, because transaction notcreation if the amount is too low (less than 0.0001)
    amount_from = 839 # Swap from a certain amount of coins
    amount_to = 839.4 # Swap up to a certain amount of coins

    swap_all_balance = True # Swap all balance
    keep_value_from = 0 # How many coins to keep on the wallet (only works when: swap_all_balance = True)
    keep_value_to = 0 # Up to how many coins to keep on the wallet (only works when: swap_all_balance = True)

    keep_value_gas_from = 0.0002 # How many coins to keep for gas fees
    keep_value_gas_to = 0.0003 # Up to how many coins to keep for gas fees

    slippage = 1 # Slippage in