
'''

'''

import itertools
import pandas as pd
import numpy as np
import time
import keras
from keras.callbacks import EarlyStopping, ModelCheckpoint, History
# import talos as ta

# For Prediction
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers import LSTM
from tensorflow.python.keras.layers import Dropout
from sklearn.model_selection import train_test_split

from stonktastic.config.config import memVariables
from stonktastic.config.config import memBatchSize
from stonktastic.config.config import memEpochs
from stonktastic.machinelearning.prepDataSets import prepareMemoryData
from stonktastic.machinelearning.rnnMemory import runMemory
from stonktastic.config.paths import modelPaths


class memoryOptResultClass:
    def __init__(self, optSubSet=[''], subDf=pd.DataFrame(), epochDF=pd.DataFrame()):
        self.optSubSet     = optSubSet
        self.subDf         = subDf
        self.epochDF       = epochDF


class TimeHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.times = []

    def on_epoch_begin(self, epoch, logs={}):
        self.epoch_time_start = time.time()

    def on_epoch_end(self, epoch, logs={}):
        self.times.append(time.time() - self.epoch_time_start)


def epochOpt(stonk):

    modelLocation = modelPaths['memoryOptModel']
    modelLocation = modelLocation + f"/modelOpted.h5"

    history = History()
    epochCallbacks = [history, EarlyStopping(monitor='val_loss', patience=15, mode='min', verbose=1, min_delta=0.0001),
                      ModelCheckpoint(filepath=modelLocation, verbose=1, monitor='val_loss',
                                      save_best_only=True, mode='min')]

    X, y, Date = prepareMemoryData(stonk, memVariables)
    model, X_train, y_train, X_test, y_test = runMemory(X, y, Date, memVariables)

    history = model.fit(X_train, y_train, epochs=100, batch_size=memBatchSize,
                        validation_split=0.2, callbacks=epochCallbacks)
    scores = model.evaluate(X_test, y_test, verbose=1)

    print(f'Score: {model.metrics_names[0]} of {scores[0]}; {model.metrics_names[1]} of {scores[1]*100}%')

    epochsRan = len(history.history['loss'])
    testingLoss = history.history['loss']
    valLoss = history.history['val_loss']
    print("Optimal Epochs Ran: ", epochsRan)
    print("Testing Loss: ", testingLoss)
    print("Validation Loss: ", valLoss)

    # ---------------------------------
    # Format our DataFrame
    # ---------------------------------
    resultsDict = {'Testing Loss': testingLoss, 'Val Loss': valLoss}
    df = pd.DataFrame(resultsDict)
    df.index = df.index + 1
    df.reset_index(inplace=True)

    df = pd.melt(df, ['index'])
    df = df.rename(columns={'index': 'Epoch', 'variable': 'Loss', 'value': 'Value'})

    df.to_csv('optEpochSet.csv', index=False)

    return df

def hyperParamModel(X_train, y_train, X_test, y_test, params):

    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], len(memVariables)-1)) # set last number to # of features
    # --------------------------------
    # Starting the process of making the model
    # --------------------------------
    model = Sequential()
    # Layer 1
    model.add(LSTM(units=params['units'], kernel_initializer=params['kernel_initializer'], return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(params['dropout']))
    # Layer 2
    model.add(LSTM(units=params['units'], kernel_initializer=params['kernel_initializer'], return_sequences=True))
    model.add(Dropout(params['dropout']))
    # Layer 3
    model.add(LSTM(units=params['units'], kernel_initializer=params['kernel_initializer']))
    model.add(Dropout(params['dropout']))

    model.add(Dense(y_train.shape[1]))

    model.compile(loss=params['loss'], optimizer=params['optimizer'], metrics=['accuracy'])

    history = model.fit(X_train, y_train, epochs=params['epochs'], batch_size=params['batch_size'],
                        validation_split=0.2)

    return history, model

def runHyperOpt(stonk):

    p = {'units': [30, 40, 50],
         'kernel_initializer': ['glorot_uniform'],
         'optimizer': ['Adam', 'Nadam', "RMSprop"],
         'dropout': [0.2, 0.5, 0.8],
         'epochs': [20],
         'loss': ['mean_squared_error', 'mean_absolute_error'],
         'batch_size': [20, 30, 40]}

    X, y, Date = prepareMemoryData(stonk, memVariables)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=4)
    X_train, X_test, y_train, y_test = np.array(X_train), np.array(X_test), np.array(y_train), np.array(y_test)

    t = ta.Scan(x=X_train,
                y=y_train,
                model=hyperParamModel,
                experiment_name='memoryHyperOpt',
                params=p,
                print_params=True)

    e = ta.Evaluate(t)
    e.data.head()
    e.data.to_csv('memoryHyperSet.csv')

def memoryVariableOpt(stonk):
    totalTime = 0.0
    memoryVariables = ["SAR", "RSI", "CCI", "MACDHist", "BBUpperBand",
                       "BBMiddleBand", "BBLowerBand", "EMA", "Chaikin",
                       "StochK", "StochD", "WILLR"]

    combinationOfColumnValues = []
    for k in range(0, len(memoryVariables) + 1):
        for subset in itertools.combinations(memoryVariables, k):
            subset = subset + (("Close", "Date"))
            if len(subset) > 4:
                combinationOfColumnValues.append(subset)

    timeCallback = TimeHistory()

    resultsList = []
    for subset in combinationOfColumnValues:
        X, y, Date = prepareMemoryData(stonk, subset)
        model, X_train, y_train, X_test, y_test = runMemory(X, y, Date, subset)
        model.fit(X_train, y_train, epochs=memEpochs, batch_size=memBatchSize,
                  validation_split=0.2, callbacks=timeCallback)
        accuracy = model.evaluate(X_test, y_test, verbose=1)

        epochTimes = timeCallback.times
        for i in epochTimes:
            totalTime += i

        result = str(accuracy/totalTime)

        print("Variables: ", subset)
        # print(f'{model.metrics_names[1]}: {accuracy[1]}')
        # print("Total Time: ", totalTime, " seconds")
        # print("Result (Accuracy/Time): ", result, '\n')

        resultsList.append([subset, accuracy, str(totalTime), result, int(len(subset))])

        totalTime = 0.0
    # -----------------------------------
    df = pd.DataFrame(resultsList, columns=['subset', 'results', 'time', 'score', 'numOfVariables'])
    df.sort_values(by='score', ascending=False, inplace=True)
    df.reset_index(drop=True)

    # -----------------------------------
    optSubSet = df['subset'][0]

    df.to_csv('memSubSet.csv')

    return (optSubSet, df)

# =========================================================
# Main
# =========================================================
def runMemoryOptimization(stonk):
    memoryResults = memoryOptResultClass()

    optSubSet, subDf = memoryVariableOpt(stonk)
    memoryResults.optSubSet = optSubSet
    memoryResults.subDf = subDf
    print("This is the subset df: ", memoryResults.subDf)

    epochDF = epochOpt(stonk)
    memoryResults.epochDF = epochDF

    runHyperOpt(stonk)

    print("==========================")
    print("Memory Optimization")
    print("==========================")
    print(f"{stonk} | Memory Optimize Variable   : {', '.join(list(optSubSet))}  \n")

    return memoryResults
