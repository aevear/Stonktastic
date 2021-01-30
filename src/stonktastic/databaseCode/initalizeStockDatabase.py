"""
.. module:: initializeStockDatabase
   :synopsis: Here we initalize the data base, import data from Yahoo Finance, then process the data into the correct tables.
"""

import numpy as np
import pandas as pd
import talib
import yfinance as yf

from stonktastic.config.config import RSILookbackTime
from stonktastic.config.paths import dbconnector, dbcursor, filePaths, nameList
from stonktastic.databaseCode.sqlQueries import (
    nameListGen,
    permFinder,
    pullDataRegistry,
    updateSNPName,
)


def obtainTickerSP500():
    """
    Pulls values from wikipedia to genrate a full list of symbols, securities and GICS Sector values. This is then saved off to a config file for the code to use as a reference.

    :return:
        CSV: Outputs into the config file a CSV with symbol, securities and GICS Sector Values

    """

    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df = table[0]

    pathToOutPut = filePaths["namesFile"]
    df.to_csv(pathToOutPut, columns=["Symbol", "Security", "GICS Sector"], index=False)


def pullHistoricalData(stonk):
    """
    This pulls data from Yahoo Finance and passes it to a function that stores the data in the *stage* table for processing

    Args:
        stonk (str): Stock ticker value that will be pulled from Yahoo Finance

    :return:
        Dictonary: dict/key pair with data from Yahoo finance.

    """
    stockTicker = yf.Ticker(stonk)

    data = stockTicker.history(period="10y")
    data.reset_index(inplace=True)
    dataDict = data.to_dict("records")
    stageData = dataDict

    return stageData


def initializeExchangeRegistry():
    """
    Here we initialize the *Exchange Registry* table that matches each stock with the exchange they are traded on.

    This function does not take any input or return any values, it just initilizes a table in the SQL database
    """

    dbcursor.execute("DROP TABLE IF EXISTS ExchangeRegistry")
    dbconnector.commit()

    dbcursor.execute(
        """
            CREATE TABLE IF NOT EXISTS exchangeRegistry(
                Exchange_ID INTEGER PRIMARY KEY,
                Exchange_Name TEXT NOT NULL,
                Data_Source TEXT NOT NULL);
                """
    )

    # Insert into the Exchange Registry the Information of each Exchange

    dbcursor.execute(
        """
            INSERT INTO exchangeRegistry(Exchange_Name, Data_Source)
            VALUES ('S&P500', 'Yahoo Finance');
            """
    )

    dbconnector.commit()


