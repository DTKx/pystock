# Pystock
Package to support stock management of common shares for filling brazilian IFRS.
Capabilities
- Capability 1: Parses notas de corretagem from PDF format (BTG broker), generating a consolidated table with Notas de Corretagem information performed to support IFRS declaration.
![Table Negocios Realizados parsed from PDF format.](https://github.com/DTKx/pystock/blob/main/images/negocios_realizados.PNG)
- Capability 2: Calculate average prices per stocks per months.
![Table Net Per Stock generated from previous table.](https://github.com/DTKx/pystock/blob/main/images/net_per_stock.PNG)
- Capability 3: Calculate owned assets in the end of the year, that should be declared in IFRS assets. This helps to verify if it is matching with information shared by the broker.
![Table Net Per Stock Year Balance, showing the remaining assets in end of year.](https://github.com/DTKx/pystock/blob/main/images/net_per_stock_year_balance.PNG)
- Capability 4: Calculate aggregated monthly Profit/Loss, to support monthly Profit/Loss declared in IFRS. Also supporting the management of taxes over profits.
![Table Monthly Profit Loss, presenting aggregated monthly profit/loss.](https://github.com/DTKx/pystock/blob/main/images/monthly_loss.PNG)


## Content
- [Motivation](#motivation)
- [Objective](#objective)
- [Installation](#installation)
- [Usage](#usage)
- [License](#licence)

## Motivation
The IFRS declaration for stock trade common shares might be time consuming as well as require extensive manual data entry.
Moreover it requires having an excel sheet to support the management of information, that might also require some data entry time.
Time that could be used in higher value added activities such as defining investment strategy.

## Objective
Improve the experience, precision and time efficiency of small investors managing IRFS stock trade of common shares informations.
Through the creation of a tool that automatically calculates information for IFRS common share stock trade directly from the PDF received from the broker (BTG).

## Installation

### Python
Please install [Python](https://www.python.org/downloads/).

### Creating the virtual environment
One may install the necessary packages in a simplified manner using pip or conda.

Using pip on cmd:
```
pip install -r environment.yml
```
#### Anaconda (Optional)
Please install the python package manager [Anaconda](https://www.anaconda.com/products/individual).

Using Conda terminal:
```
conda env create -f environ.yml
```


## Usage

An example for using the package to parse a PDF file with Notas de Corretagem of the broker BTG can be found in the file run.py.
One can use the run.py as an execution script, just makking sure to configure correctly the data paths: data_raw_notas_path (path with the file to be parsed),inputPath (Assuring the correct name of the file), data_processed_notas_path (path to store the output data). 

After activating the virtual environment created, execute the file run.py on cmd.
```
python run.py
```

<!--
## License
-->
# pystock
