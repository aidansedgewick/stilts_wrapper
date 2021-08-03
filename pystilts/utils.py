import os
import subprocess
from pathlib import Path

STILTS_EXE = os.environ.get("PYSTILTS_EXE", "stilts")

def get_docs_hint(task):
    hint = f"check docs?\n    {docs_url}/sun256/{task}.html"
    return hint

def task_help(task, parameter=None):
    help_cmd = f"{STILTS_EXE} {task} help"
    if parameter is not None:
        help_cmd += f"={parameter}"
    help = subprocess.getoutput(help_cmd)
    return help

def get_task_parameters(task):
    help = task_help(task)
    spl = help.split()
    assert spl[1] == task
    parameters = {}
    for line in spl[2:]:
        line = line.replace("[", "").replace("]", "")
        param, vals = line.split("=")
        if vals.startswith("<") and vals.endswith(">"):
            accepted = None
        else:
            accepted = vals.split("|")
        #if param.startswith("ifmt") and accepted is None:
        #    accepted = INPUT_FORMATS
        parameters[param] = accepted
    return parameters

def format_flags(config, capitalise=True, float_precision=6):
    """
    Capitalise config keys.
    Convert pathlib.Path types to str
    Convert int to str
    Convert float to six decimal place string
    Convert tuple of int to comma-separated string
    Convert tuple of float to comma-sep string with six decimal places.
    Do nothing to string.
    """
    formatted_config = {}
    for param, value in config.items():
        if capitalise:
            key = param.upper()
        else:
            key = param
        if value is None:
            value = "None"
        if isinstance(value, str):
            formatted_config[key] = value
        elif isinstance(value, Path):
            formatted_config[key] = str(value) # if it's a pathlib Path, fix it for JSON later.
        elif isinstance(value, float):
            formatted_config[key] = f"{value:.{float_precision}f}"
        elif isinstance(value, int):
            formatted_config[key] = str(value)
        elif isinstance(value, SkyCoord):
            formatted_config[key] = f"{value.ra.value:.{float_precision}f},{value.dec.value:.{float_precision}f}"
        elif isinstance(value, tuple):
            if all(isinstance(x, int) for x in value):
                formatted_config[key] = ','.join(f"{x}" for x in value)
            elif all(isinstance(x, float) for x in value):
                formatted_config[key] = ','.join(f"{x:.{float_precision}f}" for x in value)
            else:
                raise ValueError(f"Don't know how to format type {type(value)} - check element types?")
        else:
            raise ValueError(f"Don't know how to format type {type(value)}")
    return formatted_config
