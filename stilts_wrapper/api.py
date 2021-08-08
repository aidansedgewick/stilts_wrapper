import os
import logging
import subprocess
import traceback
import yaml
from pathlib import Path

from astropy.table import Table

from .known_tasks import load_known_tasks, load_known_flags
from .exc import StiltsError, StiltsUnknownTaskError, StiltsUnknownParameterError
from . import utils

STILTS_EXE = utils.STILTS_EXE
STILTS_FLAGS = load_known_flags()
KNOWN_TASKS = load_known_tasks()["all_tasks"]

logger = logging.getLogger("stilts_wrapper")

class Stilts:

    STILTS_EXE = utils.STILTS_EXE
    KNOWN_TASKS = KNOWN_TASKS

    INPUT_FORMATS = None
    OUTPUT_FORMATS = None

    stilts_version = utils.get_stilts_version()
    stil_version = utils.get_stil_version()

    def __init__(
        self, task, *args, strict=True, warning=True, **kwargs
    ):
        self.strict = strict        
        self.warning = warning

        if strict and task not in self.KNOWN_TASKS:
            raise StiltsUnknownTaskError(f"Task {task} not known.")
        self.task = task

        try:
            self.known_task_parameters = utils.get_task_parameters(self.task)
        except:
            self.known_task_parameters = {}

        self.flags = {x: None for x in args}
        flag_kwargs = [k for k in kwargs.keys() if k in STILTS_FLAGS]
        for flag in flag_kwargs:
            self.flags[flag] = kwargs.pop(flag)
        
        self.cleanup_paths = []
        self.parameters = kwargs
        self.fix_parameter_keys()

        #====== deal with astropy tables        
        to_update = {}
        for key, val in self.parameters.items():
            if isinstance(val, Table):
                output_path = Path.cwd() / f"api_written_temp_{task}_{key}.cat.fits"
                val.write(output_path, overwrite=True)
                logger.info(f"written {key} to {output_path}")
                to_update[key] = output_path
                if key.startswith("in"):
                    fmt_key = key.replace("in", "ifmt")
                    to_update[fmt_key] = "fits"
                self.cleanup_paths.append(output_path)
        self.parameters.update(to_update)

        #====== check parameters are reasonable
        if self.strict or self.warning:
            utils.check_flags(self.flags, strict=self.strict, warning=self.warning)
            utils.check_parameters(
                kwargs, 
                self.known_task_parameters, 
                strict=self.strict, 
                warning=self.warning
            )

        #====== ...build the command!
        self.build_cmd()

    def fix_parameter_keys(self,):
        to_fix = [k for k in self.parameters.keys() if k.endswith("_")]
        for k in to_fix:
            self.parameters[k[:-1]] = self.parameters.pop(k)

    def build_cmd(self, float_precision=6):
        cmd = f"{self.STILTS_EXE} {self.task} "
       
        #======== Do flags first.
        if len(self.flags) > 0:
            formatted_flags = utils.format_parameters(
                self.flags, capitalise=False, float_precision=float_precision
            )
            cmd += " ".join(
                f"-{flag}" if val == "None" else f"-{flag} {val}" 
                for flag, val in formatted_flags.items()
            ) + " "

        #======= Now do parameters.
        formatted_parameters = utils.format_parameters(
            self.parameters, capitalise=False, float_precision=float_precision
        )
        cmd += " ".join(
            f"{param}={val}" for param, val in formatted_parameters.items()
        )
        self.cmd = cmd

    def update_parameters(self, **kwargs):
        self.parameters.update(kwargs)
        self.fix_parameter_keys()
        if self.strict or self.warning:
            utils.check_parameters(
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

    def run(self, verbose=False, strict=None, cleanup=True):
        if verbose:
            logger.info("run \033[031m{self.task.upper()}\033[0m")
            logger.info("{self.cmd}")
        
        status = subprocess.call(self.cmd, shell=True)
        self.status = status
        if cleanup:
            self.cleanup()
        strict = strict or self.strict
        if strict and status > 0:
            print()
            docs_hint = utils.get_docs_hint(self.task)
            errormsg = f"run: Something went wrong (status={status}).\n{docs_hint}"
            raise StiltsError(errormsg)
        return status

    def cleanup(self,):
        for path in self.cleanup_paths:
            logger.info("removing temporary table at {path}")
            if "api_written_temp" not in str(path):
                raise StiltsError(
                    f"Can't delete {path}:\n"
                    f"I won't remove data that I've not written myself."
                )
            os.remove(path)

    @classmethod
    def tskymatch2(cls, *args, all_formats=None, **kwargs):
        stilts = cls("tskymatch2", *args, **kwargs)
        if all_formats is not None:
            stilts.set_all_formats(all_formats)
        return stilts

    @classmethod
    def tmatch2(cls, *args, all_formats=None, **kwargs):
        stilts = cls("tmatch2", *args, **kwargs)
        if all_formats is not None:
            stilts.set_all_formats(all_formats)
        return stilts

    @classmethod
    def tmatch1(cls, *args, all_formats=None, **kwargs):
        stilts = cls("tmatch1", *args, **kwargs)
        if all_formats is not None:
            stilts.set_all_formats(all_formats)
        return stilts

    @classmethod
    def tmatchn(cls, *args, all_formats=None, **kwargs):
        stilts = cls("tmatchn", *args, **kwargs)
        if all_formats is not None:
            stilts.set_all_formats(all_formats)
        return stilts




