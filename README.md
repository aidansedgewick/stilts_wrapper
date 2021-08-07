[![codecov](https://codecov.io/gh/aidansedgewick/stilts_wrapper/branch/main/graph/badge.svg?token=MZI48732VB)](https://codecov.io/gh/aidansedgewick/stilts_wrapper)

# stilts_wrapper

Thin python wrapper around Mark Taylor's [STILTS table tools](http://www.star.bris.ac.uk/~mbt/stilts/ "STILTS homepage").

Intended mainly for use with the table processing tasks.
(Only tested with these tasks.)

## Install

For now:
1) clone this repo with `git clone https://github.com/aidansedgewick/stilts_wrapper.git`.
2) `cd stilts_wrapper`
3) `python3 setup.py install`

assumes you have STILTS software installed. if not you should just be able
to do `sudo apt-get install stilts` (or equivalent for your package manager).

## Use

The main API is the class `Stilts`.

example

```
>>> from stilts_wrapper import Stilts
>>> st = Stilts(
...    "tskymatch2", in1="Jband.cat.fits", in2="Kband.cat.fits",
...    ra1="ra_Jband", dec1="dec_Jband", ra2="ra_Kband", dec2="dec_Kband",
...    out="output.cat.fits", omode="out", ofmt="out", ifmt1="fits", ifmt2="fits",
... )  
>>>
>>> st.run()
```

Stilts has an attribute `parameters`, so you can see what parameters you've loaded.
If you give an unexpected parameter, it will raise an error:

```
>>> st = Stilts("tskymatch2", bad_parameter=1.0)
StiltsUnknownParameterError()
```

unless you set the flag `strict=False`, ie.
```
>>> st = Stilts("tskymatch2", bad_parameter=1.0, strict=False)
>>> "bad_parameter" in st.parameters
True
```

You'll should still get a warning - but you can silence this too, by also using  `warning=False`.

There are a couple of convnience methods. For instance,
if all your tables as fits format (or all csv, or whatever):

```
>>> from stilts_wrapper import Stilts
>>> st = Stilts(
...    "tskymatch2", in1="Jband.cat.fits", in2="Kband.cat.fits"
...    ra1="ra_Jband", dec1="dec_Jband", ra2="ra_Kband", dec2="dec_Kband",
... )
>>> st.format_all_as("fits")
>>> print(
```

For some of the table processing tasks (currently tskymatch2, tmatch2, tmatch1, tmatchn) there are methods to call directly

```
>>> from stilts_wrapper import Stilts
>>> st = Stilts.tskymatch2(ra1="ra1", all_format="fits")
>>> st.task
"skymatch2"
>>> st.parameters["ofmt"]
fits
>>> "ra1" in st.parameters
True
```

all_format does the same thing as `st.format_all_as()`

You can update any of the parameters with eg. `st.update_parameters(ra1="new_ra")`.

## Gotchas

Some stilts tasks have parameters that are python reserved keywords, for instance `tmatch1` has parameter `in`. But:

```
>>> st = Stilts.tmatch1(in="my_catalog.cat.fits")
SyntaxError
```

To get around this, add a single underscore to the end of the keyword 
(which is removed immediately in processing - it's only as a get around).

```
>>> st = Stilts.tmatch1(in_="my_catalog.cat.fits")
>>> "in" in st.parameters
True
>>> "in_" in st.parameters
False
```


