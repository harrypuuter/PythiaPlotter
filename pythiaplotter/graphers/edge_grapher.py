"""Attaches particles to a NetworkX graph, when EDGES represent particles.

Note about convention:

A particle's "out" node is the one from which it is outgoing. Similarly, its
"in" node is the one into which it is incoming.
e.g. a -->-- b : a is the "out" node, b is the "in" node for this edge.

An "incoming edge" to a node is an edge whose destination node is the node
in question. Similarly, an "outgoing edge" from a node is any edge whose source
is the node in question.
e.g. c ---p->-- d: here p is an incoming edge to node d, whilst it is also an
outgoing edge for node c.
"""


from __future__ import absolute_import
from pythiaplotter.utils.logging_config import get_logger
import networkx as nx


log = get_logger(__name__)


def assign_particles_edges(edge_particles):
    """Attach particles to directed graph edges when EDGES represent particles.

    The graph itself is a networkx MultiDiGraph: a directed graph, that can have
    multiple edges between 2 nodes. We distinguish these via the edge['barcode']
    attribute, where the barcode value = particle barcode. We can use
    MultiDiGraph.edges(data=True) to correctly iterate over *all* edges.

    Additionally marks particles as initial/final state as necessary, based on
    whether they have any parents/children, respectively.

    Parameters
    ----------
    edge_particles: list[EdgeParticle]
        The Particle in each EdgeParticle will be assigned to a graph edge,
        using the vertex information in the EdgeParticle object.

    Returns
    -------
    NetworkX.MultiDiGraph
        Directed graph with particles assigned to edges, and nodes to represent relationships.
    """
    gr = nx.MultiDiGraph(attr=None)  # placeholder attr for later in printer

    # assign an edge for each Particle object, preserving direction
    # note that NetworkX auto adds nodes when edges are added
    for ep in edge_particles:
        gr.add_edge(ep.vtx_out_barcode, ep.vtx_in_barcode,
                    barcode=ep.barcode, particle=ep.particle)
        log.debug("Add edge %s > %s for %s", ep.vtx_out_barcode, ep.vtx_in_barcode, ep.particle)

    # Get in-degree for nodes so we can mark the initial state ones
    # (those with no incoming edges) and their particles
    for node, degree in list(gr.in_degree(gr.nodes())):
        if degree == 0:
            for _, _, edge_data in list(gr.out_edges(node, data=True)):
                edge_data['particle'].initial_state = True

    # Do same for final-state nodes/particles (nodes which have no outgoing edges)
    for node, degree in list(gr.out_degree(gr.nodes())):
        if degree == 0:
            for _, _, edge_data in list(gr.in_edges(node, data=True)):
                edge_data['particle'].final_state = True

    log.debug("Edges after assigning: %s", gr.edges())
    log.debug("Nodes after assigning: %s", gr.nodes())

    return gr


def remove_particle_edge(graph, edge):
    """Remove a particle edge from the graph.

    Rewires the other particles such that the nodes at either end of the edge
    essentially merge together into one:
    - any children of the edge, are now children of the edge's parents
    - any incoming edges into the edge's in node are now
      incoming to the out node (ie where the parents are incoming to)

    Parameters
    ----------
    graph: NetworkX.MultiDiGraph
    edge : (int, int)
        Outgoing node, incoming node
    """
    # rewire: ensure all incoming parents and all outgoing children use same vtx
    out_node, in_node = edge

    parents = graph.predecessors(out_node)
    if (len(parents) == 0 and len(graph.successors(out_node)) == 0):
        graph.remove_node(out_node)
        return

    children = graph.successors(in_node)
    if (len(children) == 0 and len(graph.predecessors(in_node)) == 1):
        graph.remove_node(in_node)
        return

    for child in children:
        these = graph[in_node][child]
        for x in these:  # since Multi DiGraph
            log.debug("Adding %d %d %s", out_node, child, these[x])
            graph.add_edge(out_node, child, **these[x])

    # incoming edges to the in_node
    for out_e, in_e, edge_data in graph.in_edges(in_node, data=True):
        if (out_e, in_e) == (out_node, in_node):
            continue  # ignore the original edge itself!
        log.debug("Adding %d %d %s", out_e, out_node, **edge_data)
        graph.add_edge(out_e, out_node, **edge_data)

    graph.remove_node(in_node)


def remove_redundant_edges(graph):
    """Remove redundant particle edges from a graph.

    A particle is redundant when:
    1) > 0 'child' particles (those outgoing from the particle's incoming node
    - this ensures we don't remove final-state particles)
    2) 1 'parent' particle with same PDGID (incoming into the particle's
    outgoing node - also ensures we don't remove initial-state particles)
    3) 0 'sibling' particles (those outgoing from the particle's outgoing node)
    Note that NetworkX includes an edge as its own sibling, so actually we
    require len(sibling_edges) == 1

    e.g.::

        --q-->-g->-g->-g->--u---->
            |             |
        --q->             --ubar->


    Remove the middle gluon and last gluon, since they add no information.

    These redundants are useful to keep if considering MC internal workings,
    but otherwise are just confusing and a waste of space.

    Since it loops over the list of graph edges, we can only remove one edge in
    a loop, otherwise adding extra/replacement edges ruins the sibling counting
    and doesn't remove redundants. So the method loops through the graph edges
    until there are no more redundant edges.

    Since we are dealing with MultiDiGraph, we have to be careful about siblings
    that actually span the same set of nodes - these shouldn't be removed.

    There is probably a more sensible way to do this, currently brute
    force and slow.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
        Graph to remove redundant nodes from.
    """

    done_removing = False
    while not done_removing:
        done_removing = True
        for out_node, in_node, edge_data in list(graph.edges(data=True)):
            # get all incoming edges to this particle's out node (parents)
            parent_edges = graph.in_edges(out_node, data=True)
            # get all outgoing edges from this particle's out node (siblings)
            sibling_edges = graph.out_edges(out_node)
            # get all outgoing edges from this particle's in node (children)
            child_edges = graph.out_edges(in_node)

            if len(parent_edges) == 1 and len(child_edges) != 0 and len(sibling_edges) == 1:
                parent_out, parent_in, parent_data = parent_edges[0]

                # Do removal if parent PDGID matches
                if parent_data["particle"].pdgid == edge_data["particle"].pdgid:
                    log.debug("Doing edge: %d %d", out_node, in_node)
                    log.debug("Parent edges: %s", parent_edges)
                    log.debug("Child edges: %s", child_edges)

                    done_removing = False

                    log.debug("Removing redundant edge (%d, %d) %s", out_node, in_node, edge_data)
                    remove_particle_edge(graph, (out_node, in_node))

                    break

def remove_edges_by_pdgid(graph, pdgid, final_state_only=True):
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
        for out_vtx, in_vtx, edge_data in list(graph.edges(data=True)):
            if ((abs(edge_data['particle'].pdgid) == pdgid) and
                ((final_state_only and len(graph.successors(in_vtx)) == 0) or
                 not final_state_only)):
                remove_particle_edge(graph, (out_vtx, in_vtx))
                done_removing = False
                break
