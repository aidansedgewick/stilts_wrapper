import os
import logging
import subprocess
import yaml

from .known_tasks import KNOWN_TASKS
from .utils import format_flags

logger = logging.getLogger("stilts_wrapper")

DOCS_URL = "http://www.star.bris.ac.uk/~mbt/stilts/"

STILTS_EXE = os.environ.get("PYSTILTS_EXE", "stilts")

INPUT_FORMATS = None

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
        if param.startswith("ifmt") and accepted is None:
            accepted = INPUT_FORMATS
        parameters[param] = accepted
    return parameters
        
    

class StiltsError(Exception):
    pass


class Stilts:
    def __init__(self, task, strict_parameters=True, **kwargs):
        if task not in KNOWN_TASKS["all_tasks"]:
            raise StiltsError(f"Task {task} not known.")
        self.task = task
        
        self.known_task_parameters = get_task_parameters(self.task)
        if strict_parameters:
            for key, val in kwargs.items():
                if key not in self.known_task_parameters:
                    raise StiltsError()
                accepted = self.known_task_parameters[key]
                if accepted is not None:
                    if val not in accepted:
                        raise StiltsError(
                        f"'{val}' not in accepted {accepted} for parameter '{key}'")
            
        self.parameters = kwargs
        self.build_cmd()

    def build_cmd(self, float_precision=6):
        cmd = f"{STILTS_EXE} {self.task} "
        flags = format_flags(self.parameters, capitalise=False, float_precision=float_precision)
        cmd += " ".join(f"{k}={v}" for k, v in self.parameters.items())
        self.cmd = cmd

    def update_parameters(self, **kwargs):
        self.parameters.update(kwargs)
        self.build_cmd()
    
    def set_all_formats(self, fmt):        
        fmt_flags = {"omode": "out", "ofmt": fmt}        
        inN_keys = [k for k in self.parameters.keys() if k.startswith("in")]
        for inN_key in inN_keys:
            fmtN_key = inN_key.replace("in", "ifmt")
            fmt_flags[fmtN_key] = fmt      
        self.update_parameters(**fmt_flags)

    def run(self, verbose=False, strict=True):
        if verbose:
            logger.info("run \033[031m{self.task.upper()}\033[0m")
            logger.info("{self.cmd}")
        
        status = subprocess.call(self.cmd, shell=True)
        self.status = status        

        if strict and status > 0:
            print()
            docs_hint = get_docs_hint(self.task)
            errormsg = f"run: Something went wrong (status={status}).\n{docs_hint}"
            raise StiltsError(error_msg)
        return status

    #def task_help(self, task, parameter=None):
        
#class TableTasks(BaseStilts):
#    def __init__(self,):
#        pass


