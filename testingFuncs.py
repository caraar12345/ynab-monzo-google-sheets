def potBalanceCalc(potName, amount):
    try:
        potBalances[potName] += -amount
    except KeyError:
        potBalances[potName] = -amount


def potBalCalc()
   for x in values:
        if x[3] == "Pot transfer":
            potBalanceCalc(x[4], float(x[7]))
            # x[1] = date; x[4] = payee; x[7] = amount in GBP; x[11] = memo

    try:
        valueHandler(x[1], x[4], float(x[7]), x[11])
    except IndexError:
        valueHandler(x[1], x[4], float(x[7]), "")

    for pot in potBalances:
        print(pot, "- Balance: £{:0.2f}".format(abs(potBalances[pot])))
