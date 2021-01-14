"""
.. module:: optimizeRanFor
   :synopsis: Preforms optimization scenarios for Random Forest and reports on best configuration options
"""
import itertools
import time

import pandas as pd

from stonktastic.config.config import ranForEstimators, ranForVariables
from stonktastic.machinelearning.prepDataSets import prepareRanForData
from stonktastic.machinelearning.ranForest import runRandomForest


class ranForOptResultClass:
    """
    Class for holding processed values for Jupyter notebook analysis

    Values:
        optSubSet (list): List of best indicators to use for Random Forest in terms of accuracy/resource cost
        subDf (dataframe): Dataframe with all subset/time/score values for graphing
        optEstimators (int): Most optimum number of trees to use in random forest calculations
        estimatorsDf (dataframe): Dataframe with all estimator amounts as well as the time it took to process and the accuracy of those predictions
    """

    def __init__(
        self,
        optSubSet=[""],
        subDf=pd.DataFrame(),
        optEstimators=100,
        estimatorsDf=pd.DataFrame(),
    ):
        self.optSubSet = optSubSet
        self.subDf = subDf
        self.optEstimators = optEstimators
        self.estimatorsDf = estimatorsDf


def ranForVariableOpt(stonk):
    """
    Generates a random forest model and test the model with varying indicators of values and ranks them based on accuracy/time.

    Args:
        stonk (str): stock ticker that will be used for optimization

    :returns:
        list: Top list of indicators in terms of time/accuracy for Random Forest using the stock ticker provided
        dataframe: complete dataframe for stock ticker with all subsets, times and scores
    """
    ranForVariables = [
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
    for k in range(0, len(ranForVariables) + 1):
        for subset in itertools.combinations(ranForVariables, k):
            subset = subset + (("Close", "date"))
            if len(subset) > 4:
                combinationOfColumnValues.append(subset)

    resultsList = []
    for subset in combinationOfColumnValues:
        startTime = time.time()
        xValueList, yValueList, date = prepareRanForData(stonk, subset)
        _, results = runRandomForest(xValueList, yValueList, date, ranForEstimators)
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


# Degrees of Polynomial
def ranForEstimatorOpt(stonk):
    """
    Generates a random forest model and test the model with varying amounts of decision trees (estimators) of values and ranks them based on accuracy/time.

    Args:
        stonk (str): stock ticker that will be used for optimization

    :returns:
        int: Optimum number of estimators in terms of time/accuracy for Random Forest using the stock ticker provided
        dataframe: complete dataframe for stock ticker with all estimators, times and scores
    """
    estimatorOptions = range(10, 1000, 10)

    resultsList = []
    for estOption in estimatorOptions:
        startTime = time.time()
        xValueList, yValueList, date = prepareRanForData(stonk, ranForVariables)
        _, results = runRandomForest(xValueList, yValueList, date, estOption)
        timeToRun = time.time() - startTime
        resultsList.append(
            [estOption, float(results), float(timeToRun), float(results / timeToRun)]
        )

    df = pd.DataFrame(resultsList, columns=["estOption", "results", "time", "score"])
    df.sort_values(by="score", ascending=False, inplace=True)
    df = df.reset_index(drop=True)

    optPolyValue = df["estOption"][0]

    print(df.head(10))

    return (optPolyValue, df)


def runRanForOptimization(stonk):
    """
    Full optimization test for Random Forest looking at both the *indicator subsets* and *estimators*

    The class has defaults loaded in so you do not have to run both optimizers at once.

    Args:
        stonk (str): the stock ticker that will be used for optimization

    :return:
        ranForOptResultClass (class): Class storing the top subset and estimators as well as full dataframes with the complete results from both optimization test.
    """
    ranOptResults = ranForOptResultClass()

    optSubSet, subDf = ranForVariableOpt(stonk)
    ranOptResults.optSubSet = optSubSet
    ranOptResults.subDf = subDf

    optEstimators, estimatorsDf = ranForEstimatorOpt(stonk)
    ranOptResults.optEstimators = optEstimators
    ranOptResults.estimatorsDf = estimatorsDf

    print("==========================")
    print("Random Forest Optimization")
    print("==========================")
    print(f"{stonk} | Optimized Variables  : {', '.join(list(optSubSet))}")
    print(f"{stonk} | Optimized Estimators : {optEstimators}")

    return ranOptResults
