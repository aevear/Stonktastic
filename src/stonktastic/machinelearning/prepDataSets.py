"""
.. module:: prepDataSets
   :synopsis: This module prepares the data for processing by either *Optimization* or the main machine learning module.
"""

import pickle

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from stonktastic.config.config import memLookbackTime
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
    df.sort_values(by="Date", ascending=False, inplace=True)
    df = df.reset_index(drop=True)

    xColumnValues = list(columnValues)
    xColumnValues.remove("Date")
    xValueList, yValueList, date = (
        df[xColumnValues].copy(),
        df["Close"].values.tolist(),
        df["Date"].values.tolist(),
    )

    xValueList.drop(xValueList.head(1).index, inplace=True)

    return xValueList, yValueList[:-1], date

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
    df.sort_values(by="Date", ascending=False, inplace=True)
    df = df.reset_index(drop=True)

    xColumnValues = list(columnValues)
    xColumnValues.remove("Date")
<<<<<<< Updated upstream
    xDF, yDF, date = df[xColumnValues], df["Close"], df["Date"].values.tolist()
=======
    df, date = df[xColumnValues], df["Date"].values.tolist()

    scaledData = pd.DataFrame(scaler.fit_transform(df))
>>>>>>> Stashed changes

    scaler.fit_transform(df)
    filename = modelPaths["rmmMemoryModels"] + f"/{stonk}Scaler.save"
    pickle.dump(scaler, open(filename, "wb"))

    xValueList, yValueList = [], []
    lookBackTime = memLookbackTime
    for i in range(lookBackTime, len(scaledData)):
        xValueList.append(scaledData.iloc[i - lookBackTime : i])
        yValueList.append(scaledData.iloc[i])

<<<<<<< Updated upstream
    return xValueList, yValueList, date[1:]
=======
    xValueList, yValueList = np.asarray(xValueList).astype('float32'), np.asarray(yValueList).astype('float32')

    return xValueList, yValueList, date
>>>>>>> Stashed changes


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
    df.sort_values(by="Date", ascending=False, inplace=True)
    df = df.reset_index(drop=True)

    xColumnValues = list(columnValues)
    xColumnValues.remove("Date")
    xValueList, yValueList, date = (
        df[xColumnValues].copy(),
        df["Close"].values.tolist(),
        df["Date"].values.tolist(),
    )

    xValueList.drop(xValueList.head(1).index, inplace=True)

    return xValueList, yValueList[:-1], date
