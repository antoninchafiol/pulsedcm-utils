import subprocess
import pandas as pd
import os


pulsedcm = "../../pulsedcm/target/release/pulsedcm-cli"
dcmdump  = "dcmdump"
dcmj2pnm = "dcmj2pnm"
dcmodify = "dcmodify"

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
    commands = {
            "dump": [
                # PulsedCM
                f"{pulsedcm} {current_folder} tags all",
                f"{pulsedcm} {current_folder} tags short",
                f"{pulsedcm} {current_folder} tags PatientName,PatientID,Modality",
                f"{pulsedcm} {current_folder} tags all --json {output_json}",
                f"{pulsedcm} {current_folder} tags all --csv {output_csv}",
                # # DCMTK
                f"for f in {current_folder}/* ; do {dcmdump} +L all -M $f ; done",
                f"for f in {current_folder}/* ; do {dcmdump} +L +P PatientName +P PatientID +P Modality $f; done",
                f"for f in {current_folder}/* ; do {dcmdump} +L +P PatientName +P PatientID +P StudyDate $f; done",
                # JSON export via Python wrapper
                f"for f in {current_folder}/* ; do dcm2json $f dcmtk_json_csv/$(basename $f).json ; done",
                f"{find} | parallel dcmdump +L all -M {{}}",
                ],
            "view": [
            #     # PulsedCM
                f"{pulsedcm} {current_folder} view",
                f"{pulsedcm} {current_folder} view --jobs 1",
            #     # DCMTK 
                f"for f in {current_folder}/* ; do {dcmj2pnm} +on +Wm  dcmtk_view/$(basename $f).png ;  done",
                f"{find} | parallel {dcmj2pnm} +on +Wm {{}} dcmtk_view/$(basename $f).png",
                ],
            "ano": [
            #     # PulsedCM
                f"{pulsedcm} {current_folder} ano --out {ano_output_dir}",
                f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --action remove",
                f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --action zero",
                f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --policy basic",
                f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --policy strict",
                f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --action zero --policy basic",
                f"{pulsedcm} {current_folder} ano --out {ano_output_dir} --action remove --policy strict",
            #     # DCMTK
                f"for f in {current_folder}/*; do dcmodify -e \"(0010,0010)\" -e \"(0010,0020)\" -e \"(0010,0030)\" -e \"(0010,0040)\" -e \"(0010,1000)\" -e \"(0010,1001)\" -e \"(0010,1040)\" -e \"(0010,2160)\" -e \"(0010,4000)\" -e \"(0008,0090)\" -e \"(0008,0050)\" -e \"(0008,0080)\" -e \"(0008,0081)\" -e \"(0008,1040)\" -e \"(0008,1010)\" -e \"(0038,0010)\" -e \"(0032,1032)\" -e \"(0032,1060)\" -e \"(0032,1064)\" -e \"(0040,1001)\" -e \"(0040,1003)\" -e \"(0040,1400)\" -e \"(0008,009C)\" -e \"(0010,1060)\" -e \"(0040,0243)\" -e \"(0040,0242)\" -e \"(0040,0254)\" -e \"(0018,1000)\" -e \"(0020,4000)\" -e \"(4008,0114)\" $f ; done",
                f"{find} | parallel dcmodify -e \"\(0010,0010\)\" -e \"\(0010,0020\)\" -e \"\(0010,0030\)\" -e \"\(0010,0040\)\" -e \"\(0010,1000\)\" -e \"\(0010,1001\)\" -e \"\(0010,1040\)\" -e \"\(0010,2160\)\" -e \"\(0010,4000\)\" -e \"\(0008,0090\)\" -e \"\(0008,0050\)\" -e \"\(0008,0080\)\" -e \"\(0008,0081\)\" -e \"\(0008,1040\)\" -e \"\(0008,1010\)\" -e \"\(0038,0010\)\" -e \"\(0032,1032\)\" -e \"\(0032,1060\)\" -e \"\(0032,1064\)\" -e \"\(0040,1001\)\" -e \"\(0040,1003\)\" -e \"\(0040,1400\)\" -e \"\(0008,009C\)\" -e \"\(0010,1060\)\" -e \"\(0040,0243\)\" -e \"\(0040,0242\)\" -e \"\(0040,0254\)\" -e \"\(0018,1000\)\" -e \"\(0020,4000\)\" -e \"\(4008,0114\)\" {{}}",
            #     f"for f in {files}; do {dcmodify} --remove \"(0010,0010)\" < $f > ano_dcmtk/modified_$f; done",
            #     f"for f in {files}; do {dcmodify} --replace \"(0010,0010)=DUMMY\" {current_folder}< $f > ano_dcmtk/modified_$f ; done",
            #     f"for f in {files}; do {dcmodify} --replace \"(0010,0010)=\\\"\\\"\" --remove \"(0008,0080)\" < $f > ano_dcmtk/modified_$f; done",
            #     (
            #         f"{dcmodify} "
            #         "--remove \"(0010,0010)\" --remove \"(0010,0020)\" "
            #         "--remove \"(0008,0080)\" --remove \"(0008,0070)\" "
            #         f"{current_folder}"
            #         ),
                ],
    }

    for group_name, cmd_list in commands.items():
        csv_out = f"hyperfine_results/hyperfine_{os.path.basename(current_folder)}_{group_name}.csv"
        hf_cmd = [
                "hyperfine",
                "--warmup", "2",
                "--runs", str(repeats),
                "--ignore-failure",
                # "--show-output",
                "--export-csv", csv_out,
                "--prepare",
                f"cp data/{current_folder.split('/')[1]}/* {current_folder}/"
                ]
        for cmd in cmd_list:
            hf_cmd += ["--command-name", cmd, cmd]
        
        # Run the benchmark
        print("===========================================================")
        print(f"\nRunning {group_name!r} on folder {current_folder}:")
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


