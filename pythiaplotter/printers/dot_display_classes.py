"""Classes to describe and generate visual attributes for making the Graphviz description.

Also set particle label in here, see ``get_particle_label()``. Or should this be a
method for the particle?
"""


from __future__ import absolute_import
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.pdgid_converter import pdgid_to_string
from pythiaplotter.utils.common import generate_repr_str, check_representation_str


log = get_logger(__name__)


def get_particle_label(particle, representation, label_opts, fancy=True):
    """Return string for particle label to be displayed on graph.

    Parameters
    ----------
    particle : Particle
        Particle under consideration
    representation : {"NODE", "EDGE"}
        Particle representation
    label_opts : dict
        Dict of labels for different representations and fancy/plain
    fancy : bool
        If True, will use HTML/unicode in labels

    Returns
    -------
    str
        Particle label string

    Raises
    ------
    RuntimeError
        If representation is not one of "NODE", "EDGE"
    """
    check_representation_str(representation)
    style_key = "fancy" if fancy else "plain"
    label = label_opts[representation.lower()][style_key].format(**particle.__dict__)
    if fancy:
        label = label.replace("inf", "&#x221e;")
    return label


class DotAttrGenerator(object):
    """Base class for generating particle attr dicts"""

    def __init__(self, particle_opts=None, label_opts=None):
        """Create Graphviz attribute str for an object that may or may not correspond to a Particle.

        Parameters
        ----------
        particle_opts : list[dict]
            List of style option dicts for particles, each with `filter` and `attr` fields.
        label_opts : dict
            Dict of label templates, for node/edge and fancy/plain.
        """
        self.particle_opts = particle_opts
        if self.particle_opts:
            for op in self.particle_opts:
                self.validate_particle_opt(op)
        self.label_opts = label_opts

    def __repr__(self):
        return generate_repr_str(self)

    @staticmethod
    def validate_particle_opt(opt):
        """Validate particle options dict"""
        for key in ['filter', 'attr']:
            if key not in opt:
                raise KeyError("Key '%s' must be in particle options dict" % key)
        for key in ['node', 'edge']:
            if key not in opt['attr']:
                raise KeyError("Key '%s' must be in particle options dict['attr']" % key)

    def gv_str(self, obj, fancy):
        """Create attribute string for obj.

        If "particle" in obj.keys(), will style it as a Particle,
        otherwise will assume it's a non-Particle.

        Parameters
        ----------
        obj : an object
            Object to create string for
        fancy : bool
            Whether to style plain or fancy
        """
        if 'particle' in list(obj.keys()):
            attr = self.get_particle_attr(obj['particle'], fancy)
        else:
            attr = self.get_non_particle_attr(obj, fancy)
        return self.dict_to_gv_str(attr)

    def get_particle_attr(self, particle, fancy):
        """Base method for getting an attribute dict for a particle.

        key:value pairs must be legal graphviz key/values.

        The user should override this method.

        Parameters
        ----------
        particle : Particle
        fancy : bool

        Returns
        -------
        dict
        """
        return {}

    def get_non_particle_attr(self, obj, fancy):
        """Base method for getting an attribute dict for not a particle.

        key:value pairs must be legal graphviz key/values.

        The user should override this method.

        Parameters
        ----------
        obj : object
            The object in question.
        fancy : bool

        Returns
        -------
        dict
        """
        return {}

    def dict_to_gv_str(self, attr_dict):
        """Convert a dict to a graphviz-legal string."""
        if not attr_dict:
            return ""
        attr_list = ['{0}={1}'.format(*it) for it in attr_dict.items()]
        return "[{0}]".format(", ".join(attr_list))


class DotEdgeAttrGenerator(DotAttrGenerator):
    """AttrGenerator specifically for Edges."""

    def __init__(self, particle_opts, label_opts):
        super(DotEdgeAttrGenerator, self).__init__(particle_opts, label_opts)

    def get_particle_attr(self, particle, fancy):
        attr = {"label": get_particle_label(particle, "EDGE", self.label_opts, fancy)}

        for opt in self.particle_opts:
            if opt['filter'](particle):
                attr.update(opt['attr']['edge'])
                break
        return attr

class DotNodeAttrGenerator(DotAttrGenerator):
    """AttrGenerator specifically for Nodes."""

    def __init__(self, particle_opts, label_opts):
        super(DotNodeAttrGenerator, self).__init__(particle_opts, label_opts)

    def __repr__(self):
        return generate_repr_str(self)

    def get_particle_attr(self, particle, fancy):
        attr = {"label": get_particle_label(particle, "NODE", self.label_opts, fancy)}

        for opt in self.particle_opts:
            if opt['filter'](particle):
                attr.update(opt['attr']['node'])
                break
        return attr

    def get_non_particle_attr(self, obj, fancy):
        return {"shape": "point"}


class DotGraphAttrGenerator(DotAttrGenerator):
    """Generate Graphviz string with overall graph options"""

    def __init__(self, attr):
        self.attr = attr

    def gv_str(self):
        """Print graph attributes in dot-friendly format"""
        attr_list = ['{0}={1};'.format(*it) for it in self.attr.items()]
        return "\n".join(attr_list)
