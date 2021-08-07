[![codecov](https://codecov.io/gh/aidansedgewick/pystilts/branch/main/graph/badge.svg?token=MZI48732VB)](https://codecov.io/gh/aidansedgewick/pystilts)

# stilts 

Thin python wrapper around Mark Taylor's [STILTS table tools](http://www.star.bris.ac.uk/~mbt/stilts/ "STILTS homepage").

## Install

For now:
1) clone this repo with `git clone https://github.com/aidansedgewick/stilts_wrapper.git`.
2) `cd stilts_wrapper`
3) python3 setup.py install

## Use

The main API is the class `Stilts`.

example

```
>>> from stilts_wrapper import Stilts
>>> st = Stilts(
...    "tskymatch2", in1="Jband.cat.fits", in2="Kband.cat.fits"
...    ra1="ra_Jband", dec1="dec_Jband", ra2="ra_Kband", dec2="dec_Kband",
...    out="output.cat.fits", omode="out", ofmt="out", ifmt1="fits", ifmt2="fit$
... )  
>>>
>>> st.run()
```

There are a couple of convnience methods for less typing. For instance,
if all your tables as fits format (or all csv, or whatever):

```
>>> from stilts_wrapper import Stilts
>>> st = Stilts(
...    "tskymatch2", in1="Jband.cat.fits", in2="Kband.cat.fits"
...    ra1="ra_Jband", dec1="dec_Jband", ra2="ra_Kband", dec2="dec_Kband",
... )
>>> st.format_all_as("fits")
```

