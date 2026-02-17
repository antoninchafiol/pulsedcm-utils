import subprocess
import pandas as pd
import os


pulsedcm = "../../pulsedcm/target/release/pulsedcm-cli"

input_folder     = os.path.join("tmp")
folders          = [os.path.join(input_folder, i)  for i in os.listdir(input_folder)]
folders          = [i for i in folders if not i.endswith('.csv')]
print(folders)
output_json      = "pulse_json_csv/tags_all.json"
output_csv       = "pulse_json_csv/tags_all.csv"
ano_output_dir   = "anonymization"
repeats          = 5

for current_folder in reversed(folders):
    find = f"find {current_folder} -type f -name \"*.dcm\""
    commands = [
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir}",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 5 --batch 5",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 5 --batch 15",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 5 --batch 25",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 10 --batch 5",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 10 --batch 25",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 10 --batch 15",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 25 --batch 5",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 25 --batch 25",
            f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --workers 25 --batch 15",
    ]

    for i, c in enumerate(commands):
        csv_out = f"hyperfine_results/hyperfine_{os.path.basename(current_folder)}_{i}.csv"
        hf_cmd = [
                "hyperfine",
                "--warmup", "2",
                "--runs", str(repeats),
                "--ignore-failure",
                # "--show-output",
                "--export-csv", csv_out,
                "--prepare",
                f"cp data/{current_folder.split('/')[1]}/* {current_folder}/",
        ]
        for i in commands:
            hf_cmd += ["--command-name",i,i]
        # Run the benchmark
        print("===========================================================")
        print(f"\nRunning {c!r} on folder {current_folder}:")
        print("  " + " \\\n  ".join(hf_cmd))
        print("===========================================================")
        subprocess.run(hf_cmd, check=True)


HF_PATH = "hyperfine_results"

base_df = pd.DataFrame({});

for f in os.listdir(HF_PATH):
    split = f.split("_")
    name = "_".join(split[1:5])
    command = split[-1].split(".")[0]

    df = pd.read_csv(f"{HF_PATH}/{f}")
    df['folder'] = name
    df['command_type'] = command
    base_df = pd.concat([base_df, df])

base_df.to_csv(f"{HF_PATH}/merged_results.csv")


