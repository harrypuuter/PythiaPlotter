from pythia8_parser import Pythia8Parser
from hepmc_parser import HepMCParser
from lhe_parser import LHEParser
from cmssw_particle_list_parser import CMSSWParticleListParser


"""Store a record of all possible parsers, along with their metainfo."""


class ParserOption(object):
    """Basic class to hold info about a parser and associated fields."""

    def __init__(self, description, parser, file_extension, default_representation):
        self.description = description
        self.parser = parser
        self.file_extension = file_extension
        self.default_representation = default_representation
        if default_representation not in ["NODE", "EDGE"]:
            raise RuntimeError("default_representation must be one of NODE, EDGE")

    def __repr__(self):
        return self.description

    def __str__(self):
        return self.description


parser_opts = {

    "PYTHIA": ParserOption(
        description="For screen output from Pythia 8 piped into file",
        parser=Pythia8Parser,
        file_extension=".txt",
        default_representation="NODE"
    ),

    "HEPMC": ParserOption(
        description="For HEPMC files",
        parser=HepMCParser,
        file_extension=".hepmc",
        default_representation="EDGE"
    ),

    "LHE": ParserOption(
        description="For LHE files",
        parser=LHEParser,
        file_extension=".lhe",
        default_representation="NODE"
    ),

    "CMSSW": ParserOption(
        description="For ParticleListDrawer output from CMSSW piped into file",
        parser=CMSSWParticleListParser,
        file_extension=None,
        default_representation="NODE"
    )

}