def initializeStockRegistry():
    """
    Here we initialize the *Stock Registry* table that matches each stock with the their exhange, information and data tables.

    This function does not take any input or return any values, it just initilizes a table in the SQL database
    """

    df = pd.read_csv(filePaths["namesFile"])
    df.reset_index()
    df = df.rename(columns={"GICS Sector": "Sector"})

    dbcursor.execute("DROP TABLE IF EXISTS stockRegistry")
    dbconnector.commit()

    dbcursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stockRegistry(
            Stock_ID INTEGER PRIMARY KEY,
            Symbol nvarchar(50),
            Security nvarchar(50),
            Sector nvarchar(50));
            """
    )

    # Populates StockRegistry table from our list of Stocks in the csv file

    for row in df.itertuples():
        dbcursor.execute(
            """
                INSERT INTO StockRegistry
                (
                Symbol,
                Security,
                Sector
                )
                VALUES (?,?,?)
                """,
            (row.Symbol, row.Security, row.Sector),
        )

    dbconnector.commit()

    updateSNPName()


def initializeIDRegistry():
    """
    Here we initialize the *ID Registry* table that matches each stock with their perm node number and stock exhange number

    This function does not take any input or return any values, it just initilizes a table in the SQL database
    """

    dbcursor.execute("DROP TABLE IF EXISTS IDRegistry")
    dbconnector.commit()

    dbcursor.execute(
        """
                        CREATE TABLE IF NOT EXISTS IDRegistry(
                            Perm_No INTEGER PRIMARY KEY,
                            Exchange_ID INTEGER NOT NULL,
                            Stock_ID INTEGER NOT NULL,
                            FOREIGN KEY (Stock_ID)
                            REFERENCES stockRegistry (Stock_ID),
                            FOREIGN KEY (EXCHANGE_ID)
                            REFERENCES exchangeRegistry (Exchange_ID)
                            );
                            """
    )

    dbconnector.commit()


def populateIDRegistry():
    """
    This function does is generate the connections between the ID registry, exchange registry and stock registry tables.
    """

    dbcursor.execute("""SELECT * FROM exchangeRegistry""")
    exchangeRecords = dbcursor.fetchall()
    for row in exchangeRecords:
        exchangeIdTemp = row[0]
        dbcursor.execute("""SELECT * FROM stockRegistry""")
        stockRecords = dbcursor.fetchall()
        for stock in stockRecords:
            stockIdTemp = stock[0]
            dbcursor.execute(
                """
                    INSERT INTO IDRegistry(Exchange_ID, Stock_ID)
                     VALUES (?,?)""",
                (exchangeIdTemp, stockIdTemp),
            )

    dbconnector.commit()


def initializeStageTable():
    """
    Here we initialize the *Stage* table that is used to load in the data before processing.

    This function does not take any input or return any values, it just initilizes a table in the SQL database
    """

    dbcursor.execute("""DROP TABLE IF EXISTS StageTable""")
    dbconnector.commit()

    dbcursor.execute(
        """
            CREATE TABLE IF NOT EXISTS StageTable(
                Data_ID INTEGER PRIMARY KEY,
                Perm_No INTEGER,
                Date DATE NOT NULL,
                Open DOUBLE,
                High DOUBLE,
                Low DOUBLE,
                Close DOUBLE,
                Volume DOUBLE,
                Dividends DOUBLE,
                Stock_Splits DOUBLE,
                SAR DOUBLE,
                RSI DOUBLE,
                CCI DOUBLE,
                MACDHist DOUBLE,
                BBUpperBand DOUBLE,
                BBMiddleBand DOUBLE,
                BBLowerBand DOUBLE,
                EMA DOUBLE,
                Chaikin DOUBLE,
                StochK DOUBLE,
                StochD DOUBLE,
                WILLR DOUBLE,
                memPred DOUBLE,
                polyreg DOUBLE,
                ranForPred DOUBLE
                );
                """
    )

    dbconnector.commit()


def initializeDataRegistry():
    """
    Here we initialize the *Data Registry* table that stores the daily values for stocks and indicators.

    This function does not take any input or return any values, it just initilizes a table in the SQL database
    """

    dbcursor.execute("""DROP TABLE IF EXISTS DataRegistry""")
    dbconnector.commit()

    dbcursor.execute(
        """
            CREATE TABLE IF NOT EXISTS DataRegistry (
                Data_ID INTEGER PRIMARY KEY,
                Perm_No INTEGER,
                Date DATE NOT NULL,
                Open DOUBLE,
                High DOUBLE,
                Low DOUBLE,
                Close DOUBLE,
                Volume DOUBLE,
                Dividends DOUBLE,
                Stock_Splits DOUBLE,
                SAR DOUBLE,
                RSI DOUBLE,
                CCI DOUBLE,
                MACDHist DOUBLE,
                BBUpperBand DOUBLE,
                BBMiddleBand DOUBLE,
                BBLowerBand DOUBLE,
                EMA DOUBLE,
                Chaikin DOUBLE,
                StochK DOUBLE,
                StochD DOUBLE,
                WILLR DOUBLE,
                memPred DOUBLE,
                polyregPred DOUBLE,
                ranForPred DOUBLE,
                FOREIGN KEY (Perm_No)
                REFERENCES IDRegistry (Perm_No)
                );
                """
    )

    dbcursor.execute(
        """
            CREATE UNIQUE INDEX nix_permno_date ON DataRegistry (Perm_No, Date)
            """
    )

    dbconnector.commit()


def populateStageTable():
    """
    Here we populate the *Stage* table that we used to hold the data before processing them into the correct tables.

    It uses the *Name List Gen* function to get a full list of the stock IDs that are used and then uses the *Pull Historical Data* function to pull from Yahoo before loading in the data.

    Values Loaded from Yahoo Finance:
        - *Date* : Date for the row
        - *Open* : Opening price for the stock that day
        - *High* : Stocks highest value during that day of trading
        - *Low* : Stocks lowest value during that day of trading
        - *Close* : The closing price for the stock during that day of trading
        - *Volume* : Amount of stocks traded during that day of trading
        - *Dividends* : Dividends payed our during the day of trading
        - *Stock Splits* : If the stock split or merged during trading hours, the value of the plit is listed here

    Values Processed Here:
        - *SAR* : Daily Parabolic SAR value for the stock for the given date
        - *RSI* : Daily Relative Strength Index value for the stock for the given date
        - *CCI* : Daily Commodity Channel Index value for the stock for the given date
        - *MACDHist* : Daily Moving Average Convergence Divergence value for the stock for the given date
        - *BBUpperBand* : Daily Upper Bollinger Band's value for the stock for the given date
        - *BBMiddleBand* : Daily Middle Bollinger Band's value for the stock for the given date
        - *BBLowerBand* : Daily Lower Bollinger Band's value for the stock for the given date
        - *EMA* : Daily Exponential Moving Average value for the stock for the given date
        - *Chaikin* : Daily Chaikin Oscillator value for the stock for the given date
        - *StockK* : Daily Stochastics K value for the stock for the given date
        - *StockD* : Daily Stochastics D value for the stock for the given date
        - *WILLR* : Daily Williams Percent Range value for the stock for the given date
    """

    nameListGen()

    for symbol in nameList:
        data = pullHistoricalData(symbol)

        processedData = []
        for idx, k in enumerate(data):
            hold = [
                str(k["Date"]),
                str(k["Open"]),
                str(k["High"]),
                str(k["Low"]),
                str(k["Close"]),
                str(k["Volume"]),
                str(k["Dividends"]),
                str(k["Stock Splits"]),
            ]
            processedData.append(hold)
        df = pd.DataFrame(
            processedData,
            columns=[
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Dividends",
                "Stock Split",
            ],
        )

        df["SAR"] = talib.SAR(df["High"], df["Low"], acceleration=0.02, maximum=0.2)
        df["RSI"] = talib.RSI(df["Close"], RSILookbackTime)
        df["CCI"] = talib.CCI(df["High"], df["Low"], df["Close"])
        _, _, df["macdhist"] = talib.MACD(
            df["Close"], fastperiod=12, slowperiod=26, signalperiod=9
        )
        df["upperband"], df["middleband"], df["lowerband"] = talib.BBANDS(
            df["Close"], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0
        )
        df["EMA"] = talib.EMA(df["Close"], timeperiod=30)
        df["Chaikin"] = talib.ADOSC(
            df["High"],
            df["Low"],
            df["Close"],
            df["Volume"],
            fastperiod=3,
            slowperiod=10,
        )
        df["stochK"], df["stochD"] = talib.STOCH(
            df["High"],
            df["Low"],
            df["Close"],
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0,
        )
        df["WILLR"] = talib.WILLR(df["High"], df["Low"], df["Close"], timeperiod=14)

        perm = permFinder(symbol)
        for idx in range(len(df)):
            values = (
                perm,
                df.at[idx, "Date"],
                df.at[idx, "Open"],
                df.at[idx, "High"],
                df.at[idx, "Low"],
                df.at[idx, "Close"],
                df.at[idx, "Volume"],
                df.at[idx, "Dividends"],
                df.at[idx, "Stock Split"],
                df.at[idx, "SAR"],
                df.at[idx, "RSI"],
                df.at[idx, "CCI"],
                df.at[idx, "macdhist"],
                df.at[idx, "upperband"],
                df.at[idx, "middleband"],
                df.at[idx, "lowerband"],
                df.at[idx, "EMA"],
                df.at[idx, "Chaikin"],
                df.at[idx, "stochK"],
                df.at[idx, "stochD"],
                df.at[idx, "WILLR"],
            )

            dbcursor.execute(
                """
                                    INSERT INTO StageTable
                                        (
                                        Perm_No,
                                        Date,
                                        Open,
                                        High,
                                        Low,
                                        Close,
                                        Volume,
                                        Dividends,
                                        Stock_Splits,
                                        SAR,
                                        RSI,
                                        CCI,
                                        MACDHist,
                                        BBUpperBand,
                                        BBMiddleBand,
                                        BBLowerBand,
                                        EMA,
                                        Chaikin,
                                        StochK,
                                        StochD,
                                        WILLR
                                        )
                                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                values,
            )

        dbconnector.commit()


