import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
import pancakeabi
import functionhash
import logzero
from logzero import logger

## https://ethereum.stackexchange.com/questions/102063/understand-price-impact-and-liquidity-in-pancakeswap
logzero.logfile("./debug.log")
rpc = 'https://bsc.getblock.io/b45294ad-7b89-4e5e-a3e4-26aadc86126e/mainnet/'
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
        logger.info("不符合计算规则")
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

        logger.info("输入数量：" + str(amountIn))
        amountInWithFee = amountIn * 0.9975
        # print("Amount In：" + str(amountIn))
        # print("Amount In with fee:" + str(amountInWithFee))
        initK = _rA * _rB
        # print("initK :" + str(initK))
        rB_ = initK / (_rA + amountInWithFee)
        # print("rb after :" + str(rB_))
        amountOut = _rB - rB_
        # print("amount out:" + str(amountOut))
        marketPrice = amountInWithFee / amountOut
        # print("market price :" + str(marketPrice))
        midPrice = _rA / _rB
        # print("mid price :" + str(midPrice))
        priceImpact = 1 - (midPrice / marketPrice)
        # print("price impact :" + str(priceImpact))

        logger.warning("交易前价格:" + str(midPrice)
                       + "交易后价格：" + str(marketPrice)
                       + "价格影响比例：" + str(int(priceImpact * 100000) / 1000) + "%")

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
    print(bsc.eth.get_block_number())
    pendingList = pending.get_new_entries()
    print(len(pendingList))
    ##print(pendingList)
    for i in pendingList:
        try:
            detail = bsc.eth.get_transaction(i.hex())
            if detail['to'] == '0x10ED43C718714eb63d5aA57B78B54704E256024E':
                if detail['input'][0:10] in functionhash.functionHash:
                    # 这里解析出来后的类型为tuple
                    readableInput = routerContract.decode_function_input(detail['input'])[1]
                    # print(readableInput)
                    logger.info("检测到一条交易：" + i.hex())
                    calculate(readableInput['path'], readableInput['amountIn'])
                    break
        except Exception as e:
            print("a error occurred")
            print(e)
            time.sleep(0.1)
    time.sleep(1)
