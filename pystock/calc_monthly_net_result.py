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

import pystock.helpersio as hio#Running from package perspective
# import helpersio as hio
import sys



HEADERS_TABLE_NET_PER_STOCK = [
    "Month Year",
    "Ticker",
    "Available Quantity units",
    "Average Buy Price brl_unit",
    "Sold Quantity units",
    "Average Sell Price without sales operations costs brl_unit",
    "Profit Loss without sales operations costs brl_per_unit",
    "Profit Loss with sales operations costs per unit brl_per_unit",
    "Profit Loss brl",
    "Remain Quantity units",
    "Remain Operation value with sales operations costs brl",
]
HEADERS_MONTHLY_PROFIT_LOSS=["Month Year","Initial assets brl","Total transactions brl","Total profitloss without sales costs brl","Total profitloss with sales costs brl","Ratio Profit to assets sold percentage ","Remaining Assets brl"]



def _transform_str_numeric_read_negocios_realizados(row):
    """Transformation fucntion from string to numeric for rows of table net_per_stock.

    Args:
        row (list): List of strings

    Returns:
        list: List of strings and numeric.
    """
    row[8] = int(float(row[8]))
    row[9] = float(row[9])
    row[10] = float(row[10])
    row[13] = float(row[13])
    return row


def _transform_str_numeric_read_net_per_stock(row):
    """Transformation fucntion from string to numeric for rows of table net_per_stock.
        "Month Year",
    "Ticker",
    "Available Quantity units",(int)
    "Average Buy Price brl_unit",(float)
    "Sold Quantity units",(int)
    "Average Sell Price brl_unit",(float)
    "Profit per unit brl_per_unit",(float)
    "Unit profit per stock including sales operations costs",(float)
    "Profit brl",(float)
    "Remain Quantity units",(int)
    "Remain Operation value w taxes brl",(float)


    Args:
        row (list): List of strings

    Returns:
        list: List of strings and numeric.
    """
    row[2] = int(float(row[2]))
    row[3] = float(row[3])
    row[4] = int(float(row[4]))
    row[5] = float(row[5])
    row[6] = float(row[6])
    row[7] = float(row[7])
    row[8] = float(row[8])
    row[9] = int(float(row[9]))
    row[10] = float(row[10])
    return row


def _load_table_net_per_stock(path, skip_headers=False):
    if os.path.exists(path) == False:
        print(
            f"Could not find the path {path}, a new table for net_per_stock will be created."
        )
        a = []
        hio.export_to_csv_from_lists(a, path)
    b = hio.read_csv(
        path,
        skip_headers=skip_headers,
        func_transf_row=_transform_str_numeric_read_net_per_stock,
    )
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


