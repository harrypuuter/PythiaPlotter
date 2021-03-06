"""Attaches particles to a NetworkX graph, when NODES represent particles."""


from __future__ import absolute_import
from pythiaplotter.utils.logging_config import get_logger
import networkx as nx


log = get_logger(__name__)


def assign_particles_nodes(node_particles):
    """Attach Particles to a directed graph when NODES represent particles via NodeParticles.

    NodeParticle objects must have their parent_barcodes specified for this to work.

    It automatically attaches directed edges, between parent and child nodes.

    Parameters
    ----------
    node_particles : list[NodeParticle]
        List of NodeParticles, whose Particle's will be attached to a graph
        with the relationship specified by self.parent_barcodes.

    Returns
    -------
    NetworkX.MultiDiGraph
        Directed graph with particles assigned to nodes, and edges to represent relationships.
    """

    gr = nx.MultiDiGraph()

    # assign a node for each Particle obj
    for np in node_particles:
        gr.add_node(np.particle.barcode, particle=np.particle)

    # get the barcode of the system to avoid useless edges
    # and non-existent particles. 0 for Pythia8, -1 for CMSSW, but easiest
    # is to check in the list of nodes (since node barcode = particle barcode)
    system_barcode = -1 if 0 in gr.nodes() else 0

    # assign edges between Parents/Children
    for np in node_particles:
        if np.parent_barcodes:
            if np.parent_barcodes[0] == system_barcode and np.parent_barcodes[-1] == system_barcode:
                continue
            for i in np.parent_barcodes:
                gr.add_edge(i, np.particle.barcode)

    # Set initial_state and final_state flags, based on number of parents
    # (for initial_state) or number of children (for final_state)
    # This should be the only place it is done, otherwise confusing!
    for node, data in list(gr.nodes(data=True)):

        if len(list(gr.predecessors(node))) == 0:
            data['particle'].initial_state = True

        if len(list(gr.successors(node))) == 0:
            data['particle'].final_state = True

    # log.debug("Graph nodes after assigning: %s" % gr.node)

    remove_isolated_nodes(gr)

    return gr


def remove_particle_node(graph, node):
    """Remove a particle node from the graph

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
    node : int
        Node to remove.
    """
    # rewire - ensure all it's parents decay to all it's children
    for child in graph.successors(node):
        for parent in graph.predecessors(node):
            graph.add_edge(parent, child)
    graph.remove_node(node)  # also removes the relevant edges


def remove_isolated_nodes(gr):
    """Remove nodes with no parents and no children.

    Parameters
    ----------
    gr : NetworkX.MultiDiGraph
    """
    nodes = list(gr.nodes())[:]
    for np in nodes:
        if len(list(gr.predecessors(np))) == 0 and len(list(gr.successors(np))) == 0:
            gr.remove_node(np)


def remove_redundant_nodes(graph):
    """Remove redundant particle nodes from a graph.

    i.e. when you have a particles which has 1 parent who has the same PDGID,
    and 1 child (no PDGID requirement).

    e.g.::

        ->-g->-g->-g->-

    These are useful to keep if considering Pythia8 internal workings,
    but otherwise are just confusing and a waste of space.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
        Graph to remove redundant nodes from
    """
    graph_new = graph.copy()  # use copy to avoid modifying the thing we're iterating over
    removed_nodes = []  # need to keep track of things we've removed
    for node, data in list(graph_new.nodes(data=True)):
        if node in removed_nodes:
            continue
        children = list(graph.successors(node))
        parents = list(graph.predecessors(node))
        if len(children) == 1 and len(parents) == 1:
            p = data['particle']
            parent = graph.node[parents[0]]['particle']
            child = graph.node[children[0]]['particle']
            if parent.pdgid == p.pdgid:
                log.debug("Removing (%d) %s", node, data['particle'])
                remove_particle_node(graph, node)
                removed_nodes.append(node)


def remove_nodes_by_pdgid(graph, pdgid, final_state_only=True):
    """Remove particles with pdgid from graph.

    Removes both particle and anti-particle.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
    pdgid : int
        PDGID of particles to remove.
    final_state_only : bool, optional
        Only remove final state particles
    """
    # Do a while loop as editign whilst iterating could lead to issues.
    done_removing = False
    while not done_removing:
        done_removing = True
        for node, node_data in list(graph.nodes(data=True)):
            if ((abs(node_data['particle'].pdgid) == pdgid) and
                ((final_state_only and len(graph.successors(node)) == 0) or
                 not final_state_only)):
                remove_particle_node(graph, node)
                done_removing = False
                break
