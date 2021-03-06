# Stonktastic

## Overview of Project

Thank you for taking a look at *Stonktastic*. Please start by taking a look at the documentation

Project Overview: We used *Juputer Notebooks* to record most of the project overview located [here](https://github.com/aevear/Stonktastic/tree/main/notebooks)
- [Data Sources Used](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Data_Source.ipynb)
- [Database Structure](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Database_Structure.ipynb)
- [Development Practices](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Development_Practices.ipynb)
- [Flask](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Flask.ipynb)
- [Installation Instructions](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Installation.ipynb)
- [Python Libraries](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Python_Libraries_Used.ipynb)
- [Stock Technical Indicators](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Stock_Technical_Indicators.ipynb)
- [Structure and Formatting Guide](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Structural_and_Formatting_Guide.ipynb)

Machine Learning Reports
- [Polynomial Regression](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Polynomial_Regression.ipynb)
- [LSTM Recurrent Neural Network](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Memory.ipynb)
- [Random Forest](https://github.com/aevear/Stonktastic/blob/main/notebooks/Documentation_Random_Forest.ipynb)

## Install Conda
*Source* : https://docs.anaconda.com/anaconda/install/
<br>
*Description* :
Conda provides an enviroment to develop projects in without the worry of having to manage multiple versions of libraries and installs. For instance, at the time of this projects writing, *Tensorflow* could not handle python 3.8.1 (current version) and instead could only work with python 3.6. Managing a web of those dependencies between projects can be a huge hassle.

Conda is thus used to keep each project and its dependencies isolated from one another and provide a large enviroment to develop in.

<br>

#### Installing Conda
To install conda, an install program needs to be run on your computer. Use the link above to find the latest copy for each operating system.

<br>

#### Creating a Conda enviroment
The following command creates a new conda enviroment. Change the name of [myenv] to whatever you want your installation to be called. We used *Stonk* for our conda install.
- *conda create -n [myenv] python=3.6*

<br>

#### Activating and Deactivating a Conda Enviroment
This will activate conda in your enviroment. Once active you will need to deactivate it if you want to turn it off.

**Activating Conda**
- *conda activate [myenv]*

**Deactivating Conda**
- *conda deactivate [myenv]*

<br>

## Installing Requirements.txt
By using *pip* one can install all of the dependencies for the project at once and with the correct version.

1. First, navigate to the correct folder (/Stonktastic/)


2. Ensure that you are in a conda enviroment with the below code:
- *conda activate [conda enviroment name]*


3. Use the below code to install all of the dependencies in a batch. Breakdown for each major library used is referenced in the Documentation file *Python Libraries*
- *pip install -r requirements.txt)*

<br>

## Local Editable Install
In order to have greater accessability to the project from outside the direct folder, we will install the project as a *Local Editable Package*. This also helps with the later push to have the finished project downloadable and installable as a package.

The Jupyter notebooks also have easier access with a local install as they only need to import the specific functions in the library from the enviroment rather than using path references.

You can install a project as a local editable install with a *setup.py* file and a *setup.cfg* file.

- *pip install -e .*

<br>

#### setup.py and Setup.cfg
Two files will need to be added to your project in order to preform the local install: *setup.py* and *setup.cfg*. Setup.py requires only two lines of code (refer to projects setup.py for reference) and uses the setup.cfg for the configuration of the local install, namely where it is located and other metadata.

<br>

## Running the Project
Navigate to *Stonktastic/src/* and open the *main.py* file. Listed there are options for running the project. For the first run, its suggested to run the *Full* option as it will preform all tasks nessessary for the project in order.
