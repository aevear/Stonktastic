"""
.. module:: optimizePolyReg
   :synopsis: Preforms optimization scenarios for Polynomial Regression and reports on best configuration options
"""

import itertools
import time

import pandas as pd

from stonktastic.config.config import polyPolynomial, polyVariables
from stonktastic.machinelearning.polyReg import runPolyReg
from stonktastic.machinelearning.prepDataSets import preparePolyRegData


class polyRegOptResultClass:
    """
    Class for holding processed values for Jupyter notebook analysis

    Values:
        optSubSet (list): List of best indicators to use for Polynomial Regression in terms of accuracy/resource cost
        subDf (dataframe): Dataframe with all subset/time/score values for graphing
        optPolyValue (int): The optimum polynomial level to use in terms of accuracy/time
        polyDf (dataframe): Dataframe with all polynomial levels as well as the time it took to process and the accuracy of those predictions
    """

    def __init__(
        self,
        optSubSet=[""],
        subDf=pd.DataFrame(),
        optPolyValue=1,
        polyDf=pd.DataFrame(),
    ):
        self.optSubSet = optSubSet
        self.subDf = subDf
        self.optPolyValue = optPolyValue
        self.polyDf = polyDf


def polyRegVariableOpt(stonk):
    """
    Generates a Polynomial Regression model and test the model with varying indicators of values and ranks them based on accuracy/time.

    Args:
        stonk (str): stock ticker that will be used for optimization

    :returns:
        list: Top list of indicators in terms of time/accuracy for Polynomial Regression using the stock ticker provided
        dataframe: complete dataframe for stock ticker with all subsets, times and scores
    """
    polyRegVariables = [
        "SAR",
        "RSI",
        "CCI",
        "MACDHist",
        "BBUpperBand",
        "BBMiddleBand",
        "BBLowerBand",
        "EMA",
        "Chaikin",
        "StochK",
        "StochD",
        "WILLR",
    ]

    combinationOfColumnValues = []
    for k in range(0, len(polyRegVariables) + 1):
        for subset in itertools.combinations(polyRegVariables, k):
            subset = subset + (("Close", "date"))
            if len(subset) > 4:
                combinationOfColumnValues.append(subset)

    resultsList = []
    for subset in combinationOfColumnValues:
        startTime = time.time()
        xValueList, yValueList, _ = preparePolyRegData(stonk, subset)
        _, results = runPolyReg(xValueList, yValueList, polyPolynomial)
        timeToRun = time.time() - startTime
        resultsList.append(
            [
                subset,
                results,
                str(timeToRun),
                str(results / timeToRun),
                int(len(subset)),
            ]
        )

    df = pd.DataFrame(
        resultsList, columns=["subset", "results", "time", "score", "numOfVariables"]
    )
    df.sort_values(by="score", ascending=False, inplace=True)
    df = df.reset_index(drop=True)

    optSubSet = df["subset"][0]

    return (optSubSet, df)


def polyRegPolynomialOpt(stonk):
    """
    Generates a Polynomial Regression model and test the model with varying polynomial degress ranks them based on accuracy/time.

    Args:
        stonk (str): stock ticker that will be used for optimization

    :returns:
        int: Optimum Polynomial Degree in terms of time/accuracy using the stock ticker provided
        dataframe: complete dataframe for stock ticker with all polynomial degree levels, times and scores
    """
    polynomialOptions = [1, 2, 3, 4, 5]

    resultsList = []
    for polyOption in polynomialOptions:
        startTime = time.time()
        xValueList, yValueList, _ = preparePolyRegData(stonk, polyVariables)
        _, results = runPolyReg(xValueList, yValueList, polyOption)
        timeToRun = time.time() - startTime
        resultsList.append(
            [polyOption, float(results), float(timeToRun), float(results / timeToRun)]
        )

    df = pd.DataFrame(resultsList, columns=["polyOption", "results", "time", "score"])
    df.sort_values(by="score", ascending=False, inplace=True)
    df = df.reset_index(drop=True)

    optPolyValue = df["polyOption"][0]

    return (optPolyValue, df)


def runPolyRegOptimization(stonk):
    """
    Full optimization test for Polynomial Regression looking at both the *indicator subsets* and *polynomial degrees*

    The class has defaults loaded in so you do not have to run both optimizers at once.

    Args:
        stonk (str): the stock ticker that will be used for optimization

    :return:
        polyRegOptResultClass (class): Class storing the top subset and polynomial degrees as well as full dataframes with the complete results from both optimization test.
    """
    polyRegResults = polyRegOptResultClass()

    optSubSet, subDf = polyRegVariableOpt(stonk)
    polyRegResults.optSubSet = optSubSet
    polyRegResults.subDf = subDf

    optPolyValue, polyDf = polyRegPolynomialOpt(stonk)
    polyRegResults.optPolyValue = optPolyValue
    polyRegResults.polyDf = polyDf

    print("==========================")
    print("Polynomial Regression Optimization")
    print("==========================")
    print(f"{stonk} | Poly Reg Optimize Variable   : {', '.join(list(optSubSet))}")
    print(f"{stonk} | Poly Reg Optimizd Poly Value : {optPolyValue}")

    return polyRegResults
