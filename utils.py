outfile = ''
with open(f"{outfile}wallets.txt", "r") as f:
    WALLETS = [row.strip() for row in f]
