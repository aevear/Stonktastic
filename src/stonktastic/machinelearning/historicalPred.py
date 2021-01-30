"""
.. module:: prepDataSets
   :synopsis: This module prepares the data for processing by either *Optimization* or the main machine learning module.
"""

import pickle

import joblib
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import model_from_json

from stonktastic.config.config import (
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

        for idx, _ in enumerate(date[:-1]):
            updateDataRegistry(stonk, date[idx], "polyRegPred", results[idx])
        print(f"Historical Predicitons made for Polynomial Regression | {stonk}")

<<<<<<< Updated upstream
=======
def using_multiindex(A, columns):
    shape = A.shape
    index = pd.MultiIndex.from_product([range(s)for s in shape], names=columns)
    df = pd.DataFrame({'A': A.flatten()}, index=index).reset_index()
    return df
>>>>>>> Stashed changes

def memHistory():
    """
    Goes through and calculates what the model would have predicted for every trade day in the last seven years

    Results:
        Updated SQL database with a prediction for each day in the last seven years.

    """

    for stonk in nameList:
        jsonFilePath = open(f"{modelPaths['rmmMemoryModels']}/{stonk}mem.json", "r")
        jsonFileData = jsonFilePath.read()
        jsonFilePath.close()

        loadedModel = model_from_json(jsonFileData)
        loadedModel.load_weights(f"{modelPaths['rmmMemoryModels']}/{stonk}weight.h5")

        filename = modelPaths["rmmMemoryModels"] + f"/{stonk}Scaler.save"
        scaler = joblib.load(filename)

        xValues, _, date = prepareMemoryData(stonk, memVariables)

<<<<<<< Updated upstream
        loadedModel.compile(loss=memLoss, optimizer=memOptimizer, metrics=["accuracy"])

        date = date[-len(xValues) :]
        xValues = np.array(xValues)
=======
        loadedModel.compile(loss=memLoss, optimizer=memOptimizer)
>>>>>>> Stashed changes

        results = loadedModel.predict(xValues)
        predictions = scaler.inverse_transform(results)

        for idx, _ in enumerate(predictions):
            pred = float(predictions[idx][0])
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

        for idx, _ in enumerate(date[:-1]):
            updateDataRegistry(stonk, date[idx], "ranForPred", results[idx])

        print(f"Historical Predicitons made for Random Forest | {stonk}")


def runHistory():
    """
    Runs each of the models through history.
    """
    polyRegHistory()
    # MemHistory()
    ranForHistory()