def loadDataRegistry():
    """
    Moves data from the *Stage* table to the *Data Registry* table
    """

    dbcursor.execute(
        """
            INSERT OR REPLACE INTO DataRegistry
            (
                Data_ID,
                Perm_No,
                Date,
                Open,
                High,
                Low,
                Close,
                Volume,
                Dividends,
                Stock_Splits,
                SAR,
                RSI,
                CCI,
                MACDHist,
                BBUpperBand,
                BBMiddleBand,
                BBLowerBand,
                EMA,
                Chaikin,
                StochK,
                StochD,
                WILLR
            )
            SELECT
                ST.Data_ID,
                ST.Perm_No,
                ST.Date,
                ST.Open,
                ST.High,
                ST.Low,
                ST.Close,
                ST.Volume,
                ST.Dividends,
                ST.Stock_Splits,
                ST.SAR,
                ST.RSI,
                ST.CCI,
                ST.MACDHist,
                ST.BBUpperBand,
                ST.BBMiddleBand,
                ST.BBLowerBand,
                ST.EMA,
                ST.Chaikin,
                ST.StochK,
                ST.StochD,
                ST.WILLR
            FROM StageTable ST
                 LEFT JOIN DataRegistry DR
                 ON DR.Perm_No = ST.Perm_No
                 AND DR.Date = ST.Date
            WHERE DR.Data_ID IS NULL
            """
    )

    dbcursor.execute(
        """
            DELETE FROM StageTable"""
    )

    dbconnector.commit()


