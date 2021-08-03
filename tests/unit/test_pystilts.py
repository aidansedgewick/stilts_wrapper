import os
import pytest

import numpy

from astropy.table import Table

from pystilts import Stilts, StiltsError, utils

class Test__PystiltsTest:

    #def 

    def test__class_init(self,):
        st = Stilts("tskymatch2")
        assert st.task == "tskymatch2"
        assert isinstance(st.known_task_parameters, dict)

        expected_task_keys = [
            "ra1", "ra2", "dec1", "dec2", 
            "find", "join", 
            "ifmt1", "ifmt2", 
            "in1", "in2", 
            "omode", "ofmt",
        ]
        assert all([test_k in st.known_task_parameters.keys() for test_k in expected_task_keys])
        for key in ["ra1", "ra2", "dec1", "dec2"]:
            assert st.known_task_parameters[key] is None
        assert st.known_task_parameters["find"] == ["all", "best", "best1", "best2"]
        assert st.known_task_parameters["join"] == [
            "1and2", "1or2", "all1", "all2", "1not2", "2not1", "1xor2"
        ]

        assert st.parameters == {}
        assert st.cmd == "stilts tskymatch2 " # there is a space, before kwargs are added.

    def test__raises_error_for_unknown_task(self,):
        with pytest.raises(StiltsError):
            failing_stilts1 = Stilts("this_task")
        with pytest.raises(StiltsError):
            failing_stilts2 = Stilts("tskymatch3")

    def test__update_parameters(self,):
        st = Stilts(
            "tskymatch2",
            ra1="old_ra1_expr", dec1="old_dec1_expr", 
            ra2="old_ra2_expr", dec2="old_dec2_expr",
            join="all1", error=0.5
        )
        assert st.parameters["ra2"] == "old_ra2_expr"
        assert st.parameters["dec2"] == "old_dec2_expr"

        assert st.cmd == (
            "stilts tskymatch2 "
            + "ra1=old_ra1_expr dec1=old_dec1_expr ra2=old_ra2_expr dec2=old_dec2_expr "
            + "join=all1 error=0.500000"
        )

        st.update_parameters(ra2="new_ra2_expr", dec2="new_dec2_expr")
        assert st.parameters["ra2"] == "new_ra2_expr"
        assert st.parameters["dec2"] == "new_dec2_expr"
        assert st.cmd == (
            "stilts tskymatch2 "
            + "ra1=old_ra1_expr dec1=old_dec1_expr ra2=new_ra2_expr dec2=new_dec2_expr "
            + "join=all1 error=0.500000"
        )

