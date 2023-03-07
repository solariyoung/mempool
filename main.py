import time

from web3 import Web3
from web3.middleware import geth_poa_middleware

import pancakeabi
import functionhash

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


def calculate(tokenPath, amountIn):
    if len(tokenPath) > 2:
        return False
    else:
        tokenPair = factoryContract.functions.getPair(
            bsc.toChecksumAddress(tokenPath[0]),
            bsc.toChecksumAddress(tokenPath[1])
        ).call()
        pairContract = bsc.eth.contract(tokenPair, abi=pancakeabi.pairAbi)
        r = pairContract.functions.getReserves().call()
        token0 = pairContract.functions.token0().call()
        if token0 != tokenPath[0]:
            reserve = [r[1], r[0]]
        else:
            reserve = r[0:2]

        _rA = reserve[0]
        _rB = reserve[1]
        print(_rA)
        print(_rB)

        amountInWithFee = amountIn * 0.9975
        print("Amount In：" + str(amountIn))
        print("Amount In with fee:" + str(amountInWithFee))
        initK = _rA * _rB
        print("initK :" + str(initK))
        rB_ = initK / (_rA + amountInWithFee)
        print("rb after :" + str(rB_))
        amountOut = _rB - rB_
        print("amount out:" + str(amountOut))
        marketPrice = amountInWithFee / amountOut
        print("market price :" + str(marketPrice))
        midPrice = _rA / _rB
        print("mid price :" + str(midPrice))
        priceImpact = 1 - (midPrice / marketPrice)
        print("price impact :" + str(priceImpact))

        return tokenPair


# 临时测试代码
'''
result = calculate([bsc.toChecksumAddress('0x55d398326f99059ff775485246999027b3197955'),
                    bsc.toChecksumAddress('0x42414624c55a9cba80789f47c8f9828a7974e40f'), ],
                   100000121014210120101021)

exit(110)
'''
pending = bsc.eth.filter('pending')

while 1:
    pendingList = pending.get_new_entries()
    ##print(pendingList)
    for i in pendingList:
        try:
            detail = bsc.eth.get_transaction(i.hex())
            if detail['to'] == '0x10ED43C718714eb63d5aA57B78B54704E256024E':
                if detail['input'][0:10] in functionhash.functionHash:
                    print(detail['input'])
                    print(routerContract.decode_function_input(detail['input']))
        except Exception as e:
            print("a error occurred")
            print(e)
            time.sleep(0.1)

    time.sleep(1)
