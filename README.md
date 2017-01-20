# PythiaPlotter

![Supports python 2.7, 3.4, 3.5, 3.6](https://img.shields.io/pypi/pyversions/Django.svg) ![Travis Build Status](https://travis-ci.org/raggleton/PythiaPlotter.svg?branch=proper_restructure)

## What Is It
Plots diagrams of particle decay trees from HEP Monte Carlo (MC) events. Very handy to figure out what is actually going on in your MC!

See examples in [`example`](example) folder, for example [this diagram](example/example_pythia8.pdf).

## What Can I Give It To Plot?

PythiaPlotter currently supports:

- Pythia 8 STDOUT (i.e. the big particle event table) *(e.g. [example/example_pythia8.txt](example/example_pythia8.txt))*
- HepMC files *(e.g. [example/example_hepmc.hepmc](example/example_hepmc.hepmc))*
- LHE files *(e.g. [example/example_lhe.lhe](example/example_lhe.lhe))*
- ParticleListDrawer STDOUT as output by CMSSW *(e.g. [example/example_cmssw.txt](example/example_cmssw.txt))*
- Heppy ROOT files (requires the `GeneratorRelationshipAnalyer` module, see [here]()), *(e.g. [example/example_heppy.root](example_heppy.root))*

## What Do I Need:

- Currently, both python 2.7 and python>=3.4 are supported (although the Heppy
 input is only supported by python 2.7 due to ROOT limitations)
- [`graphviz`](www.graphviz.org) (If the command `which dot` returns a filepath, you will be fine)
- [`PyROOT`](root.cern.ch) if you want to parse Heppy ROOT NTuples. Note that if you are in a virtualenv, 
you will need to enable global site packages. If ROOT cannot be found, then the `--inputFormat HEPPY` options will be disabled. 
- All other required python packages will be installed automatically

## How Do I Get It:

- The easiest way is to use `pip`:

```
pip install git+https://github.com/raggleton/PythiaPlotter.git@proper_restructure
```

- It can also be cloned from Github and installed locally from the base directory:

```
make install
```

## How Do I Use It:

Example usage (requires downloading the example input files in the [example](example) directory)

```
PythiaPlotter example/example_pythia8.txt --open --inputFormat PYTHIA
PythiaPlotter example/example_hepmc.hepmc --open

# to show all options:
PythiaPlotter --help
```

## What Improvements Are Being Working On:

See TODO.md

- Parser: More parsers? Some under-the-hood magic for faster/safer processing
- Printer: JS? TikZ/Latex printer for more formatting and more beautiful output?

## Full documentation:

See