def _search_index_range_of_key(key, col, a, trans_function=None, transformation=False):
    ix = []
    for i, row in enumerate(a):
        if transformation:
            val = trans_function(row[col])
        else:
            val = row[col]
        if val == key:
            ix.append(i)
    if ix:
        prev_index = ix[0]
        next_index = ix[-1] + 1
    else:
        prev_index = 0
        next_index = 0
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
        int,int: Index of the previous key being searched, first index of the next key of the key  being searched. Ex: key=3 list=[1,3,3,5] returns 1,3
    """
    if nested_list:
        # lo, hi = _search_previous_next_col(
        #     m, col, nested_list, trans_function, transformation
        # )
        lo, hi = _search_index_range_of_key(
            m, col, nested_list, trans_function, transformation
        )

        return lo, hi
    else:  # No operations found for the month
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
    # TODO:Implement a verification of month year in the case prev month is from another year
    ix_prev_ticker = -1
    for k in range(len(net_per_stock) - 1, -1, -1):
        if net_per_stock[k][1] == ticker:
            ix_prev_ticker = k
            break
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
    # TODO:Fix prev_ix, next_ix to avoid doing linear search
    prev_ix, next_ix = _get_index_range_search_col(m, 14, list_notas, get_month, True)

    # assert _is_month_year_correct(m, y, list_notas, i=lo)
    # assert _is_month_year_correct(m, y, list_notas, i=hi)

    seen_tickers = set()
    for i in range(cur_ix, next_ix):  # Loop per ticker of the month
        ticker = negocios_realizados[i][6]
        if ticker in seen_tickers:
            continue
        # print(ticker," ",m)
        seen_tickers.add(ticker)
        line = [month_year, ticker]
        buy_units = 0
        buy_value = 0
        sell_units = 0
        sell_value = 0.0
        sell_value_with_ops_cost = 0.0
        for k in range(prev_ix, next_ix):  # Loop all notas
            if ticker == negocios_realizados[k][6]:
                if negocios_realizados[k][3] == "C":  # compra
                    buy_units += negocios_realizados[k][8]
                    buy_value += (
                        negocios_realizados[k][10] + negocios_realizados[k][13]
                    )  # Valor operacao+Taxas
                elif negocios_realizados[k][3] == "V":  # Venda
                    sell_units += negocios_realizados[k][8]
                    sell_value += negocios_realizados[k][10]
                    sell_value_with_ops_cost += sell_value + negocios_realizados[k][13]

        prev_units, prev_value = get_stocks_per_ticker_previous_month_year(
            ticker, net_per_stock
        )

        bought_units = buy_units + prev_units
        avg_buy_price = (
            round((buy_value + prev_value) / bought_units, 2)
            if bought_units > 0.01
            else 0.0
        )  # includes operation costs
        avg_sell_price = round(sell_value / sell_units, 2) if sell_units > 0.01 else 0.0
        avg_unit_profit_loss = (
            round(avg_sell_price - avg_buy_price, 2) if sell_units > 0.01 else 0.0
        )
        avg_sell_price_with_ops_cost = (
            round(sell_value_with_ops_cost / sell_units, 2) if sell_units >= 0.01 else 0
        )
        avg_unit_profit_loss_with_ops_cost = (
            round(avg_sell_price_with_ops_cost - avg_buy_price, 2)
            if sell_units >= 0.01
            else 0
        )

        net_units = prev_units + buy_units - sell_units
        net_value = (
            round(prev_value + buy_value - sell_value_with_ops_cost, 2) if net_units >= 0.01 else 0.0
        )


        line.extend(
            [
                bought_units,  # Number of units in wallet
                avg_buy_price,  # Average price per stock bought considers stocks in wallet
                sell_units,  # Number sold units
                avg_sell_price,  # Average Sell Price without sales operations costs brl_unit
                avg_unit_profit_loss,  # Profit Loss without sales operations costs brl_per_unit
                avg_unit_profit_loss_with_ops_cost,  # Profit Loss with sales operations costs per unit brl_per_unit
                round(avg_unit_profit_loss * sell_units, 2),  # Profit Loss brl
                net_units,#Remain Quantity units
                net_value,#Remain Operation value with sales operations costs brl
            ]
        )
        # print(line)
        net_per_stock.append(line)


def _create_net_per_stock_year_balance(net_per_stock):
    """Create a net per stock_year_balance that consolidates owned assets in the end of december.

    Args:
        net_per_stock (list): Nested list containing stock informations per transaction.

    Returns:
        list: Nested list containing the stock_year_balance in december of the current year. This list must be passed for the next year for proper balance.
    """
    COL_AVAILABLE_STOCKS = 9
    COL_TICKER = 1
    COL_DATE = 0

    next_year = int(net_per_stock[0][0].split("/")[1]) + 1
    net_per_stock_year_balance = []
    set_tickers_seen = set()
    for i in range(len(net_per_stock) - 1, -1, -1):  # Loop latest months first
        ticker = net_per_stock[i][COL_TICKER]
        # print(ticker)
        if ticker not in set_tickers_seen:
            set_tickers_seen.add(ticker)
            if net_per_stock[i][COL_AVAILABLE_STOCKS] >= 0.01:  # Has stocks
                line = net_per_stock[i].copy()
                line[COL_DATE] = f"00/{next_year}"
                # print(net_per_stock[i])
                net_per_stock_year_balance.append(line)
                # print(line)
    return net_per_stock_year_balance

def get_summary_values_month(m,year,net_per_stock):
    initial_assets=0.0#Assets from previous month
    tot_transactions=0.0
    tot_profit_wo_sales=0.0
    tot_profit_w_sales=0.0
    remain_assets=0.0
    for i in range(1,len(net_per_stock)):#operations
        month=int(get_month(net_per_stock[i][0]))
        if month!=m:#stops
            break
        initial_assets+=net_per_stock[i][2]*net_per_stock[i][3]#Assets from previous month
        tot_transactions+=net_per_stock[i][4]*net_per_stock[i][5]    # Total transactions brl=Sold Quantity units"*Average Sell Price without sales operations costs brl_unit
        tot_profit_wo_sales+=net_per_stock[i][4]*net_per_stock[i][6]    # Total profitloss without sales costs brl=unitprofitwo*qnt
        tot_profit_w_sales+=net_per_stock[i][4]*net_per_stock[i][7]    # Total profitloss with sales costs brl=unitprofitwprice*qnt
        remain_assets+=net_per_stock[i][10]
    profit_to_assets=round(tot_profit_w_sales*100/initial_assets,2) if initial_assets>0.01 else 0.0  # Ratio Profit to total assets percentage=Total profitloss with sales costs/Initial Assets
    return [f"{m}/{year}",initial_assets,tot_transactions,tot_profit_wo_sales,tot_profit_w_sales,profit_to_assets,remain_assets]

def _calc_monthly_profit_loss(net_per_stock):
    """Calculates the monthly profit loss.
    Total transactions brl=Sold Quantity units"*Average Sell Price without sales operations costs brl_unit
    Total profitloss without sales costs brl=unitprofitwo*qnt
    Total profitloss with sales costs brl=unitprofitwprice*qnt
    Ratio Profit to total assets percentage=Total profitloss with sales costs/Total transactions
    Remaining Assets brl=Initial Assets-Total transactions brl

    Args:
        net_per_stock (list): List of lists.

    Returns:
        list: List of lists monthly profit loss.
    """
    monthly_profit_loss=[]
    year=net_per_stock[0][0].split('/')[1]
    added_month=1
    i=1
    while i<len(net_per_stock):
        initial_assets=0.0
        tot_transactions=0.0
        tot_profit_wo_sales=0.0
        tot_profit_w_sales=0.0
        remain_assets=0.0
        month=int(get_month(net_per_stock[i][0]))
        while True:
            initial_assets+=net_per_stock[i][2]*net_per_stock[i][3]#Assets from previous month
            tot_transactions+=net_per_stock[i][4]*net_per_stock[i][5]    # Total transactions brl=Sold Quantity units"*Average Sell Price without sales operations costs brl_unit
            tot_profit_wo_sales+=net_per_stock[i][4]*net_per_stock[i][6]    # Total profitloss without sales costs brl=unitprofitwo*qnt
            tot_profit_w_sales+=net_per_stock[i][4]*net_per_stock[i][7]    # Total profitloss with sales costs brl=unitprofitwprice*qnt
            remain_assets+=net_per_stock[i][10]
            try:
                next_month=int(get_month(net_per_stock[i+1][0]))
            except IndexError:
                next_month=month
            if (i>=len(net_per_stock)-1)|(next_month!=month):
                break
            else:
                i+=1
        profit_to_assets=round(tot_profit_w_sales*100/initial_assets,2) if initial_assets>0.01 else 0.0  # Ratio Profit to total assets percentage=Total profitloss with sales costs/Initial Assets    
        monthly_profit_loss.append([f"{month}/{year}",round(initial_assets,2),round(tot_transactions,2),round(tot_profit_wo_sales,2),round(tot_profit_w_sales,2),profit_to_assets,round(remain_assets,2)])
        i+=1
    return monthly_profit_loss



def _calc_profit_loss_month(net_per_stock):
    """Calculates the monthly profit loss.
    Total transactions brl=Sold Quantity units"*Average Sell Price without sales operations costs brl_unit
    Total profitloss without sales costs brl=unitprofitwo*qnt
    Total profitloss with sales costs brl=unitprofitwprice*qnt
    Ratio Profit to total assets percentage=Total profitloss with sales costs/Total transactions
    Remaining Assets brl=Initial Assets-Total transactions brl

    Args:
        net_per_stock (list): List of lists.

    Returns:
        list: List of lists monthly profit loss.
    """
    monthly_profit_loss=[]
    year=net_per_stock[0][0].split('/')[1]
    added_month=1
    for i in range(1,len(net_per_stock)):#Loop per operations
        month=int(get_month(net_per_stock[i][0]))
        if month<added_month:
            continue
        elif month>added_month:#Loops Months with no transaction
            for k in range(added_month,i): 
                initial_assets=net_per_stock[k][2]*net_per_stock[k][3]#Assets from previous month
                tot_transactions=0.0
                tot_profit_wo_sales=0.0
                tot_profit_w_sales=0.0
                profit_to_assets=0.0
                remain_assets=initial_assets
                monthly_profit_loss.append([f"{k}/{year}",initial_assets,tot_transactions,tot_profit_wo_sales,tot_profit_w_sales,profit_to_assets,remain_assets])
                added_month+=1
        assert month==added_month,"Incorrect month."
        #Starts Months with transaction        
        monthly_profit_loss.append(get_summary_values_month(added_month,year,net_per_stock))
        # monthly_profit_loss.append([f"{i}/{year}",initial_assets,tot_transactions,tot_profit_wo_sales,tot_profit_w_sales,profit_to_assets,remain_assets])
        added_month+=1
    return monthly_profit_loss


def main():
    cur_year = 2019
    prev_year = cur_year - 1

    data_processed_notas_path_cur_year = os.path.abspath(
        os.path.join(f"data/processed/{cur_year}/btg/notas_corretagem/")
    )
    data_processed_notas_path_prev_year = os.path.abspath(
        os.path.join(f"data/processed/{prev_year}/btg/notas_corretagem/")
    )
    test_data_path = os.path.abspath(os.path.join("tests/tests_data/"))


    negocios_realizados = hio.read_csv(
        os.path.join(
            data_processed_notas_path_cur_year, f"negocios_realizados_{cur_year}.csv"
        ),
        skip_headers=True,func_transf_row=_transform_str_numeric_read_negocios_realizados
    )
    try:
        net_per_stock = hio.read_csv(
            os.path.join(
                data_processed_notas_path_prev_year,
                f"net_per_stock_year_balance{prev_year}.csv",
            ),
            skip_headers=False,func_transf_row=_transform_str_numeric_read_net_per_stock
        )
    except AssertionError:
    # except FileNotFoundError|AssertionError:
        print("No previous stock data found.")
        net_per_stock = []
    # TODO:Fix range of 1,13. Verify the potential breaks given the change of the year.
    for i in range(1, 13):
        if i < 10:
            date = f"0{i}/{cur_year}"
        else:
            date = f"{i}/{cur_year}"
        _append_net_per_stock_for_month(net_per_stock, date, negocios_realizados)
    print(net_per_stock)
    net_per_stock_df = pd.DataFrame(net_per_stock)
    net_per_stock_df.to_csv(
        os.path.join(
            data_processed_notas_path_cur_year, f"net_per_stock{cur_year}.csv"
        ),
        header=0,
        index=False,
    )

    net_per_stock_year_balance = _create_net_per_stock_year_balance(net_per_stock)

    net_per_stock_year_balance_df = pd.DataFrame(net_per_stock_year_balance)
    net_per_stock_year_balance_df.to_csv(
        os.path.join(
            data_processed_notas_path_cur_year,
            f"net_per_stock_year_balance{cur_year}.csv",
        ),
        header=HEADERS_TABLE_NET_PER_STOCK,
        index=False,
    )


    # Calc monthly profit loss

    monthly_profit_loss=_calc_monthly_profit_loss(net_per_stock)
    monthly_profit_loss_df = pd.DataFrame(monthly_profit_loss)
    monthly_profit_loss_df.to_csv(
        os.path.join(
            data_processed_notas_path_cur_year,
            f"monthly_profit_loss_{cur_year}.csv",
        ),
        header=HEADERS_MONTHLY_PROFIT_LOSS,
        index=False,
    )

    # print(monthly_profit_loss)

    # # Export for testing
    # hio.export_object_as_std_out(negocios_realizados, os.path.join(test_data_path, "negocios_realizados.out"))
    # hio.export_object_as_std_out(custos_notas, os.path.join(test_data_path, "custos_notas.out"))



if __name__ == "__main__":
    main()
