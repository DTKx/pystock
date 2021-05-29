import codecs
import pickle
import sys
from ast import literal_eval
import pandas as pd
import json
import os
import csv


def exportPdFrameToLatex(path, file):
    with codecs.open(path, mode="w", encoding="utf-8") as f:
        f.write(file.to_latex(index=True, header=False, escape=True))


def exportToFile(path, file):
    with codecs.open(path, mode="w", encoding="utf-8") as f:
        f.write(file)


def export_obj(obj, path):
    with codecs.open(path, mode="w", encoding="utf-8") as f:  # Test also mode="wb"
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def assert_exist_path(path):
    assert os.path.exists(
        path
    ), f"Could not find the path {path}, please modify the path."


def load_obj(path):
    assert os.path.exists(
        path
    ), f"Could not find the path {path}, please modify the path."
    with codecs.open(path, mode="w", encoding="utf-8") as f:  # Test also mode="rb"
        obj = pickle.load(f)
    return obj


def export_object_as_std_out(myobject, path):
    with codecs.open(path, mode="w", encoding="utf-8") as f:
        print(myobject, file=f)


def import_object_as_literal(path):
    assert os.path.exists(
        path
    ), f"Could not find the path {path}, please modify the path."
    with codecs.open(path, mode="r", encoding="utf-8") as f:
        a = literal_eval(f.read().strip().replace("\n", ""))
    return a


def read_strings(path):
    assert os.path.exists(
        path
    ), f"Could not find the path {path}, please modify the path."
    a = ""
    with codecs.open(path, mode="r", encoding="utf-8") as f:
        for line in f.readlines():
            if line:
                a = "".join([a, line])
    return a


def createCsvMainFrom3ColDict(inputPath, dictAuxiliar, outputPath):
    assert os.path.exists(
        inputPath
    ), f"Could not find the path {inputPath}, please modify the path."
    df = pd.DataFrame.from_dict(
        {
            (dictAuxiliar[i][j], j): i
            for i in dictAuxiliar.keys()
            for j in dictAuxiliar[i].keys()
        },
        orient="index",
    )
    df.to_csv(outputPath)


def exportAsCsvFromDict(myDict, outputPath):
    df = pd.DataFrame.from_dict(myDict, orient="index")
    df.to_csv(outputPath)


def exportToJson(data, path):
    with open(path, "wb") as f:
        json.dump(data, codecs.getwriter("utf-8")(f), ensure_ascii=False)


"""
CSV
"""


def export_to_csv_from_lists(mylists, outputPath):
    df = pd.DataFrame(mylists)
    df.to_csv(outputPath, index=False, header=False)


def read_csv(path, skip_headers=False, delimiter=",",func_transf_row=None):
    """Read csv file, returning a nested list, each row having a column row output will be strings or numeric.

    Args:
        path (string): path to file.
        skip_headers (bool, optional): If true skips first line. Defaults to False.
        delimiter (str, optional): Delimiter that separates csv. Defaults to ",".

    Returns:
        list: list of lists with lines of file.
    """
    assert os.path.exists(
        path
    ), f"Could not find the path {path}, please modify the path."
    my_list = []
    with open(path, newline="", encoding="utf-8") as csvfile:
        f = csv.reader(csvfile, delimiter=delimiter)
        if skip_headers:
            next(f, None)  # skip the headers
        for row in f:
            if func_transf_row!=None:
                row=func_transf_row(row)
            my_list.append(row)
    return my_list


def main():
    # # Test export_object_as_std_out
    # a = [1, [1], ["cc"], ["importação , 0.0"], "Valor líquido das operações 5.200,00 C"]
    # export_object_as_std_out(a, "out.txt")

    # # Test import_object_as_literal
    # b = import_object_as_literal("out.txt")
    # print(b[0])
    # print(b[1])
    # print(b[2])
    # print(b[3])

    # # Test read_strings
    # a = "Valor líquido das operações 5.200,00 C"
    # export_object_as_std_out(a, "out.txt")
    # print(read_strings("out.txt"), end="")

    # assert_exist_path(os.getcwd())
    # # assert_exist_path(os.path.join(os.getcwd(),"aas"))#Throws assertion error

    # Tests export and import  CSV
    a = [[1, 2, 2], [1, 2, 2], [1, 2, 2]]
    path = os.path.abspath("tests/tests_data/my_list.csv")
    export_to_csv_from_lists(a, path)
    b = read_csv(path)
    print(b)
    print(b[0])
    print(b[0][0])


if __name__ == "__main__":
    main()

