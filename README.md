# Pystock
Package to support stock management for brazilian IFRS.
Capabilities
- Capability 1: Parses notas de corretagem in PDF format of BTG broker, generating a consolidated table with Notas de Corretagem information performed to support IFRS declaration.

## Content
- [Motivation](#motivation)
- [Objective](#objective)
- [Installation](#installation)
- [Usage](#usage)
- [License](#licence)

## Motivation

## Objective

### Input
- Capability 1:
	- Notas de corretagem do BTG no formato PDF

### Output
- Capability 1:
	- Table with stock operations performed.
	- Table with costs of transaction operations.

## Installation
<!--

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
conda env create -f environment.yml
```

-->


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
