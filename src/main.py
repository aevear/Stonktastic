"""
.. module:: main
   :synopsis: Runs stonks backend with options for partial runs

.. moduleauthor:: Alexander Hahn <github.com/aevear>
.. moduleauthor:: Kody Richardson <github.com/aevear>

"""

import sys

from stonktastic.config.config import maxHistory, stockToOpt
from stonktastic.databaseCode import initializeStockDatabase, nameListGen
from stonktastic.machinelearning import (
    memoryMain,
    overallEval,
    polyRegMain,
    ranForMain,
    runHistory,
)
from stonktastic.optimization import runPolyRegOptimization, runRanForOptimization


import logging
logging.getLogger('tensorflow').disabled = True

def main(option):
    """
    **Initializes Program**

    Args:
        options (str) : value provided by the user to select which aspect of the program to run. Options are listed below

    =======  ===========
    Options  Description
    =======  ===========
    Full     Erases all data and re-initializes and runs all stages of the project:
    Init     Initializes the database and fills it with data from Yahoo Finance:
    Train    Runs all three machine learning model on data loaded into the db.:
    Stats    Preforms analytics and predictions for each model for each stock.:
    Opt      Preforms the full optimization aspect of the project on whichever stonk is provided in the *config.csv* file:
    =======  ===========

    """

    if option == "full":
        initializeStockDatabase()
        polyRegMain()
        memoryMain()
        ranForMain()
        runHistory()
        overallEval()

    if option == "init":
        initializeStockDatabase()
    else:
        nameListGen()

    if option == "train":
        polyRegMain()
        memoryMain()
        ranForMain()

    if option == "stats":
        runHistory()
        overallEval()

    if option == "opt":
        runPolyRegOptimization(stockToOpt)
        runRanForOptimization(stockToOpt)


if __name__ == "__main__":
    main(sys.argv[1])