def initializeCalculationsRegistry():
    """
    Here we initialize the *Calculations Registry* table where we store data on each stock's overall (not daily) values.

    This function does not take any input or return any values, it just initilizes a table in the SQL database
    """

    dbcursor.execute("""DROP TABLE IF EXISTS CalculationsRegistry""")
    dbconnector.commit()

    dbcursor.execute(
        """
                CREATE TABLE IF NOT EXISTS CalculationsRegistry(
                    Perm_No INTEGER PRIMARY KEY,
                    StandardDeviation DOUBLE,
                    ValueScore DOUBLE,
                    polyregScore DOUBLE,
                    MemoryScore DOUBLE,
                    ranForScore Double,
                    BestModel STRING,
                    PolyProfit DOUBLE,
                    MemProfit DOUBLE,
                    RanProfit DOUBLE,
                    YearProfit DOUBLE
                    );
                    """
    )
    dbconnector.commit()


def performInitialCalculations():
    """
    Generates the *Standard Deviation* value for each stock before storing it in the *Calculations Registry* table.
    """

    for symbol in nameList:

        codes = pullDataRegistry(symbol, "Low", "High")
        values = []

        for k in codes:
            values.append([float(k[0]), float(k[1])])
        standardDeviation = np.std(values)

        perm = permFinder(symbol)

        dbcursor.execute(
            """
            INSERT OR REPLACE INTO CalculationsRegistry
            (
            Perm_No,
            StandardDeviation
            )
            VALUES (?,?)""",
            (
                int(perm),
                standardDeviation,
            ),
        )

    dbconnector.commit()


def initializeStockDatabase():
    """
    The *Main* function for pulling data, loading data and initatlizing data for the database

    Results :
        Initalized and fleshed out database with all the basic information and indicators loaded into the db
    """
    # Database initialization
    initializeExchangeRegistry()
    initializeStockRegistry()
    initializeIDRegistry()
    initializeStageTable()
    initializeDataRegistry()
    initializeCalculationsRegistry()

    # Calcuations and Table Population
    populateIDRegistry()
    populateStageTable()
    loadDataRegistry()
    performInitialCalculations()
