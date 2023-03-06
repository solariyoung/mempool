
import time

from web3 import Web3
from web3.middleware import geth_poa_middleware

import pancakeabi
import dip
## https://ethereum.stackexchange.com/questions/102063/understand-price-impact-and-liquidity-in-pancakeswap

rpc = 'https://bsc-mainnet.rpcfast.com?api_key=aAlSFtiap9XQpEU7R0i7H8xUuxzPMl6iQ0c5DMr2zy8QbSaubjWphRXmqzVIdi8V'
bsc = Web3(Web3.HTTPProvider(rpc))
bsc.middleware_onion.inject(geth_poa_middleware, layer=0)

while not bsc.isConnected():
    print(bsc.isConnected())
    time.sleep(0.1)

pancakeRouter = bsc.toChecksumAddress('0x10ED43C718714eb63d5aA57B78B54704E256024E')
routerContract = bsc.eth.contract(pancakeRouter, abi=pancakeabi.routerAbi)
pancakeFactory = bsc.toChecksumAddress('0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73')
factoryContract = bsc.eth.contract(pancakeFactory, abi=pancakeabi.factoryAbi)


def calculate(tokenPath, amount):
    if len(tokenPath) > 2:
        return False
    else:
        tokenPair = factoryContract.functions.getPair(
            bsc.toChecksumAddress(tokenPath[0]),
            bsc.toChecksumAddress(tokenPath[1])
        ).call()
        return tokenPair

## 临时测试代码
result = calculate(['0x42414624c55a9cba80789f47c8f9828a7974e40f','0x55d398326f99059ff775485246999027b3197955'],1)
print(result)
exit(110)

pending = bsc.eth.filter('pending')

while 1:
    pendingList = pending.get_new_entries()
    ##print(pendingList)
    for i in pendingList:
        try:
            detail = bsc.eth.get_transaction(i.hex())
            if detail['to'] == '0x10ED43C718714eb63d5aA57B78B54704E256024E':
                if detail['input'][0:10] == "0x38ed1739":
                    print(detail['input'])
                    print(routerContract.decode_function_input(detail['input']))
        except:
            print("a error occurred")
            time.sleep(0.1)

    time.sleep(1)