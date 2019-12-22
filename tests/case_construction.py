import json
import os

from datenguidepy.query_execution import ExecutionResults


def construct_execution_results(path):
    directory, file = os.path.split(path)
    meta_file = file.split(".", 1)[0] + "_meta.json"
    meta_path = os.path.join(directory, meta_file)
    with open(path, "r") as file:
        res = json.load(file)
    with open(meta_path, "r") as file:
        meta = json.load(file)
    return [ExecutionResults(res, meta)]


def save_result_files_from_query(query, name, result_path):
    """
        Helper function that for the construction of files
        to be loaded by `construct_execution_results`
    """
    raise NotImplementedError
