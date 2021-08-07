import os
import logging
import subprocess
import traceback
import yaml
from pathlib import Path

from astropy.table import Table

from .known_tasks import KNOWN_TASKS
from .exc import StiltsError, StiltsUnknownTaskError, StiltsUnknownParameterError
from pystilts import utils

STILTS_EXE = utils.STILTS_EXE
STILTS_FLAGS = utils.get_stilts_flags()

logger = logging.getLogger("stilts_wrapper")

class Stilts:

    STILTS_EXE = utils.STILTS_EXE
    KNOWN_TASKS = KNOWN_TASKS

    INPUT_FORMATS = None
    OUTPUT_FORMATS = None

    stilts_version = utils.get_stilts_version()
    stil_version = utils.get_stil_version()

    def __init__(self, task, strict=True, warning=True, *args, **kwargs):

        self.strict = strict        
        self.warning = warning

        if strict and task not in self.KNOWN_TASKS["all_tasks"]:
            raise StiltsUnknownTaskError(f"Task {task} not known.")
        self.task = task

        try:
            self.known_task_parameters = utils.get_task_parameters(self.task)
        except:
            self.known_task_parameters = {}
 
        self.flags = {x: None for x in args}
        flag_kwargs = [k for k in kwargs.keys() if k in STILTS_FLAGS]
        for flag in flag_kwargs:
            self.flags[flag] = kwargs.pop(kwargs)
        
        self.cleanup_paths = []
        self.parameters = kwargs
        to_update = {}
        to_fix = [k for k in self.parameters.keys() if k.endswith("_")]
        for k in to_fix:
            self.parameters[k[:-1]] = self.parameters.pop(k)
        for key, val in self.parameters.items():
            if isinstance(val, Table):
                output_path = Path.cwd() / f"stilts_wrapper_{task}_{key}.cat.fits"
                try:
                    val.write(output_path)
                    logger.info(f"written {key} to {output_path}")
                    to_update[key] = output_path
                    if key.startswith("in"):
                        fmt_key = key.replace("in", "ifmt")
                        to_update[fmt_key] = "fits"
                    self.cleanup_paths.append(output_path)
                except Exception:
                    traceback.print_exc()
                    raise StiltsError(
                        f"Couldn't write table to {output_path}. Does it already exist?\n"
                        f"Try deleting this path by hand.\n"
                        f"Or try saving the table first, and passing a path as normal."
                    )
        self.parameters.update(to_update)


        if self.strict or self.warning:
            utils.check_flags(self.flags, strict=self.strict, warning=self.warning)
            utils.check_parameters(
                kwargs, 
                self.known_task_parameters, 
                strict=self.strict, 
                warning=self.warning
            )
        self.build_cmd()
           

    def build_cmd(self, float_precision=6):
        cmd = f"{self.STILTS_EXE} {self.task} "
        formatted_parameters = utils.format_parameters(
            self.parameters, capitalise=False, float_precision=float_precision
        )
        cmd += " ".join(f"{k}={v}" for k, v in formatted_parameters.items())
        self.cmd = cmd

    def update_parameters(self, **kwargs):
        self.parameters.update(kwargs)
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

    def run(self, verbose=False, strict=True, cleanup=True):
        if verbose:
            logger.info("run \033[031m{self.task.upper()}\033[0m")
            logger.info("{self.cmd}")
        
        status = subprocess.call(self.cmd, shell=True)
        self.status = status
        if cleanup:
            self.cleanup()
        if strict and status > 0:
            print()
            docs_hint = utils.get_docs_hint(self.task)
            errormsg = f"run: Something went wrong (status={status}).\n{docs_hint}"
            raise StiltsError(error_msg)
        return status

    def cleanup(self,):
        for path in self.cleanup_paths:
            logger.info("removing temporary table at {path}")
            if "stilts_wrapper" not in str(path):
                raise StiltsError(
                    f"Can't delete {path}:\n"
                    f"I won't remove data that I've not written myself."
                )
            os.remove(path)

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




