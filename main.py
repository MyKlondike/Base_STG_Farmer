from web3 import Web3
import time
import random
import sys
from data import DATA
from utils import WALLETS
from abi import ABI_RouterETH, ABI_Ether_VaultLP, ABI_LPStakingTime, ABI_Router_base
from config import pool_amount, retries, delay, action
from contract import RouterETH_base, Ether_VaultLP_base, LPStakingTime_base, Router_base
from loguru import logger
from decimal import Decimal
from helper import process_wallet, wait_eth_gas, eth_balance, transaction_retry, wait_base_gas


chain = 'base'
rpc_url = DATA[chain]['rpc']


def addLiquidityETH(private_key: str, chain: str) -> str:
    current_retry = 0
    while current_retry < retries:
        try:
            w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
            address = w3.eth.account.from_key(private_key).address
            contract_address = w3.to_checksum_address(RouterETH_base)
            nonce = w3.eth.get_transaction_count(address)
            amount = Decimal(pool_amount)
            contract_instance = w3.eth.contract(address=contract_address, abi=ABI_RouterETH)
            value = int(amount * Decimal("1e18"))

            gas = contract_instance.functions.addLiquidityETH().estimate_gas(
                {'from': address, 'nonce': nonce, 'value': value})

            tx = {
                'chainId': DATA[chain]['chain_id'],
                'from': address,
                'value': value,
                'gas': gas,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
                 }

            transaction = contract_instance.functions.addLiquidityETH().build_transaction(tx)
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
            time.sleep(10)
            if transaction_retry(tx_hash, current_retry, chain):
                break
        except Exception as error:
            logger.error(error)


def check_lpBalance(private_key: str, chain: str) -> int:
    try:
        w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
        address = w3.eth.account.from_key(private_key).address
        contract_address = w3.to_checksum_address(Ether_VaultLP_base)
        contract_instance = w3.eth.contract(address=contract_address, abi=ABI_Ether_VaultLP)
        lp_balance = contract_instance.functions.balanceOf(Web3.to_checksum_address(address)).call()

        return lp_balance
    except Exception as e:
        print(f"Ошибка при проверке баланса lp: {str(e)}")
        return None


def check_farmLP (private_key: str, chain: str) -> tuple:
    try:
        w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
        address = w3.eth.account.from_key(private_key).address
        contract_address = w3.to_checksum_address(LPStakingTime_base)
        contract_instance = w3.eth.contract(address=contract_address, abi=ABI_LPStakingTime)
        info = contract_instance.functions.userInfo(0, Web3.to_checksum_address(address)).call()
        return tuple(info)
    except Exception as e:
        print(f"Ошибка при проверке баланса farmLP: {str(e)}")
        return None


def approve(private_key: str, chain: str) -> str:
    current_retry = 0
    while current_retry < retries:
        try:
            w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
            address = w3.eth.account.from_key(private_key).address
            contract_address = w3.to_checksum_address(Ether_VaultLP_base)
            nonce = w3.eth.get_transaction_count(address)
            contract_instance = w3.eth.contract(address=contract_address, abi=ABI_Ether_VaultLP)
            spender = w3.to_checksum_address(LPStakingTime_base)
            amount = check_lpBalance(private_key, chain)

            gas = contract_instance.functions.approve(spender, amount).estimate_gas(
                {'from': address, 'nonce': nonce})

            tx = {
                'chainId': DATA[chain]['chain_id'],
                'from': address,
                'value': 0,
                'gas': gas,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            }

            transaction = contract_instance.functions.approve(spender, amount).build_transaction(tx)
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
            time.sleep(10)
            if transaction_retry(tx_hash, current_retry, chain):
                break
        except Exception as error:
            logger.error(error)


def deposit(private_key: str, chain: str) -> str:
    current_retry = 0
    while current_retry < retries:
        try:
            w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
            address = w3.eth.account.from_key(private_key).address
            contract_address = w3.to_checksum_address(LPStakingTime_base)
            nonce = w3.eth.get_transaction_count(address)
            amount = check_lpBalance(private_key, chain)
            pid = 0

            contract_instance = w3.eth.contract(address=contract_address, abi=ABI_LPStakingTime)

            gas = contract_instance.functions.deposit(pid, amount).estimate_gas(
                {'from': address, 'nonce': nonce})

            tx = {
                'chainId': DATA[chain]['chain_id'],
                'from': address,
                'value': 0,
                'gas': gas,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
                 }

            transaction = contract_instance.functions.deposit(pid, amount).build_transaction(tx)
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
            time.sleep(10)
            if transaction_retry(tx_hash, current_retry, chain):
                break
        except Exception as error:
            logger.error(error)


