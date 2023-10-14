import random

#########___________________________________ К О Н Ф И Г ___________________________________#########

MAX_GWEI = 40 # Спим если текущий Gwei в ETH > MAX_GWEI

Base_GWEI = 0.5 # Спим если текущий Gwei в Base > Base_GWEI

pool_amount = random.uniform(0.1, 0.9) # Сколько ETH добавлять в пул

retries = 1 # Сколько делать попыток транзакций

delay = random.randint(5, 20) # Сколько спим между кошельками (секунды)

action = 1 # Что делаем Stake = 1 / Unstake = 0 / Claim = 2
