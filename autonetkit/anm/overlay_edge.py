import logging
from functools import total_ordering

import autonetkit.log as log
from autonetkit.log import CustomAdapter
from autonetkit.anm.overlay_interface import OverlayInterface
from autonetkit.anm.overlay_node import OverlayNode


@total_ordering
class OverlayEdge(object):

    """API to access link in network"""

    def __init__(
        self,
        anm,
        overlay_id,
        src_id,
        dst_id,
    ):

# Set using this method to bypass __setattr__

        object.__setattr__(self, 'anm', anm)
        object.__setattr__(self, 'overlay_id', overlay_id)
        object.__setattr__(self, 'src_id', src_id)
        object.__setattr__(self, 'dst_id', dst_id)
        logger = logging.getLogger("ANK")
        logstring = "Interface: %s" % str(self)
        logger = CustomAdapter(logger, {'item': logstring})
        object.__setattr__(self, 'log', logger)

    def __key(self):
        """Note: key doesn't include overlay_id to allow fast cross-layer comparisons"""

        # based on http://stackoverflow.com/q/2909106

        return (self.src_id, self.dst_id)

    def __hash__(self):
        """"""

        return hash(self.__key())

    def __eq__(self, other):
        """"""

        try:
            return (self.src_id, self.dst_id) == (other.src_id,
                                                  other.dst_id)
        except AttributeError:
            return self.node_id == other

    def __repr__(self):
        """String of node"""

        return '%s: (%s, %s)' % (self.overlay_id, self.src, self.dst)

    def __getitem__(self, key):
        """"""

        from autonetkit.anm.overlay_graph import OverlayGraph
        overlay = OverlayGraph(self.anm, key)
        return overlay.edge(self)

    def __lt__(self, other):
        """"""

        return (self.src.node_id, self.dst.node_id) \
            < (other.src.node_id, other.dst.node_id)

    @property
    def src(self):
        """Source node of edge"""

        return OverlayNode(self.anm, self.overlay_id, self.src_id)

    @property
    def dst(self):
        """Destination node of edge"""

        return OverlayNode(self.anm, self.overlay_id, self.dst_id)

    def apply_to_interfaces(self, attribute):
        val = self.__getattr__(attribute)
        self.src_int.__setattr__(attribute, val)
        self.dst_int.__setattr__(attribute, val)

    @property
    def src_int(self):
        """Interface bound to source node of edge"""

        src_int_id = self._interfaces[self.src_id]
        return OverlayInterface(self.anm, self.overlay_id,
                                 self.src_id, src_int_id)

    @property
    def dst_int(self):
        """Interface bound to destination node of edge"""

        dst_int_id = self._interfaces[self.dst_id]
        return OverlayInterface(self.anm, self.overlay_id,
                                 self.dst_id, dst_int_id)

    #TODO: see if these are still used
    def attr_equal(self, *args):
        """Return edges which both src and dst have attributes equal"""

        return all(getattr(self.src, key) == getattr(self.dst, key)
                   for key in args)

    def attr_both(self, *args):
        """Return edges which both src and dst have attributes set"""

        return all(getattr(self.src, key) and getattr(self.dst, key)
                   for key in args)

    def attr_any(self, *args):
        """Return edges which either src and dst have attributes set"""

        return all(getattr(self.src, key) or getattr(self.dst, key)
                   for key in args)

    def dump(self):
        return str(self._graph[self.src_id][self.dst_id])

    def __nonzero__(self):
        """Allows for checking if edge exists
        """

        return self._graph.has_edge(self.src_id, self.dst_id)

    def bind_interface(self, node, interface):
        """Bind this edge to specified index"""

        self._interfaces[node.id] = interface

    def interfaces(self):

        # TODO: warn if interface doesn't exist on node

        return iter(OverlayInterface(self.anm, self.overlay_id,
                    node_id, interface_id) for (node_id,
                    interface_id) in self._interfaces.items())

    @property
    def _graph(self):
        """Return graph the node belongs to"""

        return self.anm.overlay_nx_graphs[self.overlay_id]

    def get(self, key):
        """For consistency, edge.get(key) is neater than getattr(edge, key)"""

        return self.__getattr__(key)

    def set(self, key, val):
        """For consistency, edge.set(key, value) is neater than
        setattr(edge, key, value)"""

        return self.__setattr__(key, val)

    def __getattr__(self, key):
        """Returns edge property"""

        return self._graph[self.src_id][self.dst_id].get(key)

    def __setattr__(self, key, val):
        """Sets edge property"""

        self._graph[self.src_id][self.dst_id][key] = val
