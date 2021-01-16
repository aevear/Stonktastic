"""
.. module:: sqlQueries
   :synopsis: List of functions used to query the SQL database
"""

import pandas as pd
from pathlib import Path
import sqlite3

def nameListGen():
    """
    Summary:
        Generates a list used by many of the functions that contains all of the stock ticker values currently loaded into the SQL database.

    :results:
        nameList (list): list is stored in *paths* module and is updated to contain all current stock tickers.
    """
    names = dbcursor.execute("SELECT Symbol FROM stockRegistry")
    nameList = []
    for k in names:
        nameList.append(k[0])
    return nameList


def pullDataRegistry(ticker, *args):
    """
    Very used function that takes the ticker values and args to query the *Data Registry* table

    Args:
        ticker (type) : The stock ticker value to be queried
        *args (str) : Fields in the db that the caller wants pulled

    :return:
        cursor object: Returns a sql cursor object that needs to be parsed for results.

    """
    parameters = []

    if len(args) == 1:
        if isinstance(args, tuple):
            parameters = ", ".join(list(args)[0])
    else:
        for k in args:
            parameters.append(f"{k}, ")
        parameters = "".join(parameters)[:-2]

    try:  # if the value has dates
        query = f"""SELECT {parameters}
                     FROM DataRegistry DR
                         INNER JOIN IDRegistry ID
                             ON DR.Perm_No = ID.Perm_No
                         INNER JOIN stockRegistry SR
                             ON ID.Stock_ID = SR.Stock_ID
                     WHERE Symbol = ?
                     ORDER BY Date DESC LIMIT {1764}
                  """
        data = dbcursor.execute(query, (ticker,))
        return data

    except BaseException:  # if the value is not based on dates
        query = f"""SELECT {parameters}
                     FROM DataRegistry DR
                         INNER JOIN IDRegistry ID
                             ON DR.Perm_No = ID.Perm_No
                         INNER JOIN stockRegistry SR
                             ON ID.Stock_ID = SR.Stock_ID
                     WHERE Symbol = ?
                  """
        data = dbcursor.execute(query, (ticker,))
        return data


def pullCalculationsRegistry(*args):
    """
    Used to query the *Calculations Registry* table for overview information on all stocks.

    Does not distinguish between stock tickers

    Args:
        args (list of strings): Desired values queried from *Calcuations Registry*.

    :return:
        cursor object: Returns a sql cursor object that needs to be parsed for results.
    """
    parameters = []

    for k in args:
        parameters.append(f"CR.{k}, ")
    parameters = "".join(parameters)[:-2]

    query = f"""SELECT SR.Symbol, SR.Security, {parameters}
                 FROM CalculationsRegistry CR
                     INNER JOIN IDRegistry ID
                         ON CR.Perm_No = ID.Perm_No
                     INNER JOIN stockRegistry SR
                         ON ID.Stock_ID = SR.Stock_ID
              """
    data = dbcursor.execute(query)
    return data


def pullStockRegistry(ticker, *args):
    """
    Used to query the *Stock Registry* table for connections between stock calculations table, data registry table and other information.

    Args:
        ticker (str): Stock ticker value to be queried
        args (list of strings): Desired values queried from *Stock Registry*.

    :return:
        cursor object: Returns a sql cursor object that needs to be parsed for results.
    """
    parameters = []

    # Build the Query list - max of ten, anything over is set to blank

    for k in args:
        parameters.append(f"{k}, ")
    parameters = "".join(parameters)[:-2]

    query = f"""SELECT {parameters}
                 FROM stockRegistry
                 WHERE Symbol = "{ticker}"
              """

    data = dbcursor.execute(query)
    return data


