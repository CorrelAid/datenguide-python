import json
import os

from datenguidepy.query_execution import ExecutionResults, QueryExecutioner


def construct_execution_results(path):
    directory, file = os.path.split(path)
    meta_file = file.split(".", 1)[0] + "_meta.json"
    meta_path = os.path.join(directory, meta_file)
    with open(path, "r", encoding="utf-8") as file:
        res = json.load(file)
    with open(meta_path, "r", encoding="utf-8") as file:
        meta = json.load(file)
    return [ExecutionResults(r, meta) for r in res]


def save_result_files_from_query(query, name, result_path):
    """
        Helper function that for the construction of files
        to be loaded by `construct_execution_results`
    """
    qe = QueryExecutioner()
    execution_results = qe.run_query(query)

    query_json_file = os.path.join(result_path, f"{name}_query.json")
    result_json_file = os.path.join(result_path, f"{name}.json")
    meta_json_file = os.path.join(result_path, f"{name}_meta.json")

    with open(query_json_file, "w") as file:
        json.dump(query.get_graphql_query(), file)

    with open(result_json_file, "w") as file:
        json.dump([res.query_results for res in execution_results], file)

    with open(meta_json_file, "w") as file:
        json.dump(execution_results[0].meta_data, file)
