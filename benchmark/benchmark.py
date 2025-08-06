import subprocess
import os

pulsedcm = "pulsedcm"
dcmdump  = "dcmdump"
dcmj2pnm = "dcmj2pnm"
dcmodify = "dcmodify"

input_folder     = os.path.join("data")
folders          = [os.path.join(input_folder, i)  for i in os.listdir(input_folder)[:-1]]
output_json      = "tags_all.json"
output_csv       = "tags_all.csv"
ano_output_dir   = "anonymized_output"
repeats          = 5

for current_folder in folders:

    commands = {
            "dump": [
                # PulsedCM
                f"{pulsedcm} {input_folder} tags all",
                f"{pulsedcm} {input_folder} tags short",
                f"{pulsedcm} {input_folder} tags PatientName,PatientID,Modality",
                f"{pulsedcm} {input_folder} tags all --json {output_json}",
                f"{pulsedcm} {input_folder} tags all --csv {output_csv}",
                # DCMTK
                f"{dcmdump} +L +W all {input_folder}",
                f"{dcmdump} +L +W +P PatientName +P PatientID +P Modality {input_folder}",
                f"{dcmdump} +L +W +P PatientName +P PatientID +P StudyDate {input_folder}",
                # JSON export via Python wrapper
                (
                    "bash -c "
                    f"\"{dcmdump} +L +W all {input_folder} | "
                    "python3 -c 'import sys, json, re; tags=[]; "
                    "for ln in sys.stdin: "
                    " m=re.match(r\"\\((....),(....)\\)\\s+([A-Z0-9]+)\\s+\\[?(.*?)\\]?\\s*=\\s*(.*)\", ln); "
                    " if m: tags.append(dict(group=m[1],elem=m[2],vr=m[3],name=m[4],value=m[5])); "
                    " print(json.dumps(tags))'\""
                    ),
                # CSV export via Python wrapper
                (
                    "bash -c "
                    f"\"{dcmdump} +L +W all {input_folder} | "
                    "python3 -c 'import sys, csv, re; "
                    "writer=csv.writer(sys.stdout); writer.writerow([\"group\",\"elem\",\"vr\",\"name\",\"value\"]); "
                    "for ln in sys.stdin: "
                    " m=re.match(r\"\\((....),(....)\\)\\s+([A-Z0-9]+)\\s+\\[?(.*?)\\]?\\s*=\\s*(.*)\", ln); "
                    " if m: writer.writerow(m.groups())' > dcmdump_tags.csv\""
                    ),
                ],
            "view": [
                # PulsedCM
                f"{pulsedcm} {input_folder} view",
                f"{pulsedcm} {input_folder} view --jobs 1",
                # DCMTK 
                f"{dcmj2pnm} +on +Wm +Fa 1 {input_folder} /tmp/{{base}}.png",
                f"{dcmj2pnm} +on +Wm +Fa 1 {input_folder} /tmp/{{base}}.png",
                ],
            "ano": [
                # PulsedCM
                f"{pulsedcm} {input_folder} ano --out {ano_output_dir}",
                f"{pulsedcm} {input_folder} ano --out {ano_output_dir} --action remove",
                f"{pulsedcm} {input_folder} ano --out {ano_output_dir} --action zero",
                f"{pulsedcm} {input_folder} ano --out {ano_output_dir} --policy basic",
                f"{pulsedcm} {input_folder} ano --out {ano_output_dir} --policy strict",
                f"{pulsedcm} {input_folder} ano --out {ano_output_dir} --action zero --policy basic",
                f"{pulsedcm} {input_folder} ano --out {ano_output_dir} --action remove --policy strict",
                # DCMTK
                f"{dcmodify} --replace \"(0010,0010)=\\\"\\\"\" {input_folder}",
                f"{dcmodify} --remove \"(0010,0010)\" {input_folder}",
                f"{dcmodify} --replace \"(0010,0010)=DUMMY\" {input_folder}",
                f"{dcmodify} --replace \"(0010,0010)=\\\"\\\"\" --remove \"(0008,0080)\" {input_folder}",
                (
                    f"{dcmodify} "
                    "--remove \"(0010,0010)\" --remove \"(0010,0020)\" "
                    "--remove \"(0008,0080)\" --remove \"(0008,0070)\" "
                    f"{input_folder}"
                    ),
                ],
}

    for group_name, cmd_list in commands.items():
        csv_out = f"hyperfine_{os.path.basename(current_folder)}_{group_name}.csv"
        hf_cmd = [
                "hyperfine",
                "--warmup", "2",
                "--runs", str(repeats),
                "--export-csv", csv_out
                ]
        for cmd in cmd_list:
            hf_cmd += ["--command-name", cmd, cmd]
        # Run the benchmark
        print(f"\nRunning {group_name!r} on folder {current_folder}:")
        print("  " + " \\\n  ".join(hf_cmd))
        subprocess.run(hf_cmd, check=True)



# Read and print results
# with open(output_json) as f:
#     results = json.load(f)
#
# for result in results["results"]:
#     print(f"{result['command']} — mean: {result['mean']:.4f}s ± {result['stddev']:.4f}s")
