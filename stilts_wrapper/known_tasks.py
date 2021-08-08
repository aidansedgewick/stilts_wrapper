import os
import subprocess
import yaml
from pathlib import Path

STILTS_EXE = os.environ.get("STILTS_WRAPPER_EXE", "stilts")
INPUT_FORMATS = [
    "fits", "colfits", "votable", "cdf", "csv", "ecsv", "acsii", "ipac",
    "mrt", "parquet", "feather", "gbin", "tst", "wdc"
]

config_dir = Path(__file__).absolute().parent / "configuration"
known_tasks_path = config_dir / "known_tasks.yaml"
expected_parameters_path = config_dir / "expected_parameters.yaml"

def load_known_tasks(known_tasks_path=known_tasks_path):
    with open(known_tasks_path, "r") as f:
        known_tasks = yaml.load(f, Loader=yaml.FullLoader)
        known_tasks["all_tasks"] = [
            task for task_type in known_tasks.values() for task in task_type
        ]
    return known_tasks

def load_known_flags():
    """
    pattern = re.compile("\[([-\w\s\<\>])+\]")
    for match in pattern.finditer(flagstr):
        print(match)
        # this missed [checkversion <vers>] bc it has white space. adding \s breaks all.
    """
    # TODO fix regex!
    flagstr = (
        "[-help] [-version] [-verbose] [-allowunused] [-prompt] [-bench] "
        "[-debug] [-batch] [-memory] [-disk] [-memgui] "
        "[-checkversion <vers>] [-stdout <file>] [-stderr <file>] "
    )
    flagstr = flagstr.replace("-","")
    flags = []
    curr = ""
    for x in flagstr:
        if x not in "[]":
            curr += x
        else:
            if len(curr.strip()) > 0:
                flags.append( curr.split()[0] )
            curr = ""
    return flags

def dump_expected_parameters(
    known_tasks, expected_parameters_path=expected_parameters_path
):
    expected_parameters = {}
    for task in known_tasks:
        help_str = subprocess.getoutput(f"{STILTS_EXE} {task} help")
        help_str.split()
        parameters = {}
        for line in spl[2:]:
            line = line.replace("[", "").replace("]", "")
            try:
                param, vals = line.split("=")
            except:
                continue            
            if vals.startswith("<") and vals.endswith(">"):
                accepted = None
            else:
                accepted = vals.split("|")
                if "..." in accepted:
                    accepted = None
            if param.startswith("ifmt") and accepted is None:
                accepted = INPUT_FORMATS
            parameters[param] = accepted
        expected_parameters[task] = parameters
    with open(expected_parameters_path, "w+") as out:
        yaml.dump(expected_parameters, out)

def load_expected_parameters(
    expected_parameters_path=expected_parameters_path
):
    with open(expected_parameters_path, "r") as f:
        expected_parameters = yaml.load(f, Loader=yaml.FullLoader)
    return expected_parameters

if __name__ == "__main__":
    KNOWN_TASKS = load_known_tasks()
    dump_expected_parameters(KNOWN_TASKS["all_tasks"])
