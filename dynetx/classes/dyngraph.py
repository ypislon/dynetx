"""Base class for undirected dynamic graphs.

The DynGraph class allows any hashable object as a node.
Of each edge needs be specified the set of timestamps of its presence.

Self-loops are allowed.
"""

import networkx as nx
import copy

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"


class DynGraph(nx.Graph):
    """
    Base class for undirected dynamic graphs.

    A DynGraph stores nodes and timestamped edges.

    DynGraph hold undirected edges.  Self loops are allowed.

    Nodes can be arbitrary (hashable) Python objects with optional
    key/value attributes.

    Parameters
    ----------
    data : input graph
        Data to initialize graph.  If data=None (default) an empty
        graph is created.  The data can be an edge list, or any
        NetworkX graph object.

    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    Examples
    --------
    Create an empty graph structure (a "null graph") with no nodes and
    no edges.

    >>> G = dn.DynGraph()

    G can be grown in several ways.

    **Nodes:**

    Add one node at a time:

    >>> G.add_node(1)

    Add the nodes from any container (a list, dict, set or
    even the lines from a file or the nodes from another graph).

    >>> G.add_nodes_from([2,3])
    >>> G.add_nodes_from(range(100,110))
    >>> H=dn.DynGraph()
    >>> H.add_path([0,1,2,3,4,5,6,7,8,9], t=0)
    >>> G.add_nodes_from(H)

    In addition to strings and integers any hashable Python object
    (except None) can represent a node.

    >>> G.add_node(H)

    **Edges:**

    G can also be grown by adding edges and specifying their timestamp.

    Add one edge,

    >>> G.add_edge(1, 2, t=0)

    a list of edges,

    >>> G.add_edges_from([(3, 2), (1,3)], t=1)

    or a collection of edges,

    >>> G.add_edges_from(H.edges(), t=2)

    If some edges connect nodes not yet in the graph, the nodes
    are added automatically.

    **Attributes:**

    Each graph and node can hold key/value attribute pairs
    in an associated attribute dictionary (the keys must be hashable).
    By default these are empty, but can be added or changed using
    add_edge, add_node or direct manipulation of the attribute
    dictionaries named graph, node and edge respectively.

    >>> G = dn.Graph(day="Friday")
    >>> G.graph
    {'day': 'Friday'}

    Add node attributes using add_node(), add_nodes_from() or G.node

    >>> G.add_node(1, name='Pippo')
    >>> G.add_nodes_from([3], name='Pippo')
    >>> G.node[1]
    {'time': 'Pippo'}
    >>> G.node[1]['room'] = 714
    >>> del G.node[1]['room'] # remove attribute
    >>> G.nodes(data=True)
    [(1, {'name': 'Pippo'}), (3, {'name': 'Pippo'})]

    Warning: adding a node to G.node does not add it to the graph.

    **Shortcuts:**

    Many common graph features allow python syntax to speed reporting.

    >>> 1 in G     # check if node in graph
    True
    >>> [n for n in G if n<3]   # iterate through nodes
    [1, 2]
    >>> len(G)  # number of nodes in graph
    5

    To traverse all edges of a graph use the edges() method.


    >>> G.edges(t=1)
    [(3, 2), (1, 3)]

    **Reporting:**

    Simple graph information is obtained using methods.
    Iterator versions of many reporting methods exist for efficiency.
    Methods exist for reporting nodes(), edges(t=None), neighbors(t=None) and degree(t=None)
    as well as the number of nodes and edges.

    For details on these and other miscellaneous methods, see below.
    """

    def __init__(self, data=None, **attr):
        """Initialize a graph with edges, name, graph attributes.

        Parameters
        ----------
        data : input graph
            Data to initialize graph.  If data=None (default) an empty
            graph is created.  The data can be an edge list, or any
            NetworkX/DyNetx graph object.  If the corresponding optional Python
            packages are installed the data can also be a NumPy matrix
            or 2d ndarray, a SciPy sparse matrix, or a PyGraphviz graph.
        name : string, optional (default='')
            An optional name for the graph.
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        See Also
        --------
        convert

        Examples
        --------
        >>> G = dn.DynGraph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G = dn.DynGraph(name='my graph')
        >>> e = [(1,2),(2,3),(3,4)] # list of edges
        >>> G = dn.DynGraph(e)

        Arbitrary graph attribute pairs (key=value) may be assigned

        >>> G=dn.DynGraph(e, day="Friday")
        >>> G.graph
        {'day': 'Friday'}

        """
        super(self.__class__, self).__init__(data, **attr)
        self.time_to_edge = {}
        self.snapshots = {}

    def nodes_iter(self, t=None, data=False):
        """Return an iterator over the nodes with respect to a given temporal snapshot.

        Parameters
        ----------
        t : snapshot id (default=None).
            If None the iterator returns all the nodes of the flattened graph.
        data : boolean, optional (default=False)
               If False the iterator returns nodes.  If True
               return a two-tuple of node and node data dictionary

        Returns
        -------
        niter : iterator
            An iterator over nodes.  If data=True the iterator gives
            two-tuples containing (node, node data, dictionary)

        Examples
        --------
        >>> G = dn.DynGraph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2], 0)

        >>> [n for n, d in G.nodes_iter(t=0)]
        [0, 1, 2]
        """
        if t is not None:
            return iter([n for n in self.degree(t=t).values() if n > 0])
        return iter(self.node)

    def nodes(self, t=None, data=False):
        """Return a list of the nodes in the graph at a given snapshot.

        Parameters
        ----------
        t : snapshot id (default=None)
            If None the the method returns all the nodes of the flattened graph.
        data : boolean, optional (default=False)
               If False return a list of nodes.  If True return a
               two-tuple of node and node data dictionary

        Returns
        -------
        nlist : list
            A list of nodes.  If data=True a list of two-tuples containing
            (node, node data dictionary).

        Examples
        --------
        >>> G = dn.DynGraph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2], 0)
        >>> G.nodes(t=0)
        [0, 1, 2]
        >>> G.add_edge(1, 4, t=1)
        >>> G.nodes(t=0)
        [0, 1, 2]
        """
        return list(self.nodes_iter(t=t, data=data))

    def edges(self, nbunch=None, t=None, data=False, default=None):
        """Return the list of edges present in a given snapshot.

        Edges are returned as tuples
        in the order (node, neighbor).

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        t : snapshot id (default=None)
            If None the the method returns all the edges of the flattened graph.

        Returns
        --------
        edge_list: list of edge tuples
            Edges that are adjacent to any node in nbunch, or a list
            of all edges if nbunch is not specified.

        See Also
        --------
        edges_iter : return an iterator over the edges

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2], t=0)
        >>> G.add_edge(2,3, t=1)
        >>> G.edges(t=0)
        [(0, 1), (1, 2)]
        >>> G.edges()
        [(0, 1), (1, 2), (2, 3)]
        >>> G.edges([0,3], t=0)
        [(0, 1)]
        """
        return list(self.edges_iter(nbunch, t, data, default))

    def edges_iter(self, nbunch=None, t=None, data=False, default=None):
        """Return an iterator over the edges present in a given snapshot.

        Edges are returned as tuples
        in the order (node, neighbor).

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        t : snapshot id (default=None)
            If None the the method returns an iterator over the edges of the flattened graph.

        Returns
        -------
        edge_iter : iterator
            An iterator of (u,v) tuples of edges.

        See Also
        --------
        edges : return a list of edges

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        For directed graphs this returns the out-edges.

        Examples
        --------
        >>> G = dn.DynGraph()   # or MultiGraph, etc
        >>> G.add_path([0,1,2], 0)
        >>> G.add_edge(2,3,1)
        >>> [e for e in G.edges_iter(t=0)]
        [(0, 1), (1, 2)]
        >>> list(G.edges_iter())
        [(0, 1), (1, 2), (2, 3)]
        """
        seen = {}  # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))

        for n, nbrs in nodes_nbrs:
            for nbr in nbrs:
                if t is not None:
                    if nbr not in seen and t in self.adj[n][nbr]['t']:
                        yield (n, nbr, {"t": [t]})
                else:
                    if nbr not in seen:
                        yield (n, nbr, self.adj[n][nbr])
                seen[n] = 1
        del seen

    def add_edge(self, u, v, t=None, e=None, attr_dict=None, **attr):
        """Add an edge between u and v at time t vanishing (optional) at time e.

        The nodes u and v will be automatically added if they are
        not already in the graph.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        t : appearance snapshot id, mandatory
        e : vanishing snapshot id, optional (default=None)

        See Also
        --------
        add_edges_from : add a collection of edges at time t

        Notes
        -----
        Adding an edge that already exists but with different snapshot id updates the edge data.

        Examples
        --------
        The following all add the edge e=(1,2, 0) to graph G:

        >>> G = dn.DynGraph()
        >>> e = (1,2, 0)
        >>> G.add_edge(1, 2, 0)           # explicit two-node form
        >>> G.add_edge(*e)             # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1,2)], t=0 ) # add edges from iterable container

        Specify the vanishing of the edge

        >>>> G.add_edge(1, 3, t=1, e=10)

        will produce an edge present in snapshots [0, 9]
        """
        if t is None:
            raise nx.NetworkXError(
                "The t argument must be specified.")

        if u not in self.node:
            self.adj[u] = self.adjlist_dict_factory()
            self.node[u] = {}
        if v not in self.node:
            self.adj[v] = self.adjlist_dict_factory()
            self.node[v] = {}

        if type(t) != list:
            t = [t]

        for idt in t:
            if idt not in self.time_to_edge:
                self.time_to_edge[idt] = [(u, v, "+")]
            else:
                self.time_to_edge[idt].append((u, v, "+"))

        if e is not None:
            if e not in self.time_to_edge:
                self.time_to_edge[e] = [(u, v, "-")]
            else:
                self.time_to_edge[e].append((u, v, "-"))

        # add the edge
        datadict = self.adj[u].get(v, self.edge_attr_dict_factory())

        old_t = copy.deepcopy(t)
        if 't' in datadict:
            t.extend(datadict['t'])
            if e is not None:
                t.extend(range(max(t), e))

        if e is not None:
            span = range(max(old_t), e)
            t.extend(span)
            for idt in span:
                if idt not in self.snapshots:
                    self.snapshots[idt] = 1
                else:
                    self.snapshots[idt] += 1
        else:
            for idt in t:
                if idt not in self.snapshots:
                    self.snapshots[idt] = 1
                else:
                    self.snapshots[idt] += 1

        datadict.update({'t': t})
        datadict['t'] = sorted(list(set(t)))

        self.adj[u][v] = datadict
        self.adj[v][u] = datadict

    def add_edges_from(self, ebunch, t=None, attr_dict=None, **attr):
        """Add all the edges in ebunch at time t.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as as 2-tuples (u,v) or
            3-tuples (u,v,d) where d is a dictionary containing edge
            data.
        t : appearance snapshot id, mandatory

        See Also
        --------
        add_edge : add a single edge

        Notes
        -----
        Adding the same edge twice has no effect.

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_edges_from([(0,1),(1,2)], t=0)
        """
        # set up attribute dict
        if t is None:
            raise nx.NetworkXError(
                "The t argument must be a specified.")
        # process ebunch
        for e in ebunch:
            self.add_edge(e[0], e[1], t)

    def remove_edge(self, u, v, t=None):
        """Remove the edge between u and v at time t (if specified).

                Parameters
                ----------
                u, v : nodes
                    Remove the edge between nodes u and v.
                t : snapshot id (default=None)
                    If None the edge will be removed at from all snapshots.

                Raises
                ------
                NetworkXError
                    If there is not an edge between u and v.

                See Also
                --------
                remove_edges_from : remove a collection of edges

                Examples
                --------
                >>> G = dn.DynGraph()
                >>> G.add_path([0,1,2,3], 0)
                >>> G.remove_edge(0,1, t=0)
                """
        try:
            if t is None:
                del self.adj[v][u]

            edge_pres = self.adj[u][v]['t']
            if t in edge_pres:
                edge_pres.remove(t)
            if len(edge_pres) == 0:
                del self.adj[u][v]
                if u != v:  # self-loop needs only one entry removed
                    del self.adj[v][u]
            else:
                self.adj[u][v]['t'] = edge_pres
        except KeyError:
            raise nx.NetworkXError("The edge %s-%s is not in the graph" % (u, v))

    def remove_edges_from(self, ebunch, t=None):
        """Remove all edges specified in ebunch at time t (if specified).

        Parameters
        ----------
        ebunch: list or container of edge tuples
            Each edge given in the list or container will be removed
            from the graph.
        t : snapshot id (default=None)
            If None the edge will be removed at from all snapshots.


        See Also
        --------
        remove_edge : remove a single edge at time t

        Notes
        -----
        Will fail silently if an edge in ebunch is not in the graph.

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> ebunch=[(1,2),(2,3)]
        >>> G.remove_edges_from(ebunch, t=0)
        """
        for e in ebunch:
            self.remove_edge(e[0], e[1], t)

    def number_of_edges(self, u=None, v=None, t=None):
        """Return the number of edges between two nodes at time t.

        Parameters
        ----------
        u, v : nodes, optional (default=all edges)
            If u and v are specified, return the number of edges between
            u and v. Otherwise return the total number of all edges.
        t : snapshot id (default=None)
            If None will be returned the number of edges on the flattened graph.


        Returns
        -------
        nedges : int
            The number of edges in the graph.  If nodes u and v are specified
            return the number of edges between those nodes.

        See Also
        --------
        size

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> G.number_of_edges()
        3
        >>> G.number_of_edges(0,1, t=0)
        1
        >>> G.add_edge(3, 4, t=1)
        >>> G.number_of_edges()
        4
        """
        if t is None:
            if u is None:
                return int(self.size())
            if v in self.adj[u]:
                return 1
            else:
                return 0
        else:
            if u is None:
                return int(self.size(t))
            if v in self.adj[u]:
                if t in self.adj[u][v]:
                    return 1
                else:
                    return 0

    def has_edge(self, u, v, t=None):
        """Return True if the edge (u,v) is in the graph at time t.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        t : snapshot id (default=None)
            If None will be returned the presence of the edge on the flattened graph.


        Returns
        -------
        edge_ind : bool
            True if edge is in the graph, False otherwise.

        Examples
        --------
        Can be called either using two nodes u,v or edge tuple (u,v)

        >>> G = nx.Graph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> G.has_edge(0,1, t=0)
        True
        >>> G.has_edge(0,1, t=1)
        False
        """
        try:
            if t is None:
                return v in self.adj[u]
            else:
                return v in self.adj[u] and t in self.adj[u][v]['t']
        except KeyError:
            return False

    def neighbors(self, n, t=None):
        """Return a list of the nodes connected to the node n at time t.

        Parameters
        ----------
        n : node
           A node in the graph
        t : snapshot id (default=None)
            If None will be returned the neighbors of the node on the flattened graph.


        Returns
        -------
        nlist : list
            A list of nodes that are adjacent to n.

        Raises
        ------
        NetworkXError
            If the node n is not in the graph.

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> G.neighbors(0, t=0)
        [1]
        >>> G.neighbors(0, t=1)
        []
        """
        try:
            if t is None:
                return list(self.adj[n])
            else:
                return [i for i in self.adj[n] if t in self.adj[n][i]['t']]
        except KeyError:
            raise nx.NetworkXError("The node %s is not in the graph." % (n,))

    def neighbors_iter(self, n, t=None):
        """Return an iterator over all neighbors of node n at time t.

        Parameters
        ----------
        n : node
           A node in the graph
        t : snapshot id (default=None)
            If None will be returned an iterator over the neighbors of the node on the flattened graph.

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> [n for n in G.neighbors_iter(0, t=0)]
        [1]
        """
        try:
            if t is None:
                return iter(self.adj[n])
            else:
                return iter([i for i in self.adj[n] if t in self.adj[n][i]['t']])
        except KeyError:
            raise nx.NetworkXError("The node %s is not in the graph." % (n,))

    def degree(self, nbunch=None, t=None):
        """Return the degree of a node or nodes at time t.

        The node degree is the number of edges adjacent to that node.

        Parameters
        ----------
        nbunch : iterable container, optional (default=all nodes)
            A container of nodes.  The container will be iterated
            through once.

        t : snapshot id (default=None)
            If None will be returned the degree of nodes on the flattened graph.


        Returns
        -------
        nd : dictionary, or number
            A dictionary with nodes as keys and degree as values or
            a number if a single node is specified.

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> G.degree(0, t=0)
        1
        >>> G.degree([0,1], t=1)
        {0: 0, 1: 0}
        >>> list(G.degree([0,1], t=0).values())
        [1, 2]
        """
        if nbunch in self:  # return a single node
            return next(self.degree_iter(nbunch, t))[1]
        else:  # return a dict
            return dict(self.degree_iter(nbunch, t))

    def degree_iter(self, nbunch=None, t=None):
        """Return an iterator for (node, degree) at time t.

        The node degree is the number of edges adjacent to the node.

        Parameters
        ----------
        nbunch : iterable container, optional (default=all nodes)
            A container of nodes.  The container will be iterated
            through once.

        t : snapshot id (default=None)
            If None will be returned an iterator over the degree of nodes on the flattened graph.


        Returns
        -------
        nd_iter : an iterator
            The iterator returns two-tuples of (node, degree).

        See Also
        --------
        degree

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> list(G.degree_iter(0, t=0))
        [(0, 1)]
        >>> list(G.degree_iter([0,1], t=0))
        [(0, 1), (1, 2)]
        """
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))

        if t is None:
            for n, nbrs in nodes_nbrs:
                yield (n, len(nbrs) + (n in nbrs))  # return tuple (n,degree)
        else:
            # edge weighted graph - degree is sum of nbr edge weights
            for n, nbrs in nodes_nbrs:
                edges_t = len([v for v, k in nbrs.items() if t in k['t']])
                yield (n, edges_t)

    def size(self, t=None, weight=None):
        """Return the number of edges at time t.

        Parameters
        ----------
        t : snapshot id (default=None)
            If None will be returned the size of the flattened graph.


        Returns
        -------
        nedges : int
            The number of edges or sum of edge weights in the graph.

        See Also
        --------
        number_of_edges

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> G.size(t=0)
        3
        """
        s = sum(self.degree(t=t).values()) / 2
        return int(s)

    def number_of_nodes(self, t=None):
        """Return the number of nodes in the t snpashot of a dynamic graph.

        Parameters
        ----------
        t : snapshot id (default=None)
               If None return the number of nodes in the flattened graph.


        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        See Also
        --------
        order  which is identical

        Examples
        --------
        >>> G = dn.DynGraph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2], t=0)
        >>> G.number_of_nodes(0)
        3
        """
        if t is None:
            return len(self.node)
        else:
            nds = sum([1 for n in self.degree(t=t).values() if n > 0])
            return nds

    def order(self, t=None):
        """Return the number of nodes in the t snpashot of a dynamic graph.

        Parameters
        ----------
        t : snapshot id (default=None)
               If None return the number of nodes in the flattened graph.


        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        See Also
        --------
        number_of_nodes  which is identical

        Examples
        --------
        >>> G = dn.DynGraph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2], t=0)
        >>> G.order(0)
        3
        """
        return self.number_of_nodes(t)

    def has_node(self, n, t=None):
        """Return True if the graph, at time t, contains the node n.

        Parameters
        ----------
        n : node
        t : snapshot id (default None)
                If None return the presence of the node in the flattened graph.

        Examples
        --------
        >>> G = dn.DynGraph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2], t=0)
        >>> G.has_node(0, t=0)
        True

        It is more readable and simpler to use

        >>> 0 in G
        True

        """
        if t is None:
            try:
                return n in self.node
            except TypeError:
                return False
        else:
            return self.degree([n], t).values()[0] > 0

    def add_star(self, nodes, t=None, **attr):
        """Add a star at time t.

        The first node in nodes is the middle of the star.  It is connected
        to all other nodes.

        Parameters
        ----------
        nodes : iterable container
            A container of nodes.
        t : snapshot id (default=None)

        See Also
        --------
        add_path, add_cycle

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_star([0,1,2,3], t=0)
        """
        nlist = list(nodes)
        v = nlist[0]
        edges = ((v, n) for n in nlist[1:])
        self.add_edges_from(edges, t, **attr)

    def add_path(self, nodes, t=None, **attr):
        """Add a path at time t.

        Parameters
        ----------
        nodes : iterable container
            A container of nodes.
        t : snapshot id (default=None)

        See Also
        --------
        add_path, add_cycle

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        """
        nlist = list(nodes)
        edges = zip(nlist[:-1], nlist[1:])
        self.add_edges_from(edges, t, **attr)

    def add_cycle(self, nodes, t=None, **attr):
        """Add a cycle at time t.

        Parameters
        ----------
        nodes : iterable container
            A container of nodes.
        t : snapshot id (default=None)

        See Also
        --------
        add_path, add_cycle

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_cycle([0,1,2,3], t=0)
        """
        nlist = list(nodes)
        edges = zip(nlist, nlist[1:] + [nlist[0]])
        self.add_edges_from(edges, t, **attr)

    def stream_edges(self):
        """Generate a temporal ordered stream of interactions.


        Returns
        -------
        nd_iter : an iterator
            The iterator returns a 4-tuples of (node, node, op, timestamp).

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> G.add_path([3,4,5,6], t=1)
        >>> list(G.stream_edges())
        [(0, 1, '+', 0), (1, 2, '+', 0), (2, 3, '+', 0), (3, 4, '+', 1), (4, 5, '+', 1), (5, 6, '+', 1)]
        """
        timestamps = sorted(self.time_to_edge.keys())
        for t in timestamps:
            for e in self.time_to_edge[t]:
                yield (e[0], e[1], e[2], t)

    def time_slice(self, t_from, t_to=None):
        """Return an iterator for (node, degree) at time t.

            The node degree is the number of edges adjacent to the node.

            Parameters
            ----------

            t_from : snapshot id, mandatory
            t_to : snapshot id, optional (default=None)
                If None t_to will be set equal to t_from

            Returns
            -------
            H : a DynGraph object
                the graph described by interactions in [t_from, t_to]

            Examples
            --------
            >>> G = dn.DynGraph()
            >>> G.add_path([0,1,2,3], t=0)
            >>> G.add_path([0,4,5,6], t=1)
            >>> G.add_path([7,1,2,3], t=2)
            >>> H = G.time_slice(0)
            >>> H.edges()
            [(0, 1), (1, 2), (1, 3)]
            >>> H = G.time_slice(0, 1)
            >>> H.edges()
            [(0, 1), (1, 2), (1, 3), (0, 4), (4, 5), (5, 6)]
        """
        # create new graph and copy subgraph into it
        H = self.__class__()
        if t_to is None:
            t_to = t_from

        # copy node and attribute dictionaries
        for ed in self.edges(data=True):
            ixs, ixe = -1, -1
            e = copy.deepcopy(ed)

            if e[2]['t'][0] > t_from:
                ot_from = e[2]['t'][0]
                ixs = 0
            else:
                ot_from = t_from
            if e[2]['t'][-1] < t_to:
                ot_to = e[2]['t'][-1]
                ixe = len(e[2]['t']) - 1
            else:
                ot_to = t_to

            if ot_from > t_to:
                continue

            if ixs < 0:
                try:
                    ixs = e[2]['t'].index(ot_from)
                except ValueError:
                    continue

            if ixe < 0:
                ixe = ixs
                while e[2]['t'][ixe] < ot_to:
                    ixe += 1

            if ixs == ixe:
                ixe += 1

            attr = e[2]
            attr['t'] = e[2]['t'][ixs:ixe]
            for t in attr['t']:
                H.add_edge(e[0], e[1], t)
        return H

    def temporal_snapshots(self):
        """Return the ordered list of snapshot ids present in the dynamic graph.

            Returns
            -------

            nd : list
                a list of snapshot ids

            Examples
            --------
            >>> G = dn.DynGraph()
            >>> G.add_path([0,1,2,3], t=0)
            >>> G.add_path([0,4,5,6], t=1)
            >>> G.add_path([7,1,2,3], t=2)
            >>> G.temporal_snapshots()
            [0, 1, 2]
        """
        return sorted(self.snapshots.keys())

    def number_of_interactions(self, t=None):
        """Return the number of interactions within snapshot t.

        Parameters
        ----------

        t : snapshot id (default=None)
            If None will be returned total number of interactions across all snapshots

        Returns
        -------

        nd : dictionary, or number
            A dictionary with snapshot ids as keys and interaction count as values or
            a number if a single snapshot id is specified.

        Examples
        --------
        >>> G = dn.DynGraph()
        >>> G.add_path([0,1,2,3], t=0)
        >>> G.add_path([0,4,5,6], t=1)
        >>> G.add_path([7,1,2,3], t=2)
        >>> G.number_of_interactions(t=0)
        3
        >>> G.number_of_interactions()
        {0: 3, 1: 3, 2: 3}
        """
        if t is None:
            return self.snapshots
        else:
            try:
                return self.snapshots[t]
            except KeyError:
                raise KeyError("Snapshot not present.")
