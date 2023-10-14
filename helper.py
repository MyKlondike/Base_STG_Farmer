from web3 import Web3
import time
import random
from data import DATA
from loguru import logger
from config import MAX_GWEI, Base_GWEI


def select_chain(chain) -> str:
    selected_chain = chain.lower()
    if selected_chain in DATA:
        return DATA[selected_chain]

def process_wallet(private_key, chain):
    w3 = Web3(Web3.HTTPProvider(select_chain(chain)['rpc']))
    address = w3.eth.account.from_key(private_key).address
    logger.info(f"В обработке кошелек: {address}")
    return address


def base_gas():
    try:
        w3 = Web3(Web3.HTTPProvider(DATA['base']['rpc']))
        gas_price = w3.eth.gas_price
        gwei_gas_price = w3.from_wei(gas_price, 'gwei')
        return gwei_gas_price
    except Exception as error:
        logger.error(error)
        return base_gas()


def eth_gas():
    try:
        w3 = Web3(Web3.HTTPProvider(DATA['ethereum']['rpc']))
        gas_price = w3.eth.gas_price
        gwei_gas_price = w3.from_wei(gas_price, 'gwei')
        return gwei_gas_price
    except Exception as error:
        logger.error(error)
        return eth_gas()


def wait_eth_gas():
    logger.info(f'Сheck ETH gas')
    while True:
        current_gas = eth_gas()
        if current_gas > MAX_GWEI:
            logger.info(f'current_gas : {current_gas} > {MAX_GWEI} Жду понижения...')
            time.sleep(30)
        else:
            logger.info(f'ETH gas: {current_gas} Gwei')
            break


def wait_base_gas():
    while True:
        current_gas = base_gas()
        if current_gas > Base_GWEI:
            logger.info(f'Base gas price: {current_gas} Gwei > {Base_GWEI} Жду понижения...')
            time.sleep(60)
        else:
            logger.info(f'Base gas price: {current_gas} Gwei. Отправляю транзакцию')
            break


def eth_balance(private_key: str, chain: str) -> int:
    rpc_url = select_chain(chain)['rpc']  # определение rpc_url
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    address = w3.eth.account.from_key(private_key).address
    balance = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance, 'ether')

    return balance_eth

def transaction_retry (tx_hash, current_retry, chain):
    w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
    try:
        transaction_receipt = w3.eth.get_transaction_receipt(tx_hash)

        if transaction_receipt and 'status' in transaction_receipt:
            if transaction_receipt['status'] == 1:
                print(f"Transaction : https://basescan.org/tx/{tx_hash}")
                return True
            else:
                print(f"Ошибка во время попытки {current_retry}.")
                sleep = random.randint(10, 15)
                print(f"Попробую еще раз через {sleep} сек.")
                time.sleep(sleep)
                current_retry += 1
        else:
            print("Невозможно получить информацию о транзакции. Проверьте статус вручную.")
        return False
    except Exception as error:
        logger.error(error)
        return False
