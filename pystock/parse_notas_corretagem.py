"""
Parse notas de corretagem BTG, receive files in PDF and generates 1 table containing operations performed and 1 dictionary containing costs per número de nota.
"""
import pandas as pd
import os
import pdfplumber
import re
import json, codecs
import pystock.helpersio as hio
import sys

HEADERS_NEGOCIOS_REALIZADOS=['Q', 'Negociação', 'C/V', 'Tipo Mercado', 'Prazo', 'Especificação do título', 'Obs. (*)', 'Quantidade', 'Preço / Ajuste', 'Valor Operação / Ajuste', 'D/C','Nr. nota']

def _parse_add_negocios_realizados(table_negocios_realizados, num_nota):
    """Extrai tabela de negócios realizados, adicionando ao fim da tabela o número da nota.
    Adiciona valores a Lista de strings: Lista com os negócios realizados (negocios_realizados).
    Headers:['Q', 'Negociação', 'C/V', 'Tipo Mercado', 'Prazo', 'Especificação do título', 'Obs. (*)', 'Quantidade', 'Preço / Ajuste', 'Valor Operação / Ajuste', 'D/C','Nr. nota']


    Args:
        tables (objeto): Objeto tables
        counter (int): Número da página da nota, se 0 deve se adicionar header.
        num_nota (str): Número da nota de corretagem.
    """
    negocios_realizados = []
    for line in table_negocios_realizados[
        1:
    ]:  # [ixFirstLine:]:#Skips the columns names
        linhas_processed = [x.replace(".", "").replace(",", ".") for x in line]
        linhas_processed.append(num_nota)
        negocios_realizados.append(linhas_processed)
    return negocios_realizados


def _parse_resumo_dos_negocios(df_str):
    """Parse tabela resumo dos negócios.Retornando valores no formato delista.

    Args:
        df_str (str): String contendo tabela de resumo de negócios.

    Returns:
        lista str: Lista com valores de items.
    """

    linhas = df_str.split("\n")
    linhas_processed = [x.lower().replace(".", "").replace(",", ".") for x in linhas]

    HEADERS = [
        "debêntures",
        "vendas à vista",
        "compras à vista",
        "opções - compras",
        "opções - vendas",
        "operações à termo",
        "\)",
        "valor das operações",
    ]
    valores = []
    for i in range(len(HEADERS)):
        valores.append(float(re.split(HEADERS[i], linhas_processed[i])[-1].strip()))
    return valores


def _parse_clearing(df_str):
    """Parse tabela clearing.Retornando valores no formato delista.

    Args:
        df_str (str): String contendo tabela.

    Returns:
        lista str: lista com valores de items.
    """

    linhas = df_str.split("\n")
    linhas_processed = [x.lower().replace(".", "").replace(",", ".") for x in linhas]

    HEADERS = [
        "clearing",  # No values
        "valor líquido das operações",
        "taxa de liquidação",
        "taxa de registro",
        "total cblc",
    ]
    valores = []
    for i in range(1, len(HEADERS)):
        values = re.split(HEADERS[i], linhas_processed[i])[-1].strip()
        valores.append(float(values.split(" ")[0].strip()))
    return valores


def _parse_bovespa(df_str):
    """Parse tabela bovespa.Retornando valores no formato delista.

    Args:
        df_str (str): String contendo tabela.

    Returns:
        lista str: lista com valores de items.
    """

    linhas = df_str.split("\n")
    linhas_processed = [x.lower().replace(".", "").replace(",", ".") for x in linhas]

    HEADERS = [
        "bolsa",  # No values
        "taxa de termo/opções",
        "taxa ana",
        "emolumentos",
        "total bovespa / soma",
    ]
    valores = []
    for i in range(1, len(HEADERS)):
        values = re.split(HEADERS[i], linhas_processed[i])[-1].strip()
        valores.append(float(values.split(" ")[0].strip()))
    return valores


