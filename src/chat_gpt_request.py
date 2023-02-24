import os
import sys
from io import StringIO
from os.path import join
import multiprocessing

import pandas as pd
from chatgpt_wrapper import ChatGPT


def csv_request(prompt, filename, results_dict):
    chatgpt = ChatGPT()
    with open(join(os.path.dirname(os.getcwd()), "files", filename), "r") as f:
        df = pd.read_csv(f, index_col=[0], sep=";")

    gpt_input = (
        f"Given a pandas frame with the following columns: {list(df.columns)} "
        f"and the following data: {df.to_string()}. {prompt} using one single "
        f"python script without any comments loading the dataframe from the location "
        f"my_dataset_location, which is a csv file."
    )

    response = chatgpt.ask(gpt_input)
    response = response.split("```")[1].split("\n")

    my_dataset_location = join(os.path.dirname(os.getcwd()), "files", "csv_test.csv")
    my_dataset_location_out = join(
        os.path.dirname(os.getcwd()), "files", "csv_test_out.csv"
    )

    for l_idx, code_line in enumerate(response):
        if "python" in code_line and l_idx == 0:
            response[l_idx] = ""
        if "my_dataset_location" in code_line:
            response[
                l_idx
            ] = 'my_dataset_location = join(os.path.dirname(os.getcwd()), "files", "csv_test.csv")'
        if "df = pd.read_csv" in code_line:
            response[l_idx] = 'df = pd.read_csv(my_dataset_location, sep=";")'

    response.append(
        'df.to_csv(join(os.path.dirname(os.getcwd()), "files", "csv_test_out.csv"), sep=";")'
    )

    response = [f"{code_line} \n" for code_line in response]

    execution_code = "".join(response)
    stdout_old = sys.stdout
    execution_output = sys.stdout = StringIO()
    exec(execution_code)
    sys.stdout = stdout_old

    results_dict[0] = execution_output.getvalue()

    os.remove(my_dataset_location)
    os.remove(my_dataset_location_out)


def request_chatgpt(prompt, filename):
    manager = multiprocessing.Manager()
    results_dict = manager.dict()

    process = multiprocessing.Process(
        target=csv_request, args=(prompt, filename, results_dict)
    )
    process.start()
    process.join()

    answer = results_dict[0]

    return answer
