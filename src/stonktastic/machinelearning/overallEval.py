"""
.. module:: polyReg
   :synopsis: Runs and preforms Polynomial regression on all stocks found in the DB based on values found in the configuration file.
"""

import pandas as pd

from stonktastic.config.paths import nameList
from stonktastic.databaseCode.sqlQueries import (
    pullCalculationsRegistry,
    pullFullEstimates,
    updateCalculationsRegistry,
)


def simulateYear(df, modelType):
    """
    This function simulates a year of buying/selling stocks by looking at the predicted value for the next day and either buying/selling all of thier stock/money if the value is higher/lower than it is currently. This is not a fine tune system of measuring accuracy, its just to get an estimate on the potential gain of this stock using each algorithum.

    Args:
        df (dataframe) : Dataframe with the date, close value, and each day's predicted value for each model.
        modelType (str) : Which algorithum's prediction capability we are using for this simulation

    :returns:
        float: The yearly percentage gains

    """
    funds = 1000000.0
    stocks = 0.0

    for row in range(len(df)):

        # Buy Stocks
        if df.at[row, "Close"] < df.at[row, modelType] and funds > 0:
            stocks = funds / float(df.at[row, "Close"])
            funds = 0

        # Sell Stocks
        elif df.at[row, "Close"] > df.at[row, modelType] and stocks > 0:
            funds = stocks * float(df.at[row, "Close"])
            stocks = 0

    # Cash out
    if funds == 0:
        funds = stocks * float(df.at[row, "Close"])

    gains = (funds - 1000000.0) / 1000000.0

    return gains


def preformOverallEvalCalculations(estimates):
    """
    Here we generate find the "best model" in terms of profit and save off the yearly profit for each model per stock

    Args:
        estimates (list) : A list containing dict/key pairs of {stock ticker : dataframe}
        dataframe in estimates (df): Contains *Close*, *Date*, *polyPred*, *memPred*, *ranPred* for each day in the last year

    Results:
        Updated *Calculations Registry* table

    """
    for stonk in nameList:
        runningTotal = 0.0
        highestEstimate, bestModel = -100000000, ""
        for model in list(
            [
                ["polyPred", "polyProfit"],
                ["memPred", "MemProfit"],
                ["ranPred", "RanProfit"],
            ]
        ):

            gains = simulateYear(estimates[stonk], model[0])
            runningTotal = runningTotal + gains
            if gains > highestEstimate:
                highestEstimate = gains
                bestModel = model[0]

            updateCalculationsRegistry(stonk, model[1], gains)

        if bestModel == "polyPred":
            bestModel = "'Polynomial Regression'"
        elif bestModel == "memPred":
            bestModel = "'LTSM'"
        else:
            bestModel = "'Random Forest'"

        updateCalculationsRegistry(stonk, "BestModel", bestModel)
        updateCalculationsRegistry(stonk, "YearProfit", runningTotal / 3)


def rankStocks():
    """
    Pulls the yearly profits for each stock and provides them a tiered rank
    """
    stockYearProfits = []

    data = pullCalculationsRegistry("YearProfit")
    for k in data:
        stockYearProfits.append([k[0], k[2]])

    df = pd.DataFrame(data=stockYearProfits, columns=["Stonk", "YearProfit"])
    df.sort_values(by="YearProfit",inplace=True, ascending=False)
    df = df.reset_index(drop=True)

    for idx in range(len(df)):
        updateCalculationsRegistry(df.loc[idx, "Stonk"], "ValueScore", idx)


def overallEval():
    """
    Runs the overall stock functions. Estimates yearly gain using each model for each stock, the average gain per stock, then ranks each stock based on gains.
    """
    estimates = pullFullEstimates()
    preformOverallEvalCalculations(estimates)
    rankStocks()