def _parse_corretagem(df_str):
    """Parse tabela corretagem.Retornando valores no formato delista.

    Args:
        df_str (str): String contendo tabela.

    Returns:
        lista str: lista com valores de items.
    """

    linhas = df_str.split("\n")
    linhas_processed = [x.lower().replace(".", "").replace(",", ".") for x in linhas]

    HEADERS = [
        "corretagem / despesas",  # No values
        "clearing",
        "execução",
        "execução casa",
        "iss \(são paulo\)",
        "irrf s/ operações, base r$",
        "outras bovespa",
        "total corretagem / despesas",
    ]
    valores = []
    for i in range(1, len(HEADERS)):
        values = re.split(HEADERS[i], linhas_processed[i])[-1].strip()
        if i == 5:  # i.r.r.f. s/ operações
            valores.append(float(values.split(" ")[-1].strip()))
        else:
            valores.append(float(values.split(" ")[0].strip()))
    return valores


def _parse_add_custos_notas(df_custo, custos_notas, num_nota, numtest):
    """Parse Custos de operação por nota, gerando um dicionário key:número da nota e lista de atributos da nota.
    ATTRIBUTES = [
        "debêntures",
        "vendas à vista",
        "compras à vista",
        "opções - compras",
        "opções - vendas",
        "operações à termo",
        "Valor das oper. com títulos públ",
        "valor das operações",
        "valor líquido das operações",
        "taxa de liquidação",
        "taxa de registro",
        "total cblc",
        "taxa de termo/opções",
        "taxa a.n.a.",
        "emolumentos",
        "total bovespa / soma",
        "clearing",
        "execução",
        "execução casa",
        "iss \(são paulo\)",
        "i.r.r.f. s/ operações, base r$",
        "outras bovespa",
        "total corretagem / despesas",
        "data de liquidação",
        "valor líquido",
    ]

    Args:
        df_custo (lista (str)): Lista das tabelas de custo.
        custos_notas (dict): Dicionário adicionar valores das notas.
        num_nota (str): Número da nota.
    """
    values = []

    # # Export for testing
    # export_obj_as_std_out_test(
    #     df_custo[1][1][0], f"_parse_resumo_dos_negocios_{numtest}.in"
    # )

    resumo_dos_negocios_df = _parse_resumo_dos_negocios(df_custo[1][1][0])
    values.extend(resumo_dos_negocios_df)

    # # Export for testing
    # export_obj_as_std_out_test(
    #     resumo_dos_negocios_df,
    #     f"_parse_resumo_dos_negocios_valores_resumo_dos_negocios_{numtest}.out",
    # )

    # # Export for testing
    # export_obj_as_std_out_test(df_custo[1][1][1], f"_parse_clearing_{numtest}.in")

    clearing_df = _parse_clearing(df_custo[1][1][1])
    values.extend(clearing_df)

    # # Export for testing
    # export_obj_as_std_out_test(clearing_df, f"_parse_clearing_values_{numtest}.out")

    # # Export for testing
    # export_obj_as_std_out_test(df_custo[1][2][1], f"_parse_bovespa_{numtest}.in")

    bovespa_df = _parse_bovespa(df_custo[1][2][1])
    values.extend(bovespa_df)

    # # Export for testing
    # export_obj_as_std_out_test(bovespa_df, f"_parse_bovespa_values_{numtest}.out")

    # # Export for testing
    # export_obj_as_std_out_test(df_custo[1][3][1], f"_parse_corretagem_{numtest}.in")

    corretagem_df = _parse_corretagem(df_custo[1][3][1])
    values.extend(corretagem_df)
    # # Export for testing
    # export_obj_as_std_out_test(corretagem_df, f"_parse_corretagem_values_{numtest}.out")

    values.append(df_custo[1][4][1].split()[2])  # Data de liquidação

    values.append(df_custo[1][4][1].split()[3])  # Valor Liquido

    custos_notas[num_nota] = values


def export_obj_as_std_out_test(obj, obj_name):
    test_data_path = os.path.abspath(os.path.join("tests/tests_data/"))   
    assert os.path.exists(
        test_data_path
    ), f"Could not find the path {test_data_path}, please modify the path."
    hio.export_object_as_std_out(obj, os.path.join(test_data_path, obj_name))


