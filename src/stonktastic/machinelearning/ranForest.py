"""
.. module:: ranForest
   :synopsis: Runs and preforms Random Forest on all stocks found in the DB based on values found in the configuration file.
"""

import pickle

from sklearn.ensemble import RandomForestRegressor

from stonktastic.config.config import ranForEstimators, ranForVariables
from stonktastic.config.paths import modelPaths, nameList
from stonktastic.databaseCode.sqlQueries import updateCalculationsRegistry
from stonktastic.machinelearning.prepDataSets import prepareRanForData


def runRandomForest(xValueList, yValueList, estimators):
    """
    Preforms *Random Forest* based on the arguments provided.

    Args:
        xValueList (list of floats) : List of X values used for random forest. Offset 1 day earlier than the y values so we have something to predict. Prepared by *prepDataSets*. Can change based on the values in saved in the configuration file.
        yValueList (list of floats) : Close values tied to the X value list for the following day.
        estimators (int) : Number of Decision Trees to be used in the calculation

    :return:
        model: The actual machine Learning model.
        float: the R^2 score for the model. (the default value for the *score* function is R^2)
    """
    splitValue = int(len(xValueList) * 0.2)
    xTrain, xTest, yTrain, yTest = (
        xValueList.iloc[:-splitValue],
        xValueList.iloc[splitValue:],
        yValueList[:-splitValue],
        yValueList[splitValue:],
    )

    ranForestModel = RandomForestRegressor(n_estimators=estimators)
    ranForestModel.fit(xTrain, yTrain)

    ranForestModel.score(xTrain, yTrain)
    ranForAccuracy = ranForestModel.score(xTest, yTest)

    return (ranForestModel, ranForAccuracy)


def ranForMain():
    """
    Cycles for every stock in the project, this function prepares the data for the model using the configuration listed in the configuration.csv file

    Results:

    - Saves off the model to the *model* folder for later usage.

    - Records the R^2 value of the model to the *Calculations Registry* table.

    """
    for stonk in nameList:
        xValueList, yValueList, _ = prepareRanForData(stonk, ranForVariables)

        ranForestModel, ranForAccuracy = runRandomForest(
            xValueList, yValueList, ranForEstimators
        )

        filename = modelPaths["ranForModels"] + f"/{stonk}ranForest.sav"
        pickle.dump(ranForestModel, open(filename, "wb"))

        updateCalculationsRegistry(stonk, "ranForScore", ranForAccuracy)

        print(f"{stonk} | Random Forest : {abs(ranForAccuracy)}")
