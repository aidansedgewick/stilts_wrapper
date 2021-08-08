import os
import yaml
from pathlib import Path

STILTS_EXE = os.environ.get("STILTS_WRAPPER_EXE", "stilts")
INPUT_FORMATS = [
    "fits", "colfits", "votable", "cdf", "csv", "ecsv", "acsii", "ipac",
    "mrt", "parquet", "feather", "gbin", "tst", "wdc"
]

config_dir = Path(__file__).absolute().parent / "configuration"
known_tasks_path = config_dir / "known_tasks.yaml"
expected_tasks_path = config_dir / "expected_parameters.yaml"

def _load_known_tasks(known_tasks_path=known_tasks_path):
    with open(known_tasks_path, "r") as f:
        known_tasks= yaml.load(f, Loader=yaml.FullLoader)
        known_tasks["all_tasks"] = [
            task for task_type in known_tasks.values() for task in task_type
        ]
    return known_tasks

def _dump_expected_parameters(
    known_tasks, expected_parameters_path=expected_parameters_path
):
    expected_parameters = {}
    for task in known_tasks:
        help_cmd = f"{STILTS_EXE} {task} help"
        spl = help.split()
        for line in spl[2:]:
            line = line.replace("[", "").replace("]", "")
            param, vals = line.split("=")
            
            if vals.startswith("<") and vals.endswith(">"):
                accepted = None
            else:
                accepted = vals.split("|")
            if param.startswith("ifmt") and accepted is None:
                accepted = INPUT_FORMATS
            parameters[param] = accepted
        expected_parameters[task] = parameters
    with open(expected_parameters_path, "w+") as f:
        yaml.dump(expeceted_parameters, f)

def _load_expected_parameters(
    expected_parameters_path=expected_parameters_path
    ):
    with open()
    
KNOWN_TASKS = _load_known_tasks()
EXPECTED_PARAMETERS = _load_expected_parameters()

if __name__ == "__main__":
    _dump_known_tasks(KNOWN_TASKS)
