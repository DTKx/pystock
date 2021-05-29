"""
Calculate net monthly result per month.
First: Creates a net_per_stock table that is evaluated by month and aggregates buy, sell operations.
Second: Calculates the net profit per month.
"""
import pandas as pd
import os
import pdfplumber
import re
import json, codecs

# import pystock.helpersio as hio#Running from package perspective
import helpersio as hio
import sys

HEADERS_TABLE_NET_PER_STOCK = [
    "Month Year",
    "Ticker",
    "Available Quantity units",
    "Average Buy Price brl_unit",
    "Sold Quantity units",
    "Average Sell Price brl_unit",
    "Profit per unit brl_per_unit",
    "Profit brl",
    "Remain Quantity units",
    "Remain Operation value w taxes brl",
]


def _load_table_net_per_stock(path):
    if os.path.exists(path) == False:
        print(
            f"Could not find the path {path}, a new table for net_per_stock will be created."
        )
        a = []
        hio.export_to_csv_from_lists(a, path)
    b = hio.read_csv(path)
    return b


def _is_year_correct(y, nested_list):
    date_file = nested_list[1][14].split("/")[1:]  # Tests for the first instance only
    if y == (date_file[1]):
        return True
    else:
        raise ValueError(
            "Search year do not match, please verify the input file and date being searched."
        )


def _is_month_year_correct(m, y, nested_list, i=1):
    date_file = nested_list[i][14].split("/")[1:]  # Tests for the first instance i
    if (m == (date_file[0])) & (y == (date_file[1])):
        return True
    else:
        raise ValueError(
            f"Search year and month do not match {date_file}, please verify the input file and date being searched."
        )


def get_month(date):
    """Extract month as form receiving string dd/mm/yyyy or mm/yyyy

    Args:
        date (string): Date formate dd/mm/yyyy

    Returns:
        mm: string with month.
    """
    num_chars = len(date)
    if num_chars == 10:
        return date.split("/")[1]
    elif num_chars == 7:
        return date.split("/")[0]


def _search_col(key, col, a, lo, hi, trans_function=None, transformation=False):
    """Search key in col of a nested list, performs the lower boundary search in case of repeated values.

    Args:
        key (comparable): key to search
        col (int): index of column to search key
        a (list): nested list
        lo (int): Lower index
        hi (int): Higher index
        trans_function (function, optional): Function to preprocess column content before comparison with the key. Defaults to None.
        transformation (bool, optional): Marks if the function will use the preprocess function. Defaults to False.

    Returns:
        [type]: [description]
    """
    if lo >= hi:
        if transformation:
            try:
                val = trans_function(a[lo][col])
            except IndexError:
                # print("IndexError")
                # TODO:Create an improved function to create a set of months that contain notas so this would be avoided
                return -1  # Not found
        else:
            val = a[lo][col]
        if val == key:
            return lo
        else:
            return -1  # Not found
    mid = lo + (hi - lo) // 2
    if transformation:
        val = trans_function(a[mid][col])
    else:
        val = a[mid][col]
    if val >= key:
        return _search_col(
            key, col, a, lo, mid, trans_function, transformation
        )  # Binary Search Lower bound
    else:  # val < key
        return _search_col(key, col, a, mid + 1, hi, trans_function, transformation)


def _search_previous_col(key, col, a, trans_function=None, transformation=False):
    prev_index = -1
    for i, row in enumerate(a):
        if transformation:
            val = trans_function(row[col])
        else:
            val = row[col]
        if val < key:
            prev_index = i
        else:
            break
    return prev_index


def _search_previous_next_col(key, col, a, trans_function=None, transformation=False):
    prev_index = -1
    next_index = -1
    for i, row in enumerate(a):
        if transformation:
            val = trans_function(row[col])
        else:
            val = row[col]
        if val < key:
            prev_index = i
        elif val == key:
            continue
        else:  # Found next
            next_index = i
            break
    if next_index == -1:
        next_index = len(a)
    if prev_index == -1:
        prev_index = 0
    return prev_index, next_index


