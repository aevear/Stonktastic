"""
Summary:
    Using the *pathlib* library we generate path values and dict/key pairs for the location of the models and configuration files.
    This code also connects to the database and generates the connector and cursor values.

**Configuration Values**

    - *Localpath* (path obj) : Path to the project folder.

    - *dbLocation* (path obj) : Path to the Database.

    - *configLocations* (path obj) : Path to where the config variables are saved.

    - *modelLocation* (path obj) : Path to the models Folder.

    - *modelPaths* (dict) : Dict/Key pair for each machine learning model's folder location.

    - *filePaths* (dict) : Dict/Key pair for the configuration files.

    - *dbconnector* (obj) : SQL Lite connector object to the production DB.

    - *dbcursor* (obj) : SQL Lite cursor object for the dbconnector mentioned above.
"""

import sqlite3
from pathlib import Path

localPath = Path(Path.cwd()).parents[0]

dbLocation = localPath / "databases/masterDB.sqlite"
configLocations = localPath / "src/stonktastic/config"
modelLocation = localPath / "models"

modelPaths = {
    "rmmMemoryModels": f"{modelLocation}/ltsmModels",
    "polyRegModels": f"{modelLocation}/polynomialRegressionModels",
    "ranForModels": f"{modelLocation}/randomForestModels",
}

filePaths = {
    "namesFile": f"{configLocations}/stockList.csv",
    "configFile": f"{configLocations}/configVariables.csv",
}

dbconnector = sqlite3.connect(str(dbLocation), check_same_thread=False)
dbcursor = dbconnector.cursor()

nameList = []
