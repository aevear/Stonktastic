"""
.. module:: prepDataSets
   :synopsis: This module prepares the data for processing by either *Optimization* or the main machine learning module.
"""

import pickle

import joblib
import numpy as np
import pandas as pd
from numpy import newaxis
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import model_from_json

from stonktastic.config.config import (
    memLookbackTime,
    memLoss,
    memOptimizer,
    memVariables,
    polyVariables,
    ranForVariables,
)
from stonktastic.config.paths import modelPaths, nameList
from stonktastic.databaseCode.sqlQueries import updateDataRegistry
from stonktastic.machinelearning.prepDataSets import (
    prepareMemoryData,
    preparePolyRegData,
    prepareRanForData,
)

import csv
from csv import reader


def polyRegHistory():
    """
    Goes through and calculates what the model would have predicted for every trade day in the last seven years

    Results:
        Updated SQL database with a prediction for each day in the last seven years.

    """
    for stonk in nameList:

        filename = modelPaths["polyRegModels"] + f"/{stonk}polyReg.sav"
        loadedModel = pickle.load(open(filename, "rb"))

        xValues, _, date = preparePolyRegData(stonk, polyVariables)

        results = loadedModel.predict(xValues)

        for idx, _ in enumerate(date):
            updateDataRegistry(stonk, date[idx], "polyRegPred", results[idx])
        print(f"Historical Predicitons made for Polynomial Regression | {stonk}")



def using_multiindex(A, columns):
    shape = A.shape
    index = pd.MultiIndex.from_product([range(s)for s in shape], names=columns)
    df = pd.DataFrame({'A': A.flatten()}, index=index).reset_index()
    return df

def memHistory():
    """
    Goes through and calculates what the model would have predicted for every trade day in the last seven years

    Results:
        Updated SQL database with a prediction for each day in the last seven years.

    """
    scaler = MinMaxScaler(feature_range=(0, 1))

    for stonk in nameList:
        jsonFilePath = open(f"{modelPaths['rmmMemoryModels']}/{stonk}mem.json", "r")
        jsonFileData = jsonFilePath.read()
        jsonFilePath.close()

        loadedModel = model_from_json(jsonFileData)
        loadedModel.load_weights(f"{modelPaths['rmmMemoryModels']}/{stonk}weight.h5")

        filename = modelPaths["rmmMemoryModels"] + f"/{stonk}Scaler.save"
        scaler = joblib.load(filename)

        xTrain, _, xTest, _, date = prepareMemoryData(stonk, memVariables)

        loadedModel.compile(loss=memLoss, optimizer=memOptimizer, metrics=["accuracy"])

        totalLength = len(xTrain) + len(xTest)

        date = date[-totalLength :]
        print(date)
        print(len(date))

        loadedModel.compile(loss=memLoss, optimizer=memOptimizer)

        trainPredict = loadedModel.predict(xTrain)
        testPredict = loadedModel.predict(xTest)

        trainPredict = scaler.inverse_transform(trainPredict)
        testPredict = scaler.inverse_transform(testPredict)

        predictions = np.concatenate((testPredict,trainPredict),axis=0)

        print('This is the pricing')
        print(predictions[:,4])

        for idx, _ in enumerate(predictions):
            pred = float(predictions[idx][4])
            updateDataRegistry(stonk, date[idx], "memPred", pred)
        print(f"Historical Predicitons made for RNN LTSM Memory | {stonk}")

def ranForHistory():
    """
    Goes through and calculates what the model would have predicted for every trade day in the last seven years

    Results:
        Updated SQL database with a prediction for each day in the last seven years.

    """
    for stonk in nameList:

        filename = modelPaths["ranForModels"] + f"/{stonk}ranForest.sav"
        loadedModel = pickle.load(open(filename, "rb"))

        xValues, _, date = prepareRanForData(stonk, ranForVariables)
        results = loadedModel.predict(xValues)

        for idx, _ in enumerate(date):
            updateDataRegistry(stonk, date[idx], "ranForPred", results[idx])
            updateDataRegistry(stonk, date[idx], "memPred", results[idx])

        print(f"Historical Predicitons made for Random Forest | {stonk}")


def runHistory():
    """
    Runs each of the models through history.
    """
    polyRegHistory()
    memHistory()
    ranForHistory()
