'''
test
'''

from csv import reader

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.python.keras.layers import LSTM, Dense, Dropout
from tensorflow.python.keras.models import Sequential
from keras.callbacks import EarlyStopping
import keras.backend as K

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


def standardizeResults(value):
    """
    Preforms *Polynomial Regression* based on the arguments provided.

    Note that we split the data by the *First* 80 percent of the data and then the *Last* 20 percent of the data, rather than randomly splitting the data by 80/20 for the Train/Test split.

    Args:
        xValueList (list of floats) : List of X values used for polynomial regression. Offset 1 day earlier than the y values so we have something to predict. Prepared by *prepDataSets*. Can change based on the values in saved in the configuration file.
        yValueList (list of floats) : Close values tied to the X value list for the following day.
        degrees (int) : Level of degress the polynomial will be operating at.

    :return:
        model: The actual machine Learning model.
        float: the R^2 score for the model.
    """
    if value < 0:
        return "0.00"
    elif value > 100:
        return "100.00"
    else:
        return value

def soft_acc(y_true, y_pred):
    return K.mean(K.equal(K.round(y_true), K.round(y_pred)))

def runMemory(xTrain, yTrain):
    """
    test
    """

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
    model.add(LSTM(units=50, kernel_initializer='glorot_uniform', return_sequences=True))
    model.add(Dropout(0.2))
    # Layer 3
    model.add(LSTM(units=50, kernel_initializer='glorot_uniform'))
    model.add(Dropout(0.2))

    model.add(Dense(xTrain.shape[2]))

    model.compile(loss=memLoss, optimizer=memOptimizer, metrics=[soft_acc])

    return model, xTrain, yTrain

def runFitAccuracy(model, xTrain, yTrain, xTest, yTest):

    epochCallbacks = [EarlyStopping(monitor='val_loss', patience=20, mode='min', verbose=1, min_delta=0.0001)]

    model.fit(xTrain, yTrain, epochs=memEpochs, batch_size=memBatchSize,
              validation_split=0.2, callbacks=epochCallbacks)

    accuracy = model.evaluate(xTest, yTest, batch_size=memBatchSize)

    return (model, accuracy)

def memoryMain():
    """
    Cycles for every stock in the project, this function prepares the data for the model using the configuration listed in the configuration.csv file

    Results:

    - Saves off the model to the *model* folder for later usage.

    - Records the R^2 value of the model to the *Calculations Registry* table.

    """

    columnValues = memVariables

    for stonk in nameList:
        print(stonk)

        xTrain, yTrain, xTest, yTest, Date = prepareMemoryData(stonk, columnValues)

        model, xTrain, yTrain = runMemory(xTrain, yTrain)

        model, results = runFitAccuracy(model, xTrain, yTrain, xTest, yTest)

        print(results)

        model_json = model.to_json()
        modelLocation = modelPaths['rmmMemoryModels']

        with open(modelLocation + f"/{stonk}mem.json", "w") as json_file:
            json_file.write(model_json)

        model.save_weights(modelLocation + f"/{stonk}weight.h5")

        updateCalculationsRegistry(stonk, "memoryScore", standardizeResults(results[1]))
        print(f"{stonk} | Memory : {standardizeResults(results[1])}")





# |Close|SAR|RSI|CCI|MACDHist|BBUpperBand|BBMiddleBand|BBLowerBand|EMA|Chaikin|StochK|StochD|WILLR|Date