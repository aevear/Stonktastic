"""
Summary:
    Here we import and load the values from *config.csv* into the code. There are no functions. The code uses pandas to load the CSV into a dataframe then sequesters off each part into its own value

**Configuration Values**

    **Variables**

    - *polyVariables* (list) : list of variables that will be used for *Polynomial Regression*.

    - *memVariables* (list) : list of variables that will be used for *mem*.

    - *ranVariables* (list) : list of variables that will be used for *Random Forest*.

    **Settings**

    - *RSILookbackTime* (int) : Number of days we want to look back when calculating *RIS*.

    - *maxSQLPull* (int) : Maximum number of days to look back on from current day when pulling from the SQL database

    - *maxHistory* (int) : Number of trading days in a year.

    - *polyPolynomial* (int) : Polynomial level used in the code. This increases the chance of overfitting if raised too high.

    - *memLookbackTime* (int) : Number of days that we will look back in with the LTMS model.

    - *memLoss* (str) : The method used to calculate *loss* in the mem model.

    - *memActivation* (str) : Value we are using for activation in the mem model.

    - *memOptimizer* (str) : Optimizer used in the mem model.

    - *memEpochs* (int) : Number of Epochs used as a standard for the LTMS model.

    - *memBatchSize* (int) : Number of Neurons simulated in the mem model.

    - *ranForEstimators* (int) : Number of descision trees used in the Random Forest Model.

    - *stockToOpt* (str) : The stock code that will be used when optimizing the program

"""

import numpy as np
import pandas as pd

from stonktastic.config.paths import configLocations

df = pd.read_csv(
    configLocations / "configVariables.csv",
    sep="|",
    dtype=str,
    skip_blank_lines=True,
    header=None,
)
df = df.replace(np.nan, "", regex=True)
df.set_index(0, inplace=True)

polyVariables = df.loc["polyVariables"].values.tolist()
polyVariables = list(filter(None, polyVariables))
memVariables = df.loc["memVariables"].values.tolist()
memVariables = list(filter(None, memVariables))
ranForVariables = df.loc["ranForVariables"].values.tolist()
ranForVariables = list(filter(None, ranForVariables))

RSILookbackTime = int(df.loc["RSILookbackTime"].values.tolist()[0])
maxSQLPull = int(df.loc["maxSQLPull"].values.tolist()[0])
maxHistory = int(df.loc["maxHistory"].values.tolist()[0])
polyPolynomial = int(df.loc["polyPolynomial"].values.tolist()[0])
memLookbackTime = int(df.loc["memLookbackTime"].values.tolist()[0])
memLoss = df.loc["memLoss"].values.tolist()[0]
memActivation = df.loc["memActivation"].values.tolist()[0]
memOptimizer = df.loc["memoptimizer"].values.tolist()[0]
memEpochs = int(df.loc["memEpochs"].values.tolist()[0])
memBatchSize = int(df.loc["memBatchSize"].values.tolist()[0])
ranForEstimators = int(df.loc["ranForEstimators"].values.tolist()[0])

stockToOpt = df.loc["stockToOpt"].values.tolist()[0]