def _get_index_range_search_col(
    m, col, nested_list, trans_function=None, transformation=False
):
    """Return lower and greatest range for previous index of a key and index of the first higher key than search key. Receives as input a sorted nested list where a key is being seached in the col number.Returns 1,1(Considers receiving headers in data) if value is not contained. 

    Args:
        m (comparable): comparable being searched
        col (int): Column number to be searched.
        nested_list (list): Nested List with the values being searched. Ex [[0,1,2,2][0,1,2,2]] First inner list represents a row of attributes of an instance.
        trans_function (func): Function to transform the comparison value of the column.    
        transformation (boolean): If true uses a tranformation in the column value before comparison of the values.

    Returns:
        int,int: Index of the previous key being searched, first index of the next key of the key  being searched. Ex: key=3 list=[1,3,3,5] returns 0,3
    """
    if nested_list:
        lo, hi = _search_previous_next_col(
            m, col, nested_list, trans_function, transformation
        )
        return lo, hi
    else:  # No history of previous Stocks
        return 0, 0


def _get_previous_index_search_col(
    m, col, nested_list, trans_function=None, transformation=False
):
    """Return previous index of a a key, from a sorted nested list where a key is being seached in the col number.Returns -1 if value is not found. 

    Args:
        m (comparable): comparable being searched
        col (int): Column number to be searched.
        nested_list (list): Nested List with the values being searched. Ex [[0,1,2,2][0,1,2,2]] First inner list represents a row of attributes of an instance.
        trans_function (func): Function to transform the comparison value of the column.    
        transformation (boolean): If true uses a tranformation in the column value before comparison of the values.

    Returns:
        int: Index of the value being searched.
    """
    ix = _search_previous_col(m, col, nested_list, trans_function, transformation)
    assert ix != -1, f"Previous keyword to {m} was not found."
    return ix


def _get_first_index_search_col(
    m, col, nested_list, trans_function=None, transformation=False
):
    """Return first index of a sorted nested list where a key is being seached in the col number.Returns -1 if value is not found. 

    Args:
        m (comparable): comparable being searched
        col (int): Column number to be searched.
        nested_list (list): Nested List with the values being searched. Ex [[0,1,2,2][0,1,2,2]] First inner list represents a row of attributes of an instance.
        trans_function (func): Function to transform the comparison value of the column.    
        transformation (boolean): If true uses a tranformation in the column value before comparison of the values.

    Returns:
        int: Index of the value being searched or -1 in case no notas was found in the month.
    """
    ix = _search_col(
        m, col, nested_list, 0, len(nested_list), trans_function, transformation
    )
    if ix == -1:  # Not found
        print(f"No Notas was found for month {m}.")
    return ix


def get_stocks_per_ticker_previous_month_year(ticker, net_per_stock):
    """Get Previous month stock infos per ticker. If not found return zeros.

    Args:
        ticker (string): Ticker string
        net_per_stock (list): List containing historic information of stock wallet.

    Returns:
        int,int: prev_units=Units in wallet in previous month,prev_value=Value in wallet in previous month
    """
    print(ticker)
    # TODO:Implement a verification of month year in the case prev month is from another year
    ix_prev_ticker = -1
    for k in range(len(net_per_stock) - 1, -1, -1):
        if net_per_stock[k][1] == ticker:
            ix_prev_ticker = k
    if ix_prev_ticker == -1:
        return 0, 0
    else:
        return net_per_stock[ix_prev_ticker][-2], net_per_stock[ix_prev_ticker][-1]


