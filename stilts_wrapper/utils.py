import os
import logging
import re
import subprocess
from pathlib import Path

from astropy.coordinates import SkyCoord

from .exc import StiltsError, StiltsUnknownTaskError, StiltsUnknownParameterError

logger = logging.getLogger("stilts_utils")

STILTS_EXE = os.environ.get("PYSTILTS_EXE", "stilts")
DOCS_URL = "http://www.star.bris.ac.uk/~mbt/stilts/"

def get_docs_hint(task):
    hint = f"check docs?\n    {DOCS_URL}sun256/{task}.html"
    return hint

def get_task_help(task, parameter=None):
    help_cmd = f"{STILTS_EXE} {task} help"
    if parameter is not None:
        help_cmd += f"={parameter}"
    help = subprocess.getoutput(help_cmd)

    if "SYNOPSIS" in help:
        pass
    return help

def get_task_parameters(task):
    help = get_task_help(task)
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

def get_stilts_flags():
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


def get_stilts_version():
    vers_output = subprocess.getoutput("stilts -version").replace("\n"," ")
    p = re.compile("STILTS version ([\d.-]+)")
    res = p.search(vers_output)
    return res.group(1)

def get_stil_version():
    vers_output = subprocess.getoutput("stilts -version").replace("\n"," ")
    p = re.compile("STIL version ([\d.-]+)")
    res = p.search(vers_output)
    return res.group(1)

def check_parameters(
    input_parameters: dict, expected_parameters: dict, strict=True, warning=True
):
    if isinstance(expected_parameters, dict) and len(expected_parameters) == 0:
        logger.warning("something went wrong finding the expected parameters.")

    for key, val in input_parameters.items():

        # what if we're given "ifmt3" and known tasks only knows about "ifmtN" ?
        bare_parameter = "".join(x for x in key if x.isalpha())
        if bare_parameter + "N" in expected_parameters:
            param = bare_parameter + "N"
        else:
            param = key

        if param not in expected_parameters:
            print("we got here", strict, warning, param)
            if strict:
                print("strict is",  strict, warning, param)
                raise StiltsUnknownParameterError(
                    f"unknown parameter '{key}', expected are {expected_parameters.keys()}"
                )
            if warning:
                logger.warning(
                    f"unknown parameter '{key}', expected are {expected_parameters.keys()}"
                )
            continue # if param is not in expected, then we can't get accepted options!

        accepted = expected_parameters.get(param, None)
        if accepted is not None:
            if val not in accepted:
                if strict:
                    raise StiltsUnknownParameterError(
                        f"'{val}' not in accepted {accepted} for parameter '{key}'"
                    )
                if warning:
                    logger.warning(
                        f"'{val}' not in accepted {accepted} for parameter '{key}'"
                    )

def check_flags(input_flags: dict, strict=True, warning=True):
    for flag in input_flags.keys():
        if flag not in STILTS_FLAGS and strict:
            raise ValueError(f"flag {flag} unknown: {STILTS_FLAGS}")
        if warning:
            logger.warning(f"flag {flag} unknown: {STILTS_FLAGS}")


def format_parameters(config, capitalise=True, float_precision=6):
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
