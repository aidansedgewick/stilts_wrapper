import os
import pytest
from pathlib import Path

import numpy as np

from astropy.table import Table

from stilts_wrapper import (
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

    def test__accepts_flags(self,):
        m = Stilts("tmatch2", "verbose", in1="test.fits")
        print(m.flags)
        assert "verbose" in m.flags
        assert "-verbose" in m.cmd
        assert "in1" in m.parameters
        with pytest.raises(StiltsError):
            m2 = Stilts("tmatchn", "a_bad_flag")
        m3 = Stilts("tmatch2", "a_bad_flag", strict=False)
        assert "a_bad_flag" in m3.flags

    def test__convert_flags_with_values(self,):
        m = Stilts("tmatch2", "verbose", stdout="stdout_here", in1="table.fits")
        assert "verbose" in m.flags
        assert " -verbose " in m.cmd
        assert "stdout" in m.flags
        assert " -stdout stdout_here " in m.cmd
        assert "stdout" not in m.parameters
        assert "in1" in m.parameters
    
    def test__input_astropy_table(self,):
        tab = Table({
            "col1": np.random.uniform(0, 1, 10),
            "col2": np.random.uniform(0, 1, 10),
        })
        expected_path = Path.cwd() / "api_written_temp_tmatch2_in1.cat.fits"
        if expected_path.exists():
            os.remove(expected_path)
        assert not expected_path.exists()
        st = Stilts("tmatch2", in1=tab, values1=1.0)
        assert expected_path.exists()
        os.remove(expected_path)
        assert not expected_path.exists()

    def test__astropy_overwrite(self,):
        pass

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
        expected_path = Path.cwd() / "api_written_temp_tmatch1_in.cat.fits"
        if expected_path.exists():
            os.remove(expected_path)
        assert not expected_path.exists()
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
        m = Stilts.tmatch2(in1="table1.fits", in2="table2.fits", values1=1.0)
        assert m.task == "tmatch2"
        assert m.parameters["in1"] == "table1.fits"
        assert m.parameters["in2"] == "table2.fits"
        assert np.isclose(m.parameters["values1"], 1.0)

    def test__tmatch1_convenience_method(self,):
        m = Stilts.tmatch1(in_=Path.cwd()/"my_table.fits")
        assert m.task == "tmatch1"
        assert "in=" + str(Path.cwd()) + "/my_table.fits" in m.cmd  # ie, properly formatted.

    def test__tmatchn_convenience_method(self,):
        m = Stilts.tmatchn(
            in1="in1.csv", in2="in2.csv", in3="in3.csv", in4="in4.csv",
            all_formats="csv"
        )

        assert m.task == "tmatchn"
        assert m.parameters["ifmt1"] == "csv"
        assert m.parameters["ifmt2"] == "csv"
        assert m.parameters["ifmt3"] == "csv"
        assert m.parameters["ifmt4"] == "csv"
        assert m.parameters["omode"] == "out"
        assert m.parameters["ofmt"] == "csv"

    def test__do_tskymatch2(self,):
        tab1 = Table({
            "Jra": np.linspace(1, 10, 10).astype(float),
            "Jdec": np.zeros(10).astype(float),
            "Jmag": np.linspace(15.5, 20.5, 10),
        })
        tab2 = Table({
            "Kra": np.linspace(0, 9, 10).astype(float) + 1e-5, 
            "Kdec": np.zeros(10).astype(float),
            "Kmag": np.linspace(16., 21., 10),
        })
        
        exp1_path = Path.cwd() / "api_written_temp_tskymatch2_in1.cat.fits"
        if exp1_path.exists():
            os.remove(exp1_path)
        assert not exp1_path.exists()
        exp2_path = Path.cwd() / "api_written_temp_tskymatch2_in2.cat.fits"
        if exp2_path.exists():
            os.remove(exp2_path)
        assert not exp2_path.exists()

        outpath = Path.cwd() / "run_test_tskymatch2.cat.fits"
        if outpath.exists():
            os.remove(outpath)
        assert not outpath.exists()

        matcher = Stilts.tskymatch2(
            in1=tab1, in2=tab2, out=outpath, all_formats="fits", join="1or2", find="best",
            ra1="Jra", dec1="Jdec", ra2="Kra", dec2="Kdec",
            error=1.0,
        )
        # check we have written the tables.
        assert exp1_path.exists()
        assert exp2_path.exists()

        matcher.run()
        assert outpath.exists()

        assert not exp1_path.exists()        
        assert not exp2_path.exists()

        catalog = Table.read(outpath)
        assert len(catalog) == 11

        assert set(catalog.columns) == set(
            ["Jra", "Jdec", "Jmag", "Kra", "Kdec", "Kmag", "Separation"]
        )

        assert sum(np.isfinite(catalog["Jmag"])) == 10
        assert sum(np.isfinite(catalog["Kmag"])) == 10

        #assert np.allclose(catalog["Jmag"][1:-1] - catalog["Kmag"][1:-1], 1.0)
        
        os.remove(outpath)
        assert not outpath.exists()



    def test__will_raise_error_for_bad_input(self,):
        tab1 = Table({
            "x": np.random.uniform(0, 100, 50),
            "y": np.random.uniform(0, 100, 50),
        })
        st = Stilts.tmatchn(in1=tab1)
        # python class has initialised ok
        exp_path = Path.cwd() / "api_written_temp_tmatchn_in1.cat.fits"
        assert exp_path.exists()

        with pytest.raises(StiltsError):
            st.run()
        assert not exp_path.exists() # cleanup happens regardless.
        
        # can run with bad input without raising python error.
        st2 = Stilts.tmatchn(in1=tab1, strict=False)
        assert exp_path.exists()
        status = st2.run()
        assert status > 0
        assert not exp_path.exists()
        
        




    

