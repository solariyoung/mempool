
import time

from web3 import Web3
from web3.middleware import geth_poa_middleware
import web3.geth

import pancakeabi

rpc = 'https://bsc-mainnet.rpcfast.com?api_key=aAlSFtiap9XQpEU7R0i7H8xUuxzPMl6iQ0c5DMr2zy8QbSaubjWphRXmqzVIdi8V'
bsc = Web3(Web3.HTTPProvider(rpc))
bsc.middleware_onion.inject(geth_poa_middleware, layer=0)

while not bsc.isConnected():
    print(bsc.isConnected())
    time.sleep(1)

router = bsc.toChecksumAddress('0x10ED43C718714eb63d5aA57B78B54704E256024E')
router_contract = bsc.eth.contract(router, abi=pancakeabi.abi)

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
                    print(router_contract.decode_function_input(detail['input']))
        except:
            print("a error occured")
            time.sleep(0.1)

    time.sleep(1)