import os
import logging
import subprocess
import yaml

from .known_tasks import KNOWN_TASKS
from .utils import get_docs_hint, task_help, get_task_parameters, format_flags, STILTS_EXE

logger = logging.getLogger("stilts_wrapper")

class StiltsError(Exception):
    pass

class StiltsUnknownParameterError(StiltsError):
    pass

class StiltsUnknownTaskError(StiltsError):
    pass

def check_parameters(
    input_parameters: dict, expected_parameters: dict, strict=True, warning=True
):
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
                    f"parameter {key}, expected are {expected_parameters.keys()}"
                )
            if warning:
                logger.warning(
                    f"parameter {key}, expected are {expected_parameters.keys()}"
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

class Stilts:

    STILTS_EXE = STILTS_EXE
    KNOWN_TASKS = KNOWN_TASKS

    INPUT_FORMATS = None
    OUTPUT_FORMATS = None

    def __init__(self, task, strict=True, warning=True, **kwargs):

        self.strict = strict        
        self.warning = warning

        if strict and task not in self.KNOWN_TASKS["all_tasks"]:
            raise StiltsUnknownTaskError(f"Task {task} not known.")
        self.task = task



        try:
            self.known_task_parameters = get_task_parameters(self.task)
        except:
            self.known_task_parameters = {}
 
        self.parameters = kwargs
        if self.strict or self.warning:
            check_parameters(
                kwargs, 
                self.known_task_parameters, 
                strict=self.strict, 
                warning=self.warning
            )

        self.build_cmd()

    def build_cmd(self, float_precision=6):
        cmd = f"{self.STILTS_EXE} {self.task} "
        formatted_parameters = format_flags(
            self.parameters, capitalise=False, float_precision=float_precision
        )
        cmd += " ".join(f"{k}={v}" for k, v in formatted_parameters.items())
        self.cmd = cmd

    def update_parameters(self, **kwargs):
        self.parameters.update(kwargs)
        if self.strict or self.warning:
            check_parameters(
                self.parameters, 
                self.known_task_parameters, 
                strict=self.strict, 
                warning=self.warning
            )

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

    @classmethod
    def tskymatch2(cls, all_formats=None, **kwargs):
        stilts = cls("tskymatch2", **kwargs)
        if all_formats is not None:
            stilts.set_all_formats(all_formats)
        return stilts

    @classmethod
    def tmatch2(cls, all_formats=None, **kwargs):
        stilts = cls("tmatch2", **kwargs)
        if all_formats is not None:
            stilts.set_all_formats(all_formats)
        return stilts

    @classmethod
    def tmatch1(cls, all_formats=None, **kwargs):
        stilts = cls("tmatch1", **kwargs)
        if all_formats is not None:
            stilts.set_all_formats(all_formats)
        return stilts

    @classmethod
    def tmatchn(cls, all_formats=None, **kwargs):
        stilts = cls("tjoin", **kwargs)
        if all_formats is not None:
            stilts.set_all_formats(all_formats)
        return stilts




