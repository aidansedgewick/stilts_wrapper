import os
import pytest
from pathlib import Path

import numpy as np

from astropy.table import Table

from pystilts import (
    Stilts, StiltsError, StiltsUnknownParameterError, StiltsUnknownTaskError, utils
)

class Test__PystiltsTest:

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
        with pytest.raises(StiltsUnknownTaskError):
            failing_stilts1 = Stilts("this_task")
        with pytest.raises(StiltsUnknownTaskError):
            failing_stilts2 = Stilts("tskymatch3")

        # ...but can provide bad parameter with strict = False
        stilts = Stilts("bad_task", strict=False)
        assert stilts.task == "bad_task"

    def test__raises_error_for_unknown_parameters(self,):
        with pytest.raises(StiltsUnknownParameterError):
            failing_stilts1 = Stilts("tskymatch2", bad_parameter=1.0)
        stilts = Stilts("tskymatch2", join="all1")
        assert stilts.parameters["join"] == "all1"
        with pytest.raises(StiltsUnknownParameterError):
            failing_stilts2 = Stilts("tskymatch2", join="bad_value")

        # ...but can provide bad parameters with strict=False
        s1 = Stilts("tskymatch2", bad_parameter=1.0, strict=False)
        print(s1.cmd)
        assert np.isclose(s1.parameters["bad_parameter"], 1.0)
        s2 = Stilts("tskymatch2", join="bad_value", strict=False)
        assert s2.parameters["join"] == "bad_value"

    def test__input_astropy_table(self,):
        tab = Table({
            "col1": np.random.uniform(0, 1, 10),
            "col2": np.random.uniform(0, 1, 10),
        })
        expected_path = Path.cwd() / "stilts_wrapper_tmatch2_in1.cat.fits"
        st = Stilts("tmatch2", in1=tab, values1=1.0)
        assert expected_path.exists()
        os.remove(expected_path)
        assert not expected_path.exists()

    def test__reserved_keyword_as_parameter(self,):
        st = Stilts("tmatch1", in_="catalog.cat.fits", values=1.0)
        assert "in_" not in st.parameters
        assert "in" in st.parameters
        assert "values" in st.parameters        

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

    def test__param_checker_for_paramN(self,):
        st = Stilts("tmatchn", in3="table3.cat.fits", ifmt3="csv")
        assert "in3" not in st.known_task_parameters
        assert "inN" in st.known_task_parameters


    def test__cleanup(self,):
        tab = Table({
            "col1": np.random.uniform(0, 1, 10),
            "col2": np.random.uniform(0, 1, 10),
        })
        expected_path = Path.cwd() / "stilts_wrapper_tmatch1_in.cat.fits"
        st = Stilts("tmatch1", in_=tab, values=1.0)
        assert expected_path.exists()
        st.cleanup()
        assert not expected_path.exists()

        input_path = Path.cwd() / "very_important_do_not_delete.cat.fits"
        tab.write(input_path)
        st = Stilts("tmatch1", in_=input_path)
        st.cleanup_paths.append(input_path) # Oh no, accidentally add to list to be deleted.
        with pytest.raises(StiltsError):
            # Actually, it won't be deleted - it doesn't have "stilts_wrapper" in the name.
            st.cleanup()
        assert input_path.exists()
        os.remove(input_path)
        assert not input_path.exists()


    def test__set_all_formats(self,):
        stilts1 = Stilts("tskymatch2", in1="this_path.cat.fits", in2="that_path.cat.fits")
        assert "ifmt1" not in stilts1.parameters
        assert "ifmt2" not in stilts1.parameters
        assert "omode" not in stilts1.parameters
        assert "ofmt" not in stilts1.parameters

        assert stilts1.cmd == (
            "stilts tskymatch2 in1=this_path.cat.fits in2=that_path.cat.fits"
        )

        stilts1.set_all_formats("fits")
        assert stilts1.parameters["ifmt1"] == "fits"
        assert stilts1.parameters["ifmt2"] == "fits"
        assert stilts1.parameters["omode"] == "out"
        assert stilts1.parameters["ofmt"] == "fits"

        assert "ifmt1=fits" in stilts1.cmd
        assert "ifmt2=fits" in stilts1.cmd
        assert "omode=out" in stilts1.cmd
        assert "ofmt=fits" in stilts1.cmd        

        stilts2 = Stilts(
            "tmatchn", 
            nin=4,
            in1="path1.cat.fits", 
            in2="path2.cat.fits", 
            in3="path3.cat.fits",
            in4="path3.cat.fits",
        )
        assert "ifmt1" not in stilts2.parameters
        assert "ifmt2" not in stilts2.parameters
        assert "ifmt3" not in stilts2.parameters
        assert "ifmt4" not in stilts2.parameters
        assert "omode" not in stilts2.parameters
        assert "ofmt" not in stilts2.parameters

        stilts2.set_all_formats("fits")
        assert stilts2.parameters["ifmt1"] == "fits"
        assert stilts2.parameters["ifmt2"] == "fits"
        assert stilts2.parameters["ifmt3"] == "fits"
        assert stilts2.parameters["ifmt4"] == "fits"
        assert stilts2.parameters["omode"] == "out"
        assert stilts2.parameters["ofmt"] == "fits"

        assert "ifmt1=fits" in stilts2.cmd
        assert "ifmt2=fits" in stilts2.cmd
        assert "ifmt3=fits" in stilts2.cmd
        assert "ifmt4=fits" in stilts2.cmd
        assert "omode=out" in stilts2.cmd
        assert "ofmt=fits" in stilts2.cmd        

    def test__tskymatch2_convenience_method(self,):
        m = Stilts.tskymatch2(
            in1="./table1.cat.fits", 
            in2="./table2.cat.fits",
            ra1="ra_1",
            dec1="dec_1",
            ra2="ra_2",
            dec2="dec_2",
            join="all1", 
            all_formats="fits", 
        )
        
        assert m.task == "tskymatch2"
        assert m.parameters["ifmt1"] == "fits"
        assert m.parameters["ifmt2"] == "fits"
        assert m.parameters["omode"] == "out"
        assert m.parameters["ofmt"] == "fits"
        assert m.parameters["ra1"] == "ra_1"
        assert m.parameters["ra2"] == "ra_2"
        assert m.parameters["dec1"] == "dec_1"
        assert m.parameters["dec2"] == "dec_2"

        ## test still fails for bad inputs
        with pytest.raises(StiltsUnknownParameterError):
            m_f1 = Stilts.tskymatch2(bad_param=1.0)
        with pytest.raises(StiltsUnknownParameterError):
            m_f2 = Stilts.tskymatch2(join="bad_option")


    def test__tmatch2_convenience_method(self,):
        pass

    

