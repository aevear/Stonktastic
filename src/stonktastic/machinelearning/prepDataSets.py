"""
.. module:: prepDataSets
   :synopsis: This module prepares the data for processing by either *Optimization* or the main machine learning module.
"""

import pickle

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from stonktastic.config.config import (
    memLookbackTime,
    memVariables,
)
from stonktastic.config.paths import modelPaths
from stonktastic.databaseCode.sqlQueries import pullDataRegistry


def preparePolyRegData(stonk, columnValues):
    """
    Prepares the data for *Polynomial Regression* based on the stock ticker and the indicator values passed. First it pulls from the SQL database before procesing the data and loading it into two sepearte dataframes for the X and Y values.

    Args:
        stonk (str) : stock ticker value
        columnValues (list) : List of strings that contain the desired indicator values to be prepared for this data set.

    :return:
        xValueList (dataframe): Dataframe with the X values based on the Date, Close and *column values*
        xValueList (dataframe): Dataframe with the Y values based on Close value offset one day in the future relative to the X values
        date (list) : A list of date values connected to the other two dataframes
    """
    data = pullDataRegistry(stonk, columnValues)

    dataFrameFullData = []
    for _, row in enumerate(data):
        rowData = []
        for cell in row:
            rowData.append(cell)
        dataFrameFullData.append(rowData)

    df = pd.DataFrame(dataFrameFullData, columns=columnValues).dropna()
    df.sort_values(by="Date", ascending=True, inplace=True)
    df = df.reset_index(drop=True)

    xColumnValues = list(columnValues)
    xColumnValues.remove("Date")
    xValueList, yValueList, date = (
        df[xColumnValues].copy(),
        df["Close"].values.tolist(),
        df["Date"].values.tolist(),
    )

    xValueList.drop(xValueList.head(1).index, inplace=True)

    return xValueList, yValueList[:-1], date[1:]


def create_dataset(data, df):
    xData, yData = [], []
    for i in range(memLookbackTime, len(data)):
        xData.append(data[i-memLookbackTime:i, :])
        yData.append(data[i, 0])
    return np.array(xData), np.array(yData)

def prepareMemoryData(stonk, columnValues):
    """
    Prepares the data for *LTSM* based on the stock ticker and the indicator values passed. First it pulls from the SQL database before procesing the data and loading it into two sepearte dataframes for the X and Y values.

    Args:
        stonk (str) : stock ticker value
        columnValues (list) : List of strings that contain the desired indicator values to be prepared for this data set.

    :return:
        xValueList (dataframe): Dataframe with the X values based on the Date, Close and *column values*
        xValueList (dataframe): Dataframe with the Y values based on Close value offset one day in the future relative to the X values
        date (list) : A list of date values connected to the other two dataframes
    """
    scaler = MinMaxScaler(feature_range=(0, 1))

    data = pullDataRegistry(stonk, columnValues)

    dataFrameFullData = []
    for _, row in enumerate(data):

        rowData = []
        for cell in row:
            rowData.append(cell)

        dataFrameFullData.append(rowData)

    df = pd.DataFrame(dataFrameFullData, columns=columnValues).dropna()
    df.sort_values(by="Date", ascending=True, inplace=True)
    df = df.reset_index(drop=True)

    xColumnValues = list(columnValues)
    xColumnValues.remove("Date")
    date = df['Date'].values.tolist()
    df = df.drop('Date', axis=1)

    train, test = train_test_split(df, test_size=0.2, shuffle=False)

    train = scaler.fit_transform(train)
    test = scaler.transform(test)

    filename = modelPaths["rmmMemoryModels"] + f"/{stonk}Scaler.save"
    pickle.dump(scaler, open(filename, "wb"))

    train = np.array(train)
    test = np.array(test)

    xTrain, yTrain = create_dataset(train, df)
    xTest, yTest = create_dataset(test, df)

    print(len(xTrain), len(yTrain))
    print(len(xTest), len(yTest))

    xTrain = np.reshape(
        xTrain, (xTrain.shape[0], xTrain.shape[1], len(memVariables) - 1)
    )

    return xTrain, yTrain, xTest, yTest, date[1:]

def prepareRanForData(stonk, columnValues):
    """
    Prepares the data for *Randome Forest* based on the stock ticker and the indicator values passed. First it pulls from the SQL database before procesing the data and loading it into two sepearte dataframes for the X and Y values.

    Args:
        stonk (str) : stock ticker value
        columnValues (list) : List of strings that contain the desired indicator values to be prepared for this data set.

    :return:
        xValueList (dataframe): Dataframe with the X values based on the Date, Close and *column values*
        xValueList (dataframe): Dataframe with the Y values based on Close value offset one day in the future relative to the X values
        date (list) : A list of date values connected to the other two dataframes
    """
    data = pullDataRegistry(stonk, columnValues)

    dataFrameFullData = []
    for _, row in enumerate(data):

        rowData = []
        for cell in row:
            rowData.append(cell)

        dataFrameFullData.append(rowData)

    df = pd.DataFrame(dataFrameFullData, columns=columnValues).dropna()
    df.sort_values(by="Date", ascending=True, inplace=True)
    df = df.reset_index(drop=True)

    xColumnValues = list(columnValues)
    xColumnValues.remove("Date")
    xValueList, yValueList, date = (
        df[xColumnValues].copy(),
        df["Close"].values.tolist(),
        df["Date"].values.tolist(),
    )

    xValueList.drop(xValueList.head(1).index, inplace=True)

    return xValueList, yValueList[:-1], date[1:]

