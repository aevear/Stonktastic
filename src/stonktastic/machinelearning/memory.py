"""
test
"""

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.layers import LSTM, Dense, Dropout
from tensorflow.python.keras.models import Sequential
from tensorflow.keras.metrics import RootMeanSquaredError

from stonktastic.config.config import (
    memBatchSize,
    memEpochs,
    memLookbackTime,
    memLoss,
    memOptimizer,
    memVariables,
)
from stonktastic.config.paths import modelPaths, nameList
from stonktastic.databaseCode.sqlQueries import updateCalculationsRegistry
from stonktastic.machinelearning.prepDataSets import prepareMemoryData

warnings.simplefilter(action="ignore", category=FutureWarning)


def runMemory(xValueList, yValueList, date):
    """
    test
    """
    xTrain, xTest, yTrain, yTest = train_test_split(xValueList, yValueList, test_size=0.2, random_state=4)
    xTrain, xTest, yTrain, yTest = (
        np.array(xTrain),
        np.array(xTest),
        np.array(yTrain),
        np.array(yTest),
    )

    xTrain = np.reshape(
        xTrain, (xTrain.shape[0], xTrain.shape[1], len(memVariables) - 1)
    )  # set last number to # of features

    model = Sequential()
    # Layer 1
    model.add(
        LSTM(
            units=50,
            kernel_initializer="glorot_uniform",
            return_sequences=True,
            input_shape=(xTrain.shape[1], xTrain.shape[2]),
        )
    )
    model.add(Dropout(0.2))
    # Layer 2
    model.add(
        LSTM(units=50, kernel_initializer="glorot_uniform", return_sequences=True)
    )
    model.add(Dropout(0.2))
    # Layer 3
    model.add(LSTM(units=50, kernel_initializer="glorot_uniform"))
    model.add(Dropout(0.2))

    model.add(Dense(yTrain.shape[1]))

    model.compile(loss=memLoss, optimizer=memOptimizer, metrics=['RootMeanSquaredError'])

    model.fit(xTrain, yTrain, epochs=memEpochs, batch_size=memBatchSize)

    #check predicted values
    #predictions = model.predict(xTest)
    #Undo scaling
    #unScaledPred = scaler.inverse_transform(predictions)

    accuracy = model.evaluate(xTest, yTest, batch_size=memBatchSize)

    return (model, accuracy)


def memoryMain():
    """
    Cycles for every stock in the project, this function prepares the data for the model using the configuration listed in the configuration.csv file

    Results:

    - Saves off the model to the *model* folder for later usage.

    - Records the R^2 value of the model to the *Calculations Registry* table.

    """

    for stonk in nameList:

        X, y, Date = prepareMemoryData(stonk, memVariables)

        model, results = runMemory(X, y, Date)

        model_json = model.to_json()
        modelLocation = modelPaths["rmmMemoryModels"]

        with open(modelLocation + f"/{stonk}mem.json", "w") as json_file:
            json_file.write(model_json)

        model.save_weights(modelLocation + f"/{stonk}weight.h5")

        updateCalculationsRegistry(stonk, "memoryScore", results[1])

        print(f"{stonk} | Memory : {results[1]}")
