"""
Handle parsing of HepMC files.
"""

import utils.logging_config
import logging
from itertools import izip
from pprint import pprint, pformat
from event_classes import Event, Particle
import edge_grapher
import utils.user_args as user_args
from utils.common import check_file_exists


log = logging.getLogger(__name__)


class HepMCParser(object):
    """Main class to parse a HepMC file.

    User can pass in an event number to return the event with that ID.
    If unassigned, or no events with that event number,
    return first event in file.
    """

    def __init__(self, filename, event_num=0, remove_redundants=True):
        self.filename = filename
        self.event_num = event_num
        self.remove_redundants = remove_redundants
        self.events = []

    def __repr__(self):
        return "%s.%s(filename=%r, event_num=%d, remove_redundants=%s)" % (
            self.__module__,
            self.__class__.__name__,
            self.filename,
            self.event_num,
            self.remove_redundants)

    def __str__(self):
        return "HepMCParser:\n%s" % pformat(self.filename)

    def parse(self):
        """Loop through HepMC file and construct events with particles.

        Returns an Event object, which contains info about the event,
        a list of Particles in the event, and a NetworkX graph obj
        with particles assigned to edges (natural representation of HepMC file).
        """
        events = []
        current_event = None
        current_vertex = None
        particles = []

        log.info("Opening event file %s" % self.filename)
        with open(self.filename) as f:
            for line in f:
                if line.startswith("E") or "END_EVENT_LISTING" in line:
                    # General GenEvent information
                    if current_event:
                        # Do only having read in all particles in an event
                        current_event.particles = particles
                        particles = []
                        events.append(current_event)
                    if line.startswith("E"):
                        current_event = self.parse_event_line(line)
                elif line.startswith("V"):
                    # GenVertex info
                    current_vertex = self.parse_vertex_line(line)
                elif line.startswith("P"):
                    # GenParticle info
                    particle = self.parse_particle_line(line)
                    particle.vtx_out_barcode = current_vertex.barcode

                    # If the particle has vtx_in_barcode = 0,
                    # then this is a 'dangling' vertex (i.e. not in the list
                    # of vertices) and we must create one instead.
                    # Use +(particle.vtx_out_barcode)+particle.barcode for a
                    # unique barcode, since by convention all vertex barcodes
                    # in the file are < 0, and the particle barcode is unique.
                    # This is a final-state particle
                    if particle.vtx_in_barcode == 0:
                        particle.vtx_in_barcode = (abs(particle.vtx_out_barcode) \
                                                   + particle.barcode)
                        particle.final_state = True

                    # If the vtx_in_barcode = vtx_out_barcode, then we have a
                    # cyclical edge. This is normally reserved for an
                    # incoming proton. Need to create a new "out" node, since
                    # other particles will be outgoing from this node
                    if particle.vtx_in_barcode == particle.vtx_out_barcode:
                        particle.vtx_out_barcode = (abs(particle.vtx_out_barcode) \
                                                    + particle.barcode)
                        particle.initial_state = True

                    particles.append(particle)

        # Get the event with the matching barcode, and assign particles to
        # a NetworkX graph in edge representation
        try:
            event = next((x for x in events if x.event_num == self.event_num))
        except StopIteration:
            log.warn("Cannot find an event with event number %d, "
                     "using first event in file instead" % self.event_num)
            event = events[0]

        event.graph = edge_grapher.assign_particles_edges(event.particles,
                                                          self.remove_redundants)
        return event

    @staticmethod
    def map_columns(fields, line):
        """Make dict from fields titles and line

        Field list MUST be in same order as the entries in line.
        """
        parts = line.split()[0:len(fields) + 1]
        return {k: v for k, v in izip(fields, parts)}

    def parse_event_line(self, line):
        """Parse a HepMC GenEvent line"""
        fields = ["event_num", "num_mpi", "scale", "aQCD", "aQED",
                  "signal_process_id", "signal_process_vtx_id", "n_vtx",
                  "beam1_pdgid", "beam2_pdgid"]
        contents = self.map_columns(fields, line[1:])
        return Event(event_num=contents["event_num"],
                     signal_process_vtx_id=contents["signal_process_vtx_id"])

    def parse_vertex_line(self, line):
        """Parse a HepMC GenVertex line"""
        fields = ["barcode", "id", "x", "y", "z", "ctau", "n_orphan_in", "n_out"]
        contents = self.map_columns(fields, line[1:])
        return GenVertex(barcode=contents["barcode"],
                         n_orphan_in=contents["n_orphan_in"])

    def parse_particle_line(self, line):
        """Parse a HepMC GenParticle line"""
        fields = ["barcode", "pdgid", "px", "py", "pz", "energy", "mass",
                  "status", "pol_theta", "pol_phi", "vtx_in_barcode"]
        contents = self.map_columns(fields, line[1:])
        p = Particle(barcode=contents["barcode"], pdgid=contents["pdgid"],
                     px=contents["px"], py=contents["py"], pz=contents["pz"],
                     energy=contents["energy"], mass=contents["mass"],
                     status=contents["status"])
        p.vtx_in_barcode = int(contents["vtx_in_barcode"])
        return p


class GenVertex(object):
    """Helper class to represent a HepMC GenVertex object.

    Only exists inside this parser module since it is only used for parsing
    file and when assigning particles to a NetworkX graph.

    Use a namedtuple instead?
    """

    def __init__(self, barcode, outgoing=None, n_orphan_in=0):
        self.barcode = int(barcode)
        self.outgoing = []
        self.n_orphan_in = n_orphan_in