def get_stocks_per_ticker_at_month_year(ticker, net_per_stock, month, year):
    """Get month stock infos per ticker at month.

    Args:
        ticker (string): Ticker string
        net_per_stock (list): List containing historic information of stock wallet.
        month (comparable): Month  to be searched information.
        year (comparable): Year  to be searched information.

    Returns:
        int,int: units=Units in wallet at search month,prev_value=Value in wallet at search month
    """
    if len(net_per_stock) == 1:  # No history of previous Stocks
        return 0, 0
    elif get_month(net_per_stock[1][0]) < month:  # No history of previous Stocks
        return 0, 0
    else:
        i = _get_first_index_search_col(
            month, 0, net_per_stock, get_month, True
        )  # Month Year is within col 0
        return net_per_stock[i][10], net_per_stock[i][11]


def get_previous_month_year(m, y, type_out="int"):
    m = int(m)
    y = int(y)
    if m == 1:
        m = 12
        y -= 1
    else:
        m -= 1
        y -= 1
    if type_out == "int":
        return m, y
    elif type_out == "str":
        return str(m), str(y)
    else:
        raise ValueError(f"Type of output return {type_out} non recognized.")


def _append_net_per_stock_for_month(net_per_stock, month_year, negocios_realizados):
    """Append to list net operations per stock for month_year. Consolidates all buy, sell and remaining operations per month (including older ones) per ticker.

    Args:
        net_per_stock (list): List of table net_per_stock sorted by ascending date that will receive the values.
        month_year (string): String containg month and year to be appended in the format "03/2019"
        negocios_realizados (list): List of table negocios_realizados sorted by ascending date with the table with the notas de corretagem for the month to be appended .
    """
    m, y = month_year.split("/")
    assert _is_year_correct(y, negocios_realizados)
    list_notas = negocios_realizados.copy()

    cur_ix = _get_first_index_search_col(
        m, 14, list_notas, get_month, True
    )  # Month is within col 14
    if cur_ix == -1:  # No notas was found in the month
        return
    assert _is_month_year_correct(m, y, list_notas, i=cur_ix)

    prev_ix, next_ix = _get_index_range_search_col(m, 14, list_notas, get_month, True)

    # assert _is_month_year_correct(m, y, list_notas, i=lo)
    # assert _is_month_year_correct(m, y, list_notas, i=hi)

    seen_tickers = set()
    for i in range(cur_ix, next_ix):  # Loop per ticker of the month
        ticker = negocios_realizados[i][6]
        if ticker in seen_tickers:
            continue
        print(ticker," ",m)
        seen_tickers.add(ticker)
        line = [month_year, ticker]
        buy_units = 0
        buy_value = 0
        sell_units = 0.0
        sell_value = 0.0
        sell_value_with_ops_cost = 0.0
        for k in range(prev_ix, next_ix):  # Loop all notas
            if ticker == negocios_realizados[k][6]:
                if negocios_realizados[k][3] == "C":  # compra
                    buy_units += int(negocios_realizados[k][8])
                    buy_value += float(negocios_realizados[k][10]) + float(
                        negocios_realizados[k][13]
                    )  # Valor operacao+Taxas
                elif negocios_realizados[k][3] == "V":  # Venda
                    sell_units += int(negocios_realizados[k][8])                   
                    sell_value += float(negocios_realizados[k][10])
                    sell_value_with_ops_cost += sell_value + float(
                        negocios_realizados[k][13]
                    )

        prev_units, prev_value = get_stocks_per_ticker_previous_month_year(
            ticker, net_per_stock
        )

        bought_units = buy_units + prev_units
        avg_buy_price = (
            round((buy_value + prev_value) / bought_units, 2)
            if bought_units > 0.01
            else 0.0
        )#includes operation costs
        avg_sell_price = round(sell_value / sell_units, 2) if sell_units > 0.01 else 0.0
        avg_unit_profit_loss = (
            round(avg_sell_price - avg_buy_price, 2) if sell_units > 0.01 else 0.0
        )
        avg_sell_price_with_ops_cost = round(sell_value_with_ops_cost / sell_units, 2) if sell_units > 0.01 else 0.0
        avg_unit_profit_loss_with_ops_cost=(
            round(avg_sell_price_with_ops_cost - avg_buy_price, 2) if sell_units > 0.01 else 0.0
        )

        net_units = prev_units + buy_units - sell_units
        net_value = (
            0.0 if net_units > 0.01 else round(prev_value + buy_value - sell_value, 2)
        )

        line.extend(
            [
                bought_units,  # Number of units in wallet
                avg_buy_price,  # Average price per stock bought considers stocks in wallet
                sell_units,  # Number sold units
                avg_sell_price,  # Average price per stock sold
                avg_unit_profit_loss,  # Unit profit per stock
                avg_unit_profit_loss_with_ops_cost,# Unit profit per stock including sales operations costs
                round(avg_unit_profit_loss * sell_units, 2),  # Profit/loss value
                net_units,
                net_value,
            ]
        )
        print(line)
        net_per_stock.append(line)


def _create_net_per_stock_year_balance(net_per_stock):
    """Create a net per stock_year_balance that consolidates owned assets in the end of december.

    Args:
        net_per_stock (list): Nested list containing stock informations per transaction.

    Returns:
        list: Nested list containing the stock_year_balance in december of the current year. This list must be passed for the next year for proper balance.
    """
    COL_AVAILABLE_STOCKS = 8
    COL_TICKER = 1
    COL_DATE = 0

    next_year = int(net_per_stock[0][0].split("/")[1])+1
    net_per_stock_year_balance = []
    set_tickers_seen = set()
    for i in range(len(net_per_stock)-1,-1,-1):  # Loop latest months first
        ticker = net_per_stock[i][COL_TICKER]
        print(ticker)
        if ticker not in set_tickers_seen:
            set_tickers_seen.add(ticker)
            if net_per_stock[i][COL_AVAILABLE_STOCKS] >= 0.01:  # Has stocks
                line=net_per_stock[i].copy()
                line[COL_DATE] = f"00/{next_year}"
                print(net_per_stock[i])
                net_per_stock_year_balance.append(line)
                print(line)
    return net_per_stock_year_balance


def main():
    cur_year = 2019
    prev_year = cur_year - 1

    data_processed_notas_path_cur_year = os.path.abspath(
        os.path.join(f"data/processed/{cur_year}/btg/notas_corretagem/")
    )
    data_processed_notas_path_prev_year = os.path.abspath(
        os.path.join(f"data/processed/{prev_year}/btg/notas_corretagem/")
    )
    negocios_realizados = hio.read_csv(
        os.path.join(
            data_processed_notas_path_cur_year, f"negocios_realizados_{cur_year}.csv"
        )
    )
    try:
        net_per_stock = _load_table_net_per_stock(
            os.path.join(
                data_processed_notas_path_prev_year, f"net_per_stock_balance{prev_year}.csv"
            )
        )
    except FileNotFoundError:
        print("No previous stock data found.")
        net_per_stock=[]
    # TODO:Fix range of 1,13. Verify the potential breaks given the change of the year.
    for i in range(1, 13):
        if i < 10:
            date = f"0{i}/{cur_year}"
        else:
            date = f"{i}/{cur_year}"
        _append_net_per_stock_for_month(net_per_stock, date, negocios_realizados)
    net_per_stock_df = pd.DataFrame(net_per_stock)
    net_per_stock_df.to_csv(os.path.join(data_processed_notas_path_cur_year,f"net_per_stock{cur_year}.csv"),header=0,index=False)

    net_per_stock_year_balance = _create_net_per_stock_year_balance(net_per_stock)

    net_per_stock_year_balance_df = pd.DataFrame(net_per_stock_year_balance)
    net_per_stock_year_balance_df.to_csv(os.path.join(data_processed_notas_path_cur_year,f"net_per_stock_year_balance{cur_year}.csv"),header=0,index=False)

    print(net_per_stock)
    # net_per_stock[1][0]


if __name__ == "__main__":
    main()
