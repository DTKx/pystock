"""
Parse notas de corretagem BTG, receive files in PDF and generates 1 table containing operations performed and 1 dictionary containing costs per número de nota.
"""
import pandas as pd
import os
from pystock import parse_notas_corretagem as pnc
from pystock import helpersio as hio

def main():   
    data_raw_notas_path = os.path.abspath(
        os.path.join("data/raw/2019/btg/notas_corretagem/")
    )
    data_processed_notas_path = os.path.abspath(
        os.path.join("data/processed/2019/btg/notas_corretagem/")
    )
    test_data_path= os.path.abspath(os.path.join("tests/tests_data/"))
    hio.assert_exist_path(data_raw_notas_path)
    hio.assert_exist_path(data_processed_notas_path)
    hio.assert_exist_path(test_data_path)


    inputPath = os.path.join(data_raw_notas_path, "notas_operacoes_2019.pdf")
    negocios_realizados, custos_notas = pnc.parse_notas_corretagem_btg(inputPath)

    negocios_realizados_df = pd.DataFrame(negocios_realizados)

    # negocios_realizados_df.to_csv(os.path.join(data_processed_notas_path,"negocios_realizados_2019.csv"),header=0)
    # hio.exportToJson(custos_notas,os.path.join(data_processed_notas_path,"custos_notas.json"))

    # # Export for testing
    # hio.export_object_as_std_out(negocios_realizados, os.path.join(test_data_path, "negocios_realizados.out"))
    # hio.export_object_as_std_out(custos_notas, os.path.join(test_data_path, "custos_notas.out"))

if __name__ == "__main__":
	main()