def pullRankedTopStocksDataCalculationRegistry():
    """
    Used with the flask code, it pulls the top five stock ticker values based on YearProfit value found in the *Calculations Registry* table.

    :return:
        cursor object: Returns a sql cursor object with five ticker values that needs to be parsed for results.

    """
    query = """SELECT SR.Symbol, CR.YearProfit
                 FROM StockRegistry SR
                     INNER JOIN IDRegistry ID
                         ON ID.Stock_ID = SR.Stock_ID
                     INNER JOIN CalculationsRegistry CR
                         ON ID.Perm_No = CR.Perm_No
                 ORDER BY CR.ValueScore DESC
             """

    data = dbcursor.execute(query)
    return data


def updateDataRegistry(ticker, date, column, value):
    """
    Updates the *Data Registry* table based on the Args listed below.

    Args:
        ticker (str): Ticker value to be updated
        date (date): Date value that is to be updated
        column (str): which column needs to be updated
        value (varies): the value that the ticker/date/column combo will be changed to. Can be str, float or int

    """
    perm = permFinder(ticker)
    query = f"""
                UPDATE DataRegistry
                SET {column} = {value}
                WHERE Perm_No = {perm} AND Date = ?
              """

    dbcursor.execute(query, (date,))
    dbconnector.commit()


def updateCalculationsRegistry(ticker, column, value):
    """
    Updates the *Calcuations Registry* table based on the Args listed below.

    Args:
        ticker (str): Ticker value to be updated
        column (str): which column needs to be updated
        value (varies): the value that the ticker/date/column combo will be changed to. Can be str, float or int
    """
    perm = permFinder(ticker)
    query = f"""
                UPDATE CalculationsRegistry
                SET {column} = {value}
                WHERE Perm_No = {perm}
             """

    dbcursor.execute(query)
    dbconnector.commit()


def updateSNPName():
    """
    This function does is change the name of the SNP 500 from ^GSPC to SNP for easy of use during the program.
    """
    query = """
                UPDATE stockRegistry
                SET Symbol = "SNP"
                WHERE Symbol = "^GSPC"
             """

    dbcursor.execute(query)
    dbconnector.commit()


def permFinder(ticker):
    """
    Used internally for other sql queries, this function takes the *ticker* value provided and returns the *perm node* number.

    Perm node is used to speed up queries but is not very user friendly, so we have this code to bridge the gap.

    Args:
        ticker (str): ticker value to referenced for perm node number

    :return:
        perm (int): perm node number that references the stock ticker to be queried.
    """
    query = """
                  Select Perm_No
                  FROM IDRegistry ID
                    INNER JOIN stockRegistry SR
                        ON ID.Stock_ID = SR.Stock_ID
                  WHERE Symbol = ?"""

    perm = dbcursor.execute(query, (ticker,)).fetchall()
    perm = perm[0][0]
    return perm


def pullFullEstimates():
    """
    Used with *Historical Markings* this function pulls a full list of all estimates for all stocks in the *Data Registry* table.

    :return:
        data (list of dict/key pairs with ticker (str) and df (dataframe): List of dataframes containing the *Close*, *Date*, *polyPred*, *memPred*, *ranPred* values for each stock

    """
    results = {}
    for stonk in nameList:
        query = f"""SELECT DR.Close, DR.Date, DR.polyRegPred, DR.memPred, DR.ranForPred
                 FROM DataRegistry DR
                     INNER JOIN IDRegistry ID
                         ON DR.Perm_No = ID.Perm_No
                     INNER JOIN stockRegistry SR
                         ON ID.Stock_ID = SR.Stock_ID
                 WHERE Symbol = ?
                 ORDER BY Date DESC LIMIT {252}
              """

        data = dbcursor.execute(query, (stonk,))

        preDfData = []
        for k in data:
            preDfData.append(k)
        df = pd.DataFrame(
            data=preDfData, columns=["Close", "Date", "polyPred", "memPred", "ranPred"]
        )

        results.update({stonk: df})

    return results


localPath = Path(Path.cwd()).parents[0]
dbLocation = localPath / "databases/masterDB.sqlite"

dbconnector = sqlite3.connect(str(dbLocation), check_same_thread=False)
dbcursor = dbconnector.cursor()

nameList = nameListGen()
