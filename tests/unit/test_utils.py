import pytest

from pystilts import utils

def test__get_doc_str():

    assert utils.DOCS_URL == "http://www.star.bris.ac.uk/~mbt/stilts/"

    doc_hint = utils.get_docs_hint("tskymatch2")
    assert doc_hint == (
        "check docs?\n    http://www.star.bris.ac.uk/~mbt/stilts/sun256/tskymatch2.html"
    )
