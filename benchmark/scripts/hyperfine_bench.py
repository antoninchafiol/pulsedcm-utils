import subprocess
import pandas as pd
import numpy as np
import os
import sys
import json

def process_json():
    TYPE = sys.argv[4]
    FILE_NUMBER_DICT = {
            "CT": 516, 
            "MR": 80, 
            "MG": 1,
    }
    FOLDER_SIZE_DICT = {
            "CT": "264Mo", 
            "MR": "46Mo", 
            "MG": "53Mo",
    }
    df = {
        "type": [],
        "name": [],
        "nb_files": [],
        "size": [],
        "p50": [],
        "p95": [],
        "std_dev": [],
        "per_file": []
        }
    jsons = os.listdir("outputs")
    jsons = [i for i in jsons if "json" in i]
    for j in jsons:
        with open("outputs/"+j, 'r') as f:
            file = json.load(f)
        for r in file['results']:
            df['name'].append(r['command'])
            df['type'].append(TYPE)
            df['p50'].append(r['mean'])
            df['std_dev'].append(r['stddev'])
            df['nb_files'].append(FILE_NUMBER_DICT[r['command'].split("_")[0]])
            df['size'].append(FOLDER_SIZE_DICT[r['command'].split("_")[0]])
            df['per_file'].append(FILE_NUMBER_DICT[r['command'].split("_")[0]] / r['mean'])
            df['p95'].append(np.percentile(r['times'], 95))
    df_json = json.dumps(df, indent=4)
    print(df_json)
    df = pd.DataFrame(df)
    df.to_csv("outputs/report.csv", index=False)
    for j in jsons:
        os.remove("outputs/"+j)
    return 0

def compute_hyperfine():
    if not os.path.exists(sys.argv[1]):
        print(f"{sys.argv[1]} can't be found")
        return 1
    if not os.path.exists(sys.argv[2]):
        print(f"{sys.argv[2]} can't be found")
        return 1

    pulsedcm = sys.argv[1]
    data_main_folder = sys.argv[2]
    output_dir = sys.argv[3]

    config = {
            "runs": "10",
            "warmup": "5"
            }
    folders          = [os.path.join(data_main_folder, i)  for i in os.listdir(data_main_folder)]
    folders          = [i for i in folders if not i.endswith('.csv')]


    for i, f in enumerate(folders):
        csv_name = f[-2:]
        commands = [
                f"{pulsedcm} {f} ano --out {output_dir} --with-pixel-data",
                f"{pulsedcm} {f} ano --out {output_dir} --with-pixel-data --batch 25",
                f"{pulsedcm} {f} ano --out {output_dir} --with-pixel-data --batch 75",
                f"{pulsedcm} {f} ano --out {output_dir} --with-pixel-data --batch 100",
                ]
        json_f = f"outputs/hf_{csv_name}.json"
        hf_cmd = [
                "hyperfine",
                "--warmup", config["warmup"],
                "--runs", config["runs"],
                "--ignore-failure",
                "--show-output",
                "--export-json", json_f,
                ]
        for i in commands:
            name = i.split(" ")[1][-2:]
            print("==================", name, "============")
            if i.split(" ")[-1].isnumeric():
                name += "_" + i.split(" ")[-1]
            hf_cmd += ["--command-name",name,i]

        # Run the benchmark
        print("===========================================================")
        print(f"\nRunning {csv_name!r} on folder {data_main_folder}:")
        print("  " + " \\\n  ".join(hf_cmd))
        print("===========================================================")
        subprocess.run(hf_cmd, check=True)


def main():
    compute_hyperfine()
    process_json()

if __name__ == "__main__":
    main()
