"""
Imports the core five areas of Stonkcastic:

- Config : This has the configuration variables and the pathing

- Database Code : This contains the code that initiatlizes and queries the sql lite database

- Flask : The utility code used by flask to connect to the database

- Machine Learning : Contains the core pages used for Polynomial Regression, Random Forest, Long Short Term Memory code as well as thier supporting documentation

- Optimization : Code for testing the variables used in configuration.

"""
import stonktastic.config
import stonktastic.databaseCode
import stonktastic.machinelearning
import stonktastic.optimization
