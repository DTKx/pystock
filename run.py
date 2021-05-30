"""
Parse notas de corretagem BTG, receive files in PDF and generates 1 table containing operations performed and 1 dictionary containing costs per número de nota.
"""
import pandas as pd
import os
from pystock import parse_notas_corretagem as pnc
from pystock import helpersio as hio
from pystock import calc_monthly_net_result as cmnr


def calc_monthly_net_result_per_stock(
    CUR_YEAR, data_processed_notas_path_cur_year, data_processed_notas_path_prev_year
):

    PREV_YEAR = CUR_YEAR - 1
    negocios_realizados = hio.read_csv(
        os.path.join(
            data_processed_notas_path_cur_year, f"negocios_realizados_{CUR_YEAR}.csv"
        ),
        skip_headers=True,
        func_transf_row=cmnr._transform_str_numeric_read_negocios_realizados,
    )
    try:
        net_per_stock = hio.read_csv(
            os.path.join(
                data_processed_notas_path_prev_year,
                f"net_per_stock_year_balance{PREV_YEAR}.csv",
            ),
            skip_headers=True,
            func_transf_row=cmnr._transform_str_numeric_read_net_per_stock,
        )
    except AssertionError:
        print("No previous stock data found.")
        net_per_stock = []
    # TODO:Fix range of 1,13. Verify the potential breaks given the change of the year.
    for i in range(1, 13):
        if i < 10:
            date = f"0{i}/{CUR_YEAR}"
        else:
            date = f"{i}/{CUR_YEAR}"
        cmnr._append_net_per_stock_for_month(net_per_stock, date, negocios_realizados)
    return net_per_stock


def main():
    CUR_YEAR = 2020

    data_raw_notas_path = os.path.abspath(
        os.path.join(f"data/raw/{CUR_YEAR}/btg/notas_corretagem/")
    )

    data_processed_notas_path_cur_year = os.path.abspath(
        os.path.join(f"data/processed/{CUR_YEAR}/btg/notas_corretagem/")
    )
    data_processed_notas_path_prev_year = os.path.abspath(
        os.path.join(f"data/processed/{CUR_YEAR-1}/btg/notas_corretagem/")
    )

    test_data_path = os.path.abspath(os.path.join("tests/tests_data/"))
    hio.assert_exist_path(data_raw_notas_path)
    hio.assert_exist_path(data_processed_notas_path_cur_year)
    hio.assert_exist_path(test_data_path)

    # Parse Notas de corretagem
    PARSE_NOTAS_CORRETAGEM = False
    NEGOCIOS_REALIZADOS_EXPORT_RESULTS = False
    NEGOCIOS_REALIZADOS_EXPORT_FOR_TESTS = False
    if PARSE_NOTAS_CORRETAGEM:
        inputPath = os.path.join(data_raw_notas_path, f"notas_operacoes_{CUR_YEAR}.pdf")
        negocios_realizados, custos_notas = pnc.parse_notas_corretagem_btg(inputPath)
        negocios_realizados_df = pd.DataFrame(negocios_realizados)
    if NEGOCIOS_REALIZADOS_EXPORT_RESULTS:
        negocios_realizados_df.to_csv(
            os.path.join(
                data_processed_notas_path_cur_year,
                f"negocios_realizados_{CUR_YEAR}.csv",
            ),
            header=0,
        )
        hio.exportToJson(
            custos_notas,
            os.path.join(
                data_processed_notas_path_cur_year, f"custos_notas{CUR_YEAR}.json"
            ),
        )
    if NEGOCIOS_REALIZADOS_EXPORT_FOR_TESTS:  # Export for testing
        hio.export_object_as_std_out(
            negocios_realizados,
            os.path.join(test_data_path, f"negocios_realizados_{CUR_YEAR}.out"),
        )
        hio.export_object_as_std_out(
            custos_notas, os.path.join(test_data_path, f"custos_notas_{CUR_YEAR}.out")
        )

    # Calculate monthly net result per stock
    CALC_MONTHLY_NET_RESULT_PER_STOCK = True
    EXPORT_NET_PER_STOCK = True
    EXPORT_NET_PER_STOCK_YEAR_BALANCE = True

    if CALC_MONTHLY_NET_RESULT_PER_STOCK:
        net_per_stock = calc_monthly_net_result_per_stock(
            CUR_YEAR,
            data_processed_notas_path_cur_year,
            data_processed_notas_path_prev_year,
        )
        net_per_stock_year_balance = cmnr._create_net_per_stock_year_balance(
            net_per_stock
        )
    if EXPORT_NET_PER_STOCK:
        net_per_stock_df = pd.DataFrame(net_per_stock)
        net_per_stock_df.to_csv(
            os.path.join(
                data_processed_notas_path_cur_year, f"net_per_stock{CUR_YEAR}.csv"
            ),
            header=cmnr.HEADERS_TABLE_NET_PER_STOCK,
            index=False,
        )
    if EXPORT_NET_PER_STOCK_YEAR_BALANCE:
        if net_per_stock_year_balance:
            net_per_stock_year_balance_df = pd.DataFrame(net_per_stock_year_balance)
            net_per_stock_year_balance_df.to_csv(
                os.path.join(
                    data_processed_notas_path_cur_year,
                    f"net_per_stock_year_balance{CUR_YEAR}.csv",
                ),
                header=cmnr.HEADERS_TABLE_NET_PER_STOCK,
                index=False,
            )
        else:
            net_per_stock_year_balance_df = pd.DataFrame(net_per_stock_year_balance)
            net_per_stock_year_balance_df.to_csv(
                os.path.join(
                    data_processed_notas_path_cur_year,
                    f"net_per_stock_year_balance{CUR_YEAR}.csv",
                ),
                header=0,
                index=False,
            )

    # Calculate monthly profit loss per month
    CALC_MONTHLY_PROFIT_LOSS = True
    EXPORT_MONTHLY_PROFIT_LOSS = True
    if CALC_MONTHLY_PROFIT_LOSS:
        monthly_profit_loss=cmnr._calc_monthly_profit_loss(net_per_stock)
        monthly_profit_loss_df = pd.DataFrame(monthly_profit_loss)
        monthly_profit_loss_df.to_csv(
            os.path.join(
                data_processed_notas_path_cur_year,
                f"monthly_profit_loss_{CUR_YEAR}.csv",
            ),
            header=cmnr.HEADERS_MONTHLY_PROFIT_LOSS,
            index=False,
        )
        

if __name__ == "__main__":
    main()