def _add_custos_notas_ativos_resumo_nota(
    negocios_realizados, custos_notas, num_nota, resumo_nota, data_pregao
):
    """ Calcula taxas médias por ativo e adiciona a lista
    taxas=(total corretagem(22))/Num ativos por nota +
    ((Taxa de Liquidação(9)+Taxa de Registro(10)+Emolumentos(14))/Valor das Operações(7))*(Valor Operação Ativo)

    Args:
        negocios_realizados ([type]): [description]
        custos_notas ([type]): [description]
        num_nota ([type]): Nr. Nota
        num_atributes ([type]): Número de atributos 
        resumo_nota ([type]): Resumo nota
        data_pregao ([type]): data_pregao
    """
    taxa_corretagem = custos_notas[num_nota][22] / float(len(negocios_realizados))
    taxas_LRE_div_total = (
        custos_notas[num_nota][9]
        + custos_notas[num_nota][10]
        + custos_notas[num_nota][14]
    ) / (custos_notas[num_nota][7])
    for ativo in negocios_realizados:
        ativo.append(
            round(taxa_corretagem + taxas_LRE_div_total * float(ativo[9]), ndigits=2)
        )
        ativo.append(data_pregao)
        assert len(ativo) == len(
            resumo_nota[0]
        ), f"Error in parsing, incorrect shape {len(ativo)} of received output."
        resumo_nota.append(ativo)  # Final Update


def parse_notas_corretagem_btg(path):
    """Parse notas de corretagem btg. Extrai negócios realizados e custos por nota de corretagem.

    Args:
        path (string): Caminho do arquivo de nota do btg.

    Returns:
        lista (str),dict (key(str):values(str)): : lista de negócios realizados,dict de custos por nota
    """
    resumo_nota = [
        [
            "Q",
            "Negociação",
            "C/V",
            "Tipo Mercado",
            "Prazo",
            "Especificação do título",
            "Obs. (*)",
            "Quantidade",
            "Preço / Ajuste",
            "Valor Operação / Ajuste",
            "D/C",
            "Nr. nota",
            "taxas",
            "Data pregao",
        ]
    ]
    custos_notas = {}  # Key:Num Nota, Negocios Realizados:
    with pdfplumber.open(path) as pdf:
        i = 0
        count_page = 0
        for page in pdf.pages:
            tables = page.extract_tables()
            num_nota = tables[0][0][5].split()[2]
            data_pregao = tables[0][0][8].split()[2]

            # # Export for testing
            # export_obj_as_std_out_test(
            #     tables[1],
            #     f"_parse_add_negocios_realizados_table_negocios_realizados_{count_page}.in",
            # )
            negocios_realizados = _parse_add_negocios_realizados(tables[1], num_nota)
            assert len(resumo_nota[0]) - 2 == len(
                negocios_realizados[0]
            ), f"Error in parsing, incorrect shape {len(negocios_realizados[0])} of received output."

            # # Export for testing
            # export_obj_as_std_out_test(
            #     negocios_realizados,
            #     f"_parse_add_negocios_realizados_table_negocios_realizados_{count_page}.out",
            # )

            table_settings = {"horizontal_strategy": "lines_strict"}
            df_custo = page.extract_tables(table_settings)
            _parse_add_custos_notas(df_custo, custos_notas, num_nota, count_page)
            _add_custos_notas_ativos_resumo_nota(
                negocios_realizados, custos_notas, num_nota, resumo_nota, data_pregao
            )
            assert len(resumo_nota[0]) == len(
                negocios_realizados[0]
            ), f"Error in parsing, incorrect shape {len(negocios_realizados[0])} of received output."
            count_page += 1
    return resumo_nota, custos_notas


def main():
    data_raw_notas_path = os.path.abspath(
        os.path.join("data/raw/2020/btg/notas_corretagem/")
    )
    inputPath = os.path.join(data_raw_notas_path, "notas_operacoes_2020.pdf")
    negocios_realizados, custos_notas = parse_notas_corretagem_btg(inputPath)
    print(negocios_realizados)
    print(custos_notas)


if __name__ == "__main__":
    main()
