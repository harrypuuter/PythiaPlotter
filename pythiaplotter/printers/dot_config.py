"""Default configuration for dot printer.

Settings for the graph as whole are stored in `DOT_GRAPH_OPTS`.
This stores attribute name: value pairs. See link below for possible options.

Settings for particles are stored in `DOT_PARTICLE_OPTS`, in a variety of
dicts, with fields `filter` and `attr`.

The `filter` field is a lambda, which acts upon each `Particle` in the `Event`.
Therefore you are free to insert any expression to select particles.

The `attr` field stores the dot settings.
There are separate dicts for the node & edge representations of particles.
For each, we store dot attributes as key:value pairs, where keys & values can be any
suitable attribute name & value as described in the GraphViz documentation:
http://www.graphviz.org/doc/info/attrs.html
http://www.graphviz.org/doc/info/colors.html

Note that in the event of several option dicts evaulating True,
only the first matching dict in the list will be used.
"""


from __future__ import absolute_import, division


# Settings for the entire graph
DOT_GRAPH_OPTS = {
    "rankdir": "LR",
    "ranksep": 0.6,
    "nodesep": 0.6,
    "labelloc": "top",
    "labeljust": "left",
    "label": '<<FONT POINT-SIZE="45"><B>Event</B></FONT>>'
}


# Settings for particles.
DOT_PARTICLE_OPTS = [
    # Example for b quarks
    dict(
        filter=lambda p: abs(p.pdgid) == 5,
        attr={
            "node": {
                "style": "filled",
                "color": "red"
            },
            "edge": {
                "color": "red",
                "fontcolor": "red"
            }
        }
    ),
    # Example for muons, taus
    dict(
        filter=lambda p: abs(p.pdgid) in [13, 15],
        attr={
            "node": {
                "style": "filled",
                "color": "purple"
            },
            "edge": {
                "color": "purple",
                "fontcolor": "purple",
                "penwidth": 4
            }
        }
    ),
    # Example for gluons
    dict(
        filter=lambda p: abs(p.pdgid) == 21,
        attr={
            "node": {
                "style": "filled",
                "color": "grey"
            },
            "edge": {
                "color": "grey",
                "fontcolor": "grey"
            }
        }
    ),
    # Example for photons
    dict(
        filter=lambda p: abs(p.pdgid) == 22,
        attr={
            "node": {
                "style": "filled",
                "color": "cadetblue1"
            },
            "edge": {
                "color": "cadetblue1",
                "fontcolor": "cadetblue1"
            }
        }
    ),

    # Default for initial-state particles
    dict(
        filter=lambda p: p.initial_state,
        attr={
            "node": {
                "style": "filled",
                "shape": "circle",
                "color": "green3"
            },
            "edge": {
                "color": "green3",
                "fontcolor": "green3",
                "penwidth": 5
            }
        }
    ),

    # Default for final-state particles
    dict(
        filter=lambda p: p.final_state,
        attr={
            "node": {
                "style": "filled",
                "shape": "box",
                "color": "dodgerblue1"
            },
            "edge": {
                "color": "dodgerblue1",
                "fontcolor": "dodgerblue1"
            }
        }
    ),
    # Default for all particles
    dict(
        filter=lambda p: True,
        attr={
            "node": {},
            "edge": {
                "penwidth": 2
            }
        }
    )
]
