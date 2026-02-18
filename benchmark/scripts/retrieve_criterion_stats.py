import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import os 
import sys

CRITERION_FOLDER = "../../../pulsedcm/target/criterion/" 
WHICH = "new"
NANO_TO_SECS = 1000000000

FILE_NUMBER_DICT = {
        "CT": 516, 
        "MR": 80, 
        "MG": 1,
}
FOLDER_SIZE_DICT = {
        "CT": "264Mo", 
        "MR": "320Ko", 
        "MG": "53Mo",
}

def main(): 
    print(f"Cold? : {sys.argv[1]}")
    folders = os.listdir(CRITERION_FOLDER)
    out = []
    df = {
        "name": [],
        "nb_files": [],
        "size": [],
        "type": [],
        "p50": [],
        "p95": [],
        "std_dev": [],
        "per_file": []
        }

    for i in folders:
        if i == "report":
            continue
        name = i.split("/")[-1] 
        path_sample = CRITERION_FOLDER+i+"/"+WHICH+"/"+"sample.json"
        path_estimates = CRITERION_FOLDER+i+"/"+WHICH+"/"+"estimates.json"
        if not os.path.isfile(path_sample) or not os.path.isfile(path_estimates):
            print(f"Can't find path: {path_sample} or {path_estimates}")

        df["name"].append(name)
        df['type'].append(sys.argv[1])
        df['nb_files'].append(FILE_NUMBER_DICT[name.split("_")[0]])
        df['size'].append(FOLDER_SIZE_DICT[name.split("_")[0]])
        # --- p50_median, p95, std, per_file_equivalent        
        with open(path_estimates, 'r') as f:
            estimates = json.load(f)
            p50 = estimates['median']['point_estimate'] / NANO_TO_SECS
            df["p50"].append(p50)
            df["std_dev"].append(estimates['std_dev']['point_estimate'] / NANO_TO_SECS)
            df['per_file'].append(FILE_NUMBER_DICT[name.split("_")[0]] / p50)

        try:
            samples_df = pd.read_json(path_sample)
            df['p95'].append(np.percentile(samples_df['times'],95) / NANO_TO_SECS)
        except:
            pass    

    df = pd.DataFrame(df)
    df.to_csv("../outputs/report.csv", index=False)
    
if __name__ == "__main__":
    main()
