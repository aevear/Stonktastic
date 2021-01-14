"""
There are three major groups of code imported here.

Those that directly run the machine learning code

Machine Learning Code
- *polyReg*: Runs *Polynomial Regression*.

- *memory* : Runs *Long Term - Short Term Memory Neural Network*.

- *ranForest* : Runs *Random Forest*.

Preparing Machine Learning Code
- *prepDataSets* : Which prepares the datasets to be run based on the values provided.

Post Processing
- *historicalPred* : Uses the machine learning models to preform historical predictions for reference and graphing.

- *overallEval* : Preforms an analysis on each stock and ranks them against one another.

"""

from stonktastic.machinelearning.historicalPred import runHistory
from stonktastic.machinelearning.memory import memoryMain, runMemory
from stonktastic.machinelearning.overallEval import overallEval
from stonktastic.machinelearning.polyReg import polyRegMain, runPolyReg
from stonktastic.machinelearning.prepDataSets import (
    prepareMemoryData,
    preparePolyRegData,
    prepareRanForData,
)
from stonktastic.machinelearning.ranForest import ranForMain, runRandomForest
