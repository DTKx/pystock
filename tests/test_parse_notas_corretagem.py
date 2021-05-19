import unittest
import numpy as np
import copy
import pickle
from context import pystock
from pystock import helpersio as hio
from pystock import parse_notas_corretagem as pnc
from ast import literal_eval
import os

path_data = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests_data/"))
hio.assert_exist_path(path_data)


class TestParseNotasCorretagem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("setupClass")

    def setUp(self):
        print("setUp")

    def test__parse_add_negocios_realizados(self):
        """
        Test parse of table of negocios realizados, compare parsed values versus a manually curated file.
        """
        print("_parse_add_negocios_realizados")

        id_test_cases = [0, 1, 2, 3, 4, 5, 6]
        for id_test in id_test_cases:
            in_case = hio.import_object_as_literal(
                os.path.join(
                    path_data,
                    f"_parse_add_negocios_realizados_table_negocios_realizados_{id_test}.in",
                )
            )
            out_case = hio.import_object_as_literal(
                os.path.join(
                    path_data,
                    f"_parse_add_negocios_realizados_table_negocios_realizados_{id_test}.out",
                )
            )
            out_test = pystock.parse_notas_corretagem._parse_add_negocios_realizados(
                in_case, out_case[0][-1]
            )
            self.assertListEqual(out_case, out_test)

    def tearDown(self):
        print("tearDown")

    def setUp(self):
        print("setUp")

    def test__parse_resumo_dos_negocios(self):
        """
        Test parse of table of resumo dos negocios.
        """
        print("_parse_resumo_dos_negocios")
        id_test_cases = [0]
        for id_test in id_test_cases:
            in_case = hio.read_strings(
                os.path.join(path_data, f"_parse_resumo_dos_negocios_{id_test}.in")
            )
            out_case = hio.import_object_as_literal(
                os.path.join(
                    path_data,
                    f"_parse_resumo_dos_negocios_valores_resumo_dos_negocios_{id_test}.out",
                )
            )
            out_test = pystock.parse_notas_corretagem._parse_resumo_dos_negocios(
                in_case
            )
            self.assertListEqual(out_case, out_test)

    def tearDown(self):
        print("tearDown")

    def setUp(self):
        print("setUp")

    def test__parse_clearing(self):
        """
        Test parse of table clearing.
        """
        print("_parse_clearing")
        id_test_cases = [0]
        for id_test in id_test_cases:
            in_case = hio.read_strings(
                os.path.join(path_data, f"_parse_clearing_{id_test}.in")
            )
            out_case = hio.import_object_as_literal(
                os.path.join(path_data, f"_parse_clearing_values_{id_test}.out",)
            )
            out_test = pystock.parse_notas_corretagem._parse_clearing(in_case)
            self.assertListEqual(out_case, out_test)

    def tearDown(self):
        print("tearDown")

    def setUp(self):
        print("setUp")

    def test__parse_bovespa(self):
        """
        Test parse of table bovespa.
        """
        print("_parse_bovespa")
        id_test_cases = [0]
        for id_test in id_test_cases:
            in_case = hio.read_strings(
                os.path.join(path_data, f"_parse_bovespa_{id_test}.in")
            )
            out_case = hio.import_object_as_literal(
                os.path.join(path_data, f"_parse_bovespa_values_{id_test}.out",)
            )
            out_test = pystock.parse_notas_corretagem._parse_bovespa(in_case)
            self.assertListEqual(out_case, out_test)

    def tearDown(self):
        print("tearDown")

    def setUp(self):
        print("setUp")

    def test__parse_corretagem(self):
        """
        Test parse of table corretagem.
        """
        print("_parse_corretagem")
        id_test_cases = [0]
        for id_test in id_test_cases:
            in_case = hio.read_strings(
                os.path.join(path_data, f"_parse_corretagem_{id_test}.in")
            )
            out_case = hio.import_object_as_literal(
                os.path.join(path_data, f"_parse_corretagem_values_{id_test}.out",)
            )
            out_test = pystock.parse_notas_corretagem._parse_corretagem(in_case)
            self.assertListEqual(out_case, out_test)

    def tearDown(self):
        print("tearDown")

    def setUp(self):
        print("setUp")

    def test_parse_notas_corretagem_btg(self):
        """
        Test parse of table corretagem comparing to manually curated values.
        """
        print("parse_notas_corretagem_btg")
        negocios_realizados, custos_notas = pnc.parse_notas_corretagem_btg(
            os.path.join(path_data, "notas_operacoes_2020.pdf",)
        )
        # Verify negocios_realizados
        out_case = hio.import_object_as_literal(
            os.path.join(path_data, "negocios_realizados.out")
        )
        self.assertListEqual(out_case, negocios_realizados)

        # Verify custos_notas
        hio.export_object_as_std_out(
            custos_notas, os.path.join(path_data, "custos_notas_test.out")
        )
        out_case_2 = hio.read_strings(os.path.join(path_data, "custos_notas_test.out"))
        custos_notas_test = hio.read_strings(
            os.path.join(path_data, "custos_notas_test.out")
        )
        self.assertEqual(out_case_2, custos_notas_test)

    def tearDown(self):
        print("tearDown")

    @classmethod
    def tearDownClass(cls):
        print("teardownClass")


if __name__ == "__main__":
    unittest.main(verbosity=2)