def claim(private_key: str, chain: str) -> str:
    current_retry = 0
    while current_retry < retries:
        try:
            w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
            address = w3.eth.account.from_key(private_key).address
            contract_address = w3.to_checksum_address(LPStakingTime_base)
            nonce = w3.eth.get_transaction_count(address)
            amount = 0
            pid = 0

            contract_instance = w3.eth.contract(address=contract_address, abi=ABI_LPStakingTime)

            gas = contract_instance.functions.deposit(pid, amount).estimate_gas(
                {'from': address, 'nonce': nonce})

            tx = {
                'chainId': DATA[chain]['chain_id'],
                'from': address,
                'value': 0,
                'gas': gas,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
                 }

            transaction = contract_instance.functions.deposit(pid, amount).build_transaction(tx)
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
            time.sleep(10)
            if transaction_retry(tx_hash, current_retry, chain):
                break
        except Exception as error:
            logger.error(error)


def withdraw(private_key: str, chain: str) -> str:
    current_retry = 0
    while current_retry < retries:
        try:
            w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
            address = w3.eth.account.from_key(private_key).address
            contract_address = w3.to_checksum_address(LPStakingTime_base)
            nonce = w3.eth.get_transaction_count(address)
            pid = 0
            amount = check_farmLP(private_key, chain)
            contract_instance = w3.eth.contract(address=contract_address, abi=ABI_LPStakingTime)

            gas = contract_instance.functions.withdraw(pid, amount[0]).estimate_gas(
                {'from': address, 'nonce': nonce})

            tx = {
                'chainId': DATA[chain]['chain_id'],
                'from': address,
                'value': 0,
                'gas': gas,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
                 }

            transaction = contract_instance.functions.withdraw(pid, amount[0]).build_transaction(tx)
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
            time.sleep(10)
            if transaction_retry(tx_hash, current_retry, chain):
                break
        except Exception as error:
            logger.error(error)


def instantRedeemLocal(private_key: str, chain: str, amount: int) -> str:
    try:
        w3 = Web3(Web3.HTTPProvider(DATA[chain]['rpc']))
        address = w3.eth.account.from_key(private_key).address
        contract_address = w3.to_checksum_address(Router_base)
        nonce = w3.eth.get_transaction_count(address)
        id = 13

        contract_instance = w3.eth.contract(address = contract_address, abi = ABI_Router_base)

        gas = contract_instance.functions.instantRedeemLocal(id, amount, address).estimate_gas(
            {'from': address, 'nonce': nonce})

        tx = {
            'chainId': DATA[chain]['chain_id'],
            'from': address,
            'value': 0,
            'gas': gas,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        }

        transaction = contract_instance.functions.instantRedeemLocal(id, amount, address).build_transaction(tx)
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key = private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
        time.sleep(100)
        if 'status' in w3.eth.get_transaction_receipt(tx_hash) and w3.eth.get_transaction_receipt(tx_hash)['status'] == 1:
            print(f"Transaction : https://basescan.org/tx/{tx_hash}")
        else:
            print(f"Ошибка Transaction : https://basescan.org/tx/{tx_hash}. Проверь в ручную")
    except Exception as error:
        logger.error(error)


def type_action(action, private_key, chain):
    sleep = random.randint(10, 60)
    if action == 1:
        logger.info(f'Добавляю ETH в pool.')
        addLiquidityETH(private_key, chain)
        t = sleep * random.uniform(1, 2)
        print(f"Имитация поведения реального пользователя. Перерыв {round(t,)} сек.")
        time.sleep(t)
        check_lpBalance(private_key, chain)
        logger.info(f'Делаю approve LP.')
        approve(private_key, chain)
        print(f"Имитация поведения реального пользователя. Продолжу работу через {sleep} сек.")
        time.sleep(sleep)
        logger.info(f'Добавляю LP в Farming.')
        deposit(private_key, chain)
    elif action == 2:
        logger.info(f'Получаю награду за Farming.')
        claim(private_key, chain)
    elif action == 0:
        logger.info(f'Unstake в процессе.')
        withdraw(private_key, chain)
        t = random.uniform(30, 60)
        print(f"Имитация поведения реального пользователя. Перерыв {round(t,)} сек.")
        time.sleep(t)
        logger.info(f'Делаю Withdraw.')
        amount = check_lpBalance(private_key, chain)
        print(f"Withdraw в процессе. Жду подтверждения транзакции.")
        instantRedeemLocal(private_key, chain, amount)
    else:
        print("Ошибка: Недопустимое значение переменной action. Программа завершена.")
        sys.exit()


def main():
    random.shuffle(WALLETS)
    total_wallets = len(WALLETS)
    number = 0
    for key in WALLETS:
        number += 1
        print(f"Обработка кошелька {number} из {total_wallets}")
        private_key = key
        address, balance = process_wallet(private_key, chain), eth_balance(private_key, chain)
        logger.info(f" Баланс: {round(balance, 6)} ETH")
        wait_eth_gas()
        wait_base_gas()
        type_action(action, private_key, chain)
        sleep = delay
        if number != total_wallets:
            print(f"Следующий кошелек будет обработан через {sleep} сек.")
            time.sleep(sleep)
        else:
            print(f"Все кошельки успешно обработаны!")

if __name__ == "__main__":
    main()
