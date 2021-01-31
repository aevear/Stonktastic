"""
.. module:: flask
   :synopsis: provides backend support for the flask app
"""


import math

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from app.code.sqlQueries import (
    pullCalculationsRegistry,
    pullDataRegistry,
    pullRankedTopStocksDataCalculationRegistry,
    pullStockRegistry,
)


def round_down(n, decimals=0):
    """
    used to round down values

    Args:
        n (float): This number will be rounded

    :return:
        int: the provided number rounded down
    """
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


def getDashboardFlaskData():
    """
    Gathers the information that flask needs for the *Dashboard* html page

    :returns:

        dashboardChart (list): A list of list containing
        - ticker (str): stock ticker value

        - datelist (list of str): dates used in the chart

        - closeList (list of floats): close values for the ticker


        stockDataList (list): A list of list containing:
        - ticker (str): stock ticker value

        - security(str): stock security value

        - symbol (str): stock symbol


        totalValueDataList (list): A list of list containing:
        - ticker (str): stock ticker value

        - Year Profit (float): yearly profit from all models rounded to the second decimal place

        - Average Model Score (int): Average model score for all three models for this stock


        snpChartData (list): A list of list containing:
        - ticker (str): stock ticker value

        - date (str): date values for the SNP chart (last 25 days)

        - close (float): rounded to the second decimal, it contains close values for the snp char (last 25 days)

    """

    topFiveStocksSymbols = pullRankedTopStocksDataCalculationRegistry()

    dashboardChart, stonkList = [], []
    for stonk in topFiveStocksSymbols:
        stonkList.append(stonk[0])

    stonkList = stonkList[::-1]
    stonkList = stonkList[:5]

    for stonk in stonkList:
        stockData = pullDataRegistry(stonk, "Date", "Close")

        dateList, closeList = [], []
        scaler = MinMaxScaler(feature_range=(0, 100))
        for idx, k in enumerate(stockData):
            if idx < 25:
                dateList.append(str(k[0])[:-9])
                closeList.append([k[1], k[1]])

        holdList = scaler.fit_transform(np.array(closeList))

        closeList = []
        for k in holdList:
            closeList.append(str(round(k[0], 2)))

        dashboardChart.append([stonk, dateList, closeList])

    stockDataList = []
    for stonk in stonkList:
        stockData = pullStockRegistry(stonk, "Security", "Symbol")
        for k in stockData:
            stockDataList.append([stonk, k[0], k[1]])

    totalValueDataList = []
    for stonk in stonkList:
        stockData = pullCalculationsRegistry(
            "YearProfit", "polyRegScore", "MemoryScore", "ranForScore"
        )
        for k in stockData:
            if k[0] == stonk:
                totalValueDataList.append(
                    [
                        stonk,
                        round(k[2], 2),
                        int(((float(k[3]) + float(k[4]) + float(k[5])) / 3) * 100),
                    ]
                )

    stockData = pullDataRegistry("S&P", "Date", "Close")

    snpChartData, dateList, closeList = [], [], []
    for idx, k in enumerate(stockData):
        if idx < 25:
            dateList.append(str(k[0])[:-9])
            closeList.append(round(k[1], 2))
    snpChartData.append([dateList, closeList])

    return dashboardChart, stockDataList, totalValueDataList, snpChartData


def getStockTemplateData():
    """
    Used for the general stocklist html sheet, contains general information on each stock

    :return:
        list:
            - List of stock ranks

            - List of company names

            - List of ticker values

            - list of yearly profit

    """
    data = pullCalculationsRegistry("ValueScore", "YearProfit")

    stockData = []
    for idx, k in enumerate(data):
        companyName = k[0]
        stonkNames = k[1]
        rank = int(k[2])
        value = round(k[3], 2)

        row = [rank, companyName, stonkNames, value]
        stockData.append(row)

    return stockData


def getIndividualStockInfo(stonkName):
    """
    For the individual stock page

    Args:
        stonkName (str): stock ticker for individual page

    :returns:
        stonkName (str) : stock ticker provided by source


        chartData (list): contains four float values that will be passed to the bubbles under the graph
            - polyRegScore (float): The Polynomial Regression score

            - memoryScore (float): The LTSM score

            - ranForScore (float): The Random Forest score


        dataTable (list): Contains the information for the daily values found at the bottom of the page
            - date (list): Date of that day of trading

            - open (list): Opening values for that day of trading

            - close (list): Closing values for that day of trading

            - predClose (list): Average predicted close value for that day between all three models

            - change (list): Calculated difference between the predicted close and actual close value

            - accuracy (list): Accuracy of the prediction versus the real close value


        dates (list): list of dates that wil be used in the chart

        closeValue (list): list of floats that represent daily close values

        polyRegPred (list): list of floats for predicted close using Polynomial Regression

        memoryPred (list): list of floats for predicted close using LTSM

        forestPred (list): list of floats for predicted close using Random Forest


    """
    data = pullDataRegistry(
        stonkName, "Date", "Close", "polyRegPred", "memPred", "ranForPred"
    )

    dates, closeValue, polyRegPred, memoryPred, forestPred = [], [], [], [], []
    for idx, k in enumerate(data):
        if idx < 20:
            dates.append(str(k[0])[:-9])
            closeValue.append(k[1])
            polyRegPred.append(k[2])
            memoryPred.append(k[3])
            forestPred.append(k[4])

    data = pullCalculationsRegistry("polyRegScore", "memoryScore", "ranForScore")

    for k in data:
        if k[0] == stonkName:
            sumScore = round(float(((k[2] + k[3] + k[4]) / 3) * 100), 0)
            polyRegScore = round_down(float(k[2] * 100))
            memoryScore = round_down(float(k[3] * 100))
            ranForScore = round_down(float(k[4] * 100))

            chartData = [sumScore, polyRegScore, memoryScore, ranForScore]

    data = pullDataRegistry(stonkName, "date", "open", "close", "ranForPred")

    dataTable = []
    for idx, k in enumerate(data):
        if idx < 252:
            date = str(k[0])[5:-9]
            open = round(float(k[1]), 2)
            close = round(float(k[2]), 2)
            predClose = round(float(k[3]), 2)
            change = str((round((((k[2] - k[3]) / k[2]) * 100), 0))) + " %"
            accuracy = str(int(100 - abs(((k[2] - k[3]) / k[2]) * 100))) + " %"

            dataTable.append([date, open, close, predClose, change, accuracy])

    return (
        stonkName,
        chartData,
        dataTable,
        dates,
        closeValue,
        polyRegPred,
        memoryPred,
        forestPred,
    )
