import pytest

import numpy as np

from astropy.coordinates import SkyCoord

from pystilts import utils

def test__get_doc_str():

    assert utils.DOCS_URL == "http://www.star.bris.ac.uk/~mbt/stilts/"

    doc_hint = utils.get_docs_hint("tskymatch2")
    assert doc_hint == (
        "check docs?\n    http://www.star.bris.ac.uk/~mbt/stilts/sun256/tskymatch2.html"
    )


def test__get_task_help():
    string1 = utils.get_task_help("tskymatch2")
    
def test__get_stilts_version():
    vers = utils.get_stilts_version()
    assert isinstance(vers, str)
    # not sure what else to test

def test__get_stil_version():
    vers = utils.get_stil_version()
    assert isinstance(vers, str)
    

def test__format_parameters():
    test_config = {
        "tuple_int_test": (100, 400, 9000),
        "tuple_float_test": (1234.543, 6000.),
        "none_test": None,
        "float_test": 3.14159265358979324,
        "int_test": 200,
        "str_test": "my_string123",
        "test_coord": SkyCoord(ra=98.765, dec=-45.999, unit="deg")
    }
    
    output_config = utils.format_parameters(test_config)
    assert output_config["TUPLE_INT_TEST"] == "100,400,9000"
    assert output_config["TUPLE_FLOAT_TEST"] == "1234.543000,6000.000000"
    assert output_config["NONE_TEST"] == "None"
    assert output_config["FLOAT_TEST"] == "3.141593"
    assert output_config["INT_TEST"] == "200"
    assert output_config["STR_TEST"] == "my_string123"
    assert output_config["TEST_COORD"] == "98.765000,-45.999000"

    input_lower = {"lower_case": 1000}
    output_lower = utils.format_parameters(input_lower, capitalise=False)
    assert output_lower["lower_case"] == "1000"
    assert "LOWER_CASE" not in output_lower

    with pytest.raises(ValueError):
        failing_input1 = {"test1": (1000., 1000)} # tuple of mixed types.
        fail1 = utils.format_parameters(failing_input1)
    
    with pytest.raises(ValueError):
        failing_input2 = {"test1": np.array([1,2,3])}
        fail2 = utils.format_parameters(failing_input2)
