"""
.. module:: polyReg
   :synopsis: Runs and preforms Polynomial regression on all stocks found in the DB based on values found in the configuration file.
"""

import pickle

from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

from stonktastic.config.config import polyPolynomial, polyVariables
from stonktastic.config.paths import modelPaths, nameList
from stonktastic.databaseCode.sqlQueries import updateCalculationsRegistry
from stonktastic.machinelearning.prepDataSets import preparePolyRegData


def runPolyReg(xValueList, yValueList, degrees):
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

    splitValue = int(len(xValueList) * 0.2)
    xTrain, xTest, yTrain, yTest = (
        xValueList.iloc[:-splitValue],
        xValueList.iloc[splitValue:],
        yValueList[:-splitValue],
        yValueList[splitValue:],
    )

    polyreg = make_pipeline(PolynomialFeatures(degree=degrees), LinearRegression())

    polyreg.fit(xTrain, yTrain)
    yPred = polyreg.predict(xTest)

    results = metrics.rmse_score(yTest, yPred)

    return (polyreg, results)


def polyRegMain():
    """
    Cycles for every stock in the project, this function prepares the data for the model using the configuration listed in the configuration.csv file

    Results:

    - Saves off the model to the *model* folder for later usage.

    - Records the R^2 value of the model to the *Calculations Registry* table.

    """
    for stonk in nameList:

        xValueList, yValueList, _ = preparePolyRegData(stonk, polyVariables)

        polyreg, results = runPolyReg(xValueList, yValueList, polyPolynomial)

        filename = modelPaths["polyRegModels"] + f"/{stonk}PolyReg.sav"
        pickle.dump(polyreg, open(filename, "wb"))

        updateCalculationsRegistry(stonk, "PolyRegScore", abs(results))

        print(f"{stonk} | Polynomial Regression : {abs(results)}")
