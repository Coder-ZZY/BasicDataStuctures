"""Directed and undirected graph with three interchangeable internal representations.

This module provides :class:`Graph`, a graph implementation that supports
directed and undirected edges, and three internal storage modes selectable at
construction time:

* **OUT_DEGREE** – adjacency list keyed by source node; each entry stores the
  node's out-neighbours (default, most cache-friendly for successor queries).
* **IN_DEGREE**  – adjacency list keyed by destination node; each entry stores
  the node's in-neighbours (optimal for predecessor / topological-sort heavy
  workloads).
* **MATRIX**     – square adjacency matrix with O(1) edge lookup; nodes are
  mapped to contiguous integer indices that are updated on deletion.

All public methods share a unified edge semantic ``u → v`` (directed) or
``u — v`` (undirected) regardless of the active mode.  An existing graph can
be converted to any other mode at any time via :meth:`Graph.to_mode`.

Typical usage::

    from graph import Graph, GraphMode

    # Undirected graph (default)
    g = Graph()
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    assert g.has_edge(1, 0)          # True – edges are symmetric
    print(g.bfs(0))                  # [0, 1, 2]

    # Directed graph
    gd = Graph(directed=True)
    gd.add_edge(0, 1)
    assert not gd.has_edge(1, 0)    # True – edges are one-way
    print(gd.topological_sort())

    # Adjacency-matrix mode
    gm = g.to_mode(GraphMode.MATRIX)
    print(gm.has_edge(0, 1))        # True

Note:
    The module targets Python 3.10+ (``X | Y`` union syntax in annotations).
    For earlier versions add ``from __future__ import annotations`` in the
    consuming module, or replace union types with ``Union[X, Y]`` from
    ``typing``.
"""

from __future__ import annotations

from collections import deque
from enum import Enum, auto
from typing import Optional

# ---------------------------------------------------------------------------
# Public type alias
# ---------------------------------------------------------------------------

#: Type alias for node identifiers accepted by :class:`Graph`.
Node = int | str | float


# ---------------------------------------------------------------------------
# GraphMode
# ---------------------------------------------------------------------------


class GraphMode(Enum):
    """Enumeration of internal storage representations for :class:`Graph`.

    Attributes:
        OUT_DEGREE: Adjacency list where ``adj[v]`` stores all nodes that *v*
            points to (out-neighbours).  Best for forward traversals and
            successor queries.
        IN_DEGREE: Adjacency list where ``adj[v]`` stores all nodes that point
            *to v* (in-neighbours).  Best for backward traversals and
            predecessor queries.
        MATRIX: Square adjacency matrix; ``matrix[i][j] == 1`` indicates an
            edge from node *i* to node *j*.  Offers O(1) edge lookup at the
            cost of O(V²) memory.  For undirected graphs the matrix is always
            symmetric.
    """

    OUT_DEGREE = auto()
    IN_DEGREE = auto()
    MATRIX = auto()


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------


class Graph:
    """A graph with selectable directedness and internal storage representation.

    Edges are stored as ``u → v`` (directed) or ``u — v`` (undirected).
    All public methods expose a consistent interface regardless of the active
    :class:`GraphMode` or the value of *directed*; only time and space
    complexity differ across modes.

    Args:
        mode: Internal storage strategy.  Defaults to
            :attr:`GraphMode.OUT_DEGREE`.
        directed: When ``True`` the graph treats edges as directed (``u → v``
            does **not** imply ``v → u``).  When ``False`` (default) every
            added edge is stored in both directions automatically.

    Attributes:
        mode (GraphMode): The active storage mode.  Read-only after
            construction; use :meth:`to_mode` to obtain a converted copy.
        directed (bool): ``True`` for a directed graph, ``False`` for an
            undirected graph.

    Example::

        # Undirected (default)
        g = Graph()
        g.add_edge("a", "b")
        assert g.has_edge("b", "a")   # True

        # Directed
        gd = Graph(directed=True)
        gd.add_edge("a", "b")
        assert not gd.has_edge("b", "a")
    """

    # ------------------------------------------------------------------
    # Construction & dunder methods
    # ------------------------------------------------------------------

    def __init__(
        self,
        mode: GraphMode = GraphMode.OUT_DEGREE,
        directed: bool = False,
    ) -> None:
        self.mode: GraphMode = mode
        self.directed: bool = directed

        # Adjacency-list storage (IN_DEGREE and OUT_DEGREE modes).
        self._adj: dict[Node, list[Node]] = {}

        # Matrix storage (MATRIX mode).
        # _nodes  : ordered list providing index → node mapping.
        # _index  : reverse mapping node → row/column index.
        # _matrix : V×V adjacency matrix; entry is 1 if edge exists, else 0.
        self._nodes: list[Node] = []
        self._index: dict[Node, int] = {}
        self._matrix: list[list[int]] = []

    def __repr__(self) -> str:
        """Return a human-readable string showing the graph configuration and edge data.

        Returns:
            A multi-line string.  For adjacency-list modes the raw dict is
            shown; for MATRIX mode a formatted grid is rendered.  The header
            line always includes the mode name and directedness.

        Example::

            >>> g = Graph(directed=True)
            >>> g.add_edge(0, 1)
            >>> repr(g)
            "Graph(OUT_DEGREE, directed=True)\\n{0: [1], 1: []}"
        """
        kind = f"{self.mode.name}, directed={self.directed}"
        if self.mode == GraphMode.MATRIX:
            header = "     " + "  ".join(str(n) for n in self._nodes)
            rows = [
                f"{n:>3}| " + "  ".join(str(cell) for cell in self._matrix[i])
                for i, n in enumerate(self._nodes)
            ]
            return f"Graph({kind})\n" + header + "\n" + "\n".join(rows)
        return f"Graph({kind})\n{self._adj!r}"

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def add_node(self, n: Node) -> None:
        """Add an isolated node if it does not already exist.

        Adding a node that is already present is a no-op.

        Args:
            n: The node identifier to add.

        Example::

            g = Graph()
            g.add_node(42)
            assert 42 in g.nodes
        """
        if self.mode == GraphMode.MATRIX:
            self._matrix_add_node(n)
        else:
            if n not in self._adj:
                self._adj[n] = []

    def del_node(self, n: Node) -> None:
        """Remove a node and all edges incident to it.

        Removing a node that does not exist is a no-op.

        Args:
            n: The node identifier to remove.

        Example::

            g = Graph()
            g.add_edge(1, 2)
            g.del_node(1)
            assert 1 not in g.nodes
            assert not g.has_edge(1, 2)
        """
        if self.mode == GraphMode.MATRIX:
            self._matrix_del_node(n)
            return

        if n not in self._adj:
            return
        self._adj.pop(n)
        # Remove all references to n from every other node's neighbour list.
        for neighbours in self._adj.values():
            if n in neighbours:
                neighbours.remove(n)

    @property
    def nodes(self) -> list[Node]:
        """Return a snapshot list of all nodes currently in the graph.

        The returned list is a copy; mutations do not affect the graph.

        Returns:
            A list of node identifiers in insertion order.

        Example::

            g = Graph()
            g.add_edge(0, 1)
            assert set(g.nodes) == {0, 1}
        """
        if self.mode == GraphMode.MATRIX:
            return list(self._nodes)
        return list(self._adj.keys())

    # ------------------------------------------------------------------
    # Edge management
    # ------------------------------------------------------------------

    def add_edge(self, u: Node, v: Node) -> None:
        """Add an edge between ``u`` and ``v``.

        For **directed** graphs a single directed edge ``u → v`` is added.
        For **undirected** graphs both directions are stored automatically so
        that ``has_edge(u, v)`` and ``has_edge(v, u)`` both return ``True``.

        Both endpoints are created automatically if they do not exist.
        Adding a duplicate edge is a no-op (no parallel edges are stored).

        Args:
            u: Source node (directed), or one endpoint (undirected).
            v: Destination node (directed), or the other endpoint (undirected).

        Example::

            g = Graph()                 # undirected
            g.add_edge("x", "y")
            assert g.has_edge("y", "x")

            gd = Graph(directed=True)
            gd.add_edge("x", "y")
            assert not gd.has_edge("y", "x")
        """
        self.add_node(u)
        self.add_node(v)

        if self.mode == GraphMode.MATRIX:
            self._matrix[self._index[u]][self._index[v]] = 1
            if not self.directed:
                self._matrix[self._index[v]][self._index[u]] = 1

        elif self.mode == GraphMode.OUT_DEGREE:
            if v not in self._adj[u]:
                self._adj[u].append(v)
            if not self.directed and u not in self._adj[v]:
                self._adj[v].append(u)

        else:  # IN_DEGREE: adj[v] stores all predecessors of v.
            if u not in self._adj[v]:
                self._adj[v].append(u)
            if not self.directed and v not in self._adj[u]:
                self._adj[u].append(v)

    def del_edge(self, u: Node, v: Node) -> None:
        """Remove the edge between ``u`` and ``v``.

        For **directed** graphs only the edge ``u → v`` is removed.  For
        **undirected** graphs both directions are removed.  Removing an edge
        that does not exist is a no-op; neither endpoint is removed.

        Args:
            u: Source node (directed), or one endpoint (undirected).
            v: Destination node (directed), or the other endpoint (undirected).

        Example::

            g = Graph()
            g.add_edge(1, 2)
            g.del_edge(1, 2)
            assert not g.has_edge(1, 2)
            assert not g.has_edge(2, 1)   # also removed (undirected)
        """
        if self.mode == GraphMode.MATRIX:
            if u in self._index and v in self._index:
                self._matrix[self._index[u]][self._index[v]] = 0
                if not self.directed:
                    self._matrix[self._index[v]][self._index[u]] = 0

        elif self.mode == GraphMode.OUT_DEGREE:
            if u in self._adj and v in self._adj[u]:
                self._adj[u].remove(v)
            if not self.directed and v in self._adj and u in self._adj[v]:
                self._adj[v].remove(u)

        else:  # IN_DEGREE
            if v in self._adj and u in self._adj[v]:
                self._adj[v].remove(u)
            if not self.directed and u in self._adj and v in self._adj[u]:
                self._adj[u].remove(v)

    def has_edge(self, u: Node, v: Node) -> bool:
        """Return ``True`` if an edge from ``u`` to ``v`` exists.

        For **undirected** graphs ``has_edge(u, v)`` and ``has_edge(v, u)``
        always return the same value.

        Args:
            u: Source node (directed), or one endpoint (undirected).
            v: Destination node (directed), or the other endpoint (undirected).

        Returns:
            ``True`` when the edge is present, ``False`` otherwise (including
            when either endpoint is absent from the graph).

        Example::

            gd = Graph(directed=True)
            gd.add_edge(0, 1)
            assert gd.has_edge(0, 1)
            assert not gd.has_edge(1, 0)
        """
        if self.mode == GraphMode.MATRIX:
            if u not in self._index or v not in self._index:
                return False
            return self._matrix[self._index[u]][self._index[v]] == 1

        elif self.mode == GraphMode.OUT_DEGREE:
            return u in self._adj and v in self._adj[u]

        else:  # IN_DEGREE
            return v in self._adj and u in self._adj[v]

    # ------------------------------------------------------------------
    # Neighbour queries
    # ------------------------------------------------------------------

    def successors(self, v: Node) -> list[Node]:
        """Return all nodes reachable from ``v`` via a single edge.

        For **directed** graphs this returns out-neighbours only.  For
        **undirected** graphs all neighbours are returned (direction is
        symmetric).

        Args:
            v: The query node.

        Returns:
            A list of neighbour nodes.  Returns an empty list if ``v`` is
            not in the graph.

        Example::

            g = Graph()
            g.add_edge(0, 1)
            g.add_edge(0, 2)
            assert set(g.successors(0)) == {1, 2}
            assert 0 in g.successors(1)   # True for undirected
        """
        if self.mode == GraphMode.MATRIX:
            if v not in self._index:
                return []
            row = self._matrix[self._index[v]]
            return [self._nodes[j] for j, w in enumerate(row) if w]

        elif self.mode == GraphMode.OUT_DEGREE:
            return list(self._adj.get(v, []))

        else:  # IN_DEGREE: scan all nodes to locate successors of v.
            return [u for u, preds in self._adj.items() if v in preds]

    def predecessors(self, v: Node) -> list[Node]:
        """Return all nodes that have an edge pointing to ``v``.

        For **undirected** graphs this is identical to :meth:`successors`
        because edges are symmetric.  For **directed** graphs only strict
        in-neighbours are returned.

        Args:
            v: The query node.

        Returns:
            A list of predecessor nodes.  Returns an empty list if ``v`` is
            not in the graph.

        Example::

            gd = Graph(directed=True)
            gd.add_edge(1, 3)
            gd.add_edge(2, 3)
            assert set(gd.predecessors(3)) == {1, 2}
        """
        if not self.directed:
            return self.successors(v)

        if self.mode == GraphMode.MATRIX:
            if v not in self._index:
                return []
            j = self._index[v]
            return [self._nodes[i] for i, row in enumerate(self._matrix) if row[j]]

        elif self.mode == GraphMode.OUT_DEGREE:
            return [u for u, succs in self._adj.items() if v in succs]

        else:  # IN_DEGREE
            return list(self._adj.get(v, []))

    def neighbors(self, v: Node) -> list[Node]:
        """Alias for :meth:`successors`.

        For undirected graphs all incident nodes are returned.  For directed
        graphs only out-neighbours are returned.

        Args:
            v: The query node.

        Returns:
            A list of neighbour nodes.
        """
        return self.successors(v)

    # ------------------------------------------------------------------
    # Degree queries
    # ------------------------------------------------------------------

    def in_degree(self, v: Node) -> int:
        """Return the number of edges directed *into* ``v``.

        For **undirected** graphs this equals :meth:`degree` because every
        edge contributes to both endpoints.

        Args:
            v: The query node.

        Returns:
            In-degree of ``v``, or ``0`` if ``v`` is absent from the graph.

        Example::

            gd = Graph(directed=True)
            gd.add_edge(0, 2)
            gd.add_edge(1, 2)
            assert gd.in_degree(2) == 2
        """
        return len(self.predecessors(v))

    def out_degree(self, v: Node) -> int:
        """Return the number of edges directed *out of* ``v``.

        For **undirected** graphs this equals :meth:`degree` because every
        edge contributes to both endpoints.

        Args:
            v: The query node.

        Returns:
            Out-degree of ``v``, or ``0`` if ``v`` is absent from the graph.

        Example::

            gd = Graph(directed=True)
            gd.add_edge(0, 1)
            gd.add_edge(0, 2)
            assert gd.out_degree(0) == 2
        """
        return len(self.successors(v))

    def degree(self, v: Node) -> int:
        """Return the degree of ``v``.

        For **undirected** graphs the degree is the number of incident edges.
        For **directed** graphs this method returns the out-degree; use
        :meth:`in_degree` and :meth:`out_degree` explicitly when both are
        needed.

        Args:
            v: The query node.

        Returns:
            Degree of ``v``, or ``0`` if ``v`` is absent from the graph.

        Example::

            g = Graph()   # undirected
            g.add_edge(0, 1)
            g.add_edge(0, 2)
            assert g.degree(0) == 2
        """
        return self.out_degree(v)

    # ------------------------------------------------------------------
    # Graph traversal
    # ------------------------------------------------------------------

    def dfs(self, start: Node) -> list[Node]:
        """Perform a depth-first search from ``start``.

        For directed graphs traversal follows out-edges only.  For undirected
        graphs all incident edges are explored.  Each reachable node is visited
        exactly once.

        Args:
            start: The node from which traversal begins.

        Returns:
            Nodes in DFS pre-order visit sequence.  Returns an empty list if
            ``start`` is not in the graph.

        Example::

            g = Graph()
            for u, v in [(0, 1), (0, 2), (1, 3)]:
                g.add_edge(u, v)
            assert g.dfs(0) == [0, 1, 3, 2]
        """
        visited: set[Node] = set()
        order: list[Node] = []

        def _visit(v: Node) -> None:
            if v in visited:
                return
            visited.add(v)
            order.append(v)
            for u in self.successors(v):
                _visit(u)

        _visit(start)
        return order

    def bfs(self, start: Node) -> list[Node]:
        """Perform a breadth-first search from ``start``.

        For directed graphs traversal follows out-edges only.  For undirected
        graphs all incident edges are explored.  Each reachable node is visited
        exactly once.

        Args:
            start: The node from which traversal begins.

        Returns:
            Nodes in BFS level-order visit sequence.  Returns an empty list if
            ``start`` is not in the graph.

        Example::

            g = Graph()
            for u, v in [(0, 1), (0, 2), (1, 3)]:
                g.add_edge(u, v)
            assert g.bfs(0) == [0, 1, 2, 3]
        """
        present = self._index if self.mode == GraphMode.MATRIX else self._adj
        if start not in present:
            return []

        visited: set[Node] = {start}
        queue: deque[Node] = deque([start])
        order: list[Node] = []

        while queue:
            v = queue.popleft()
            order.append(v)
            for u in self.successors(v):
                if u not in visited:
                    visited.add(u)
                    queue.append(u)
        return order

    # ------------------------------------------------------------------
    # Topological sort & cycle detection
    # ------------------------------------------------------------------

    def topological_sort(self) -> list[Node]:
        """Return a topological ordering of all nodes using Kahn's algorithm.

        A topological ordering is only defined for directed acyclic graphs
        (DAGs).  Calling this method on an undirected graph always raises
        :exc:`ValueError`.  If the directed graph contains a cycle the method
        returns ``None``.

        Returns:
            A list of nodes in topological order, or ``None`` if the directed
            graph contains at least one cycle.

        Raises:
            ValueError: If called on an undirected graph.

        Example::

            gd = Graph(directed=True)
            for u, v in [(0, 1), (0, 2), (1, 3), (2, 3)]:
                gd.add_edge(u, v)
            order = gd.topological_sort()
            assert order is not None
            assert order.index(0) < order.index(3)
        """
        if not self.directed:
            raise ValueError(
                "topological_sort() is only defined for directed graphs. "
                "Use Graph(directed=True) to create a directed graph."
            )

        in_deg: dict[Node, int] = {n: self.in_degree(n) for n in self.nodes}
        queue: deque[Node] = deque(n for n, d in in_deg.items() if d == 0)
        order: list[Node] = []

        while queue:
            v = queue.popleft()
            order.append(v)
            for u in self.successors(v):
                in_deg[u] -= 1
                if in_deg[u] == 0:
                    queue.append(u)

        return order if len(order) == len(self.nodes) else None

    def has_cycle(self) -> bool:
        """Return ``True`` if the graph contains at least one cycle.

        For **directed** graphs, delegates to :meth:`topological_sort`; a
        failed sort indicates a directed cycle.

        For **undirected** graphs, uses DFS with parent tracking: a back-edge
        to any node other than the immediate parent indicates a cycle.

        Returns:
            ``True`` if a cycle is present, ``False`` for acyclic or empty
            graphs.

        Example::

            gd = Graph(directed=True)
            for u, v in [(0, 1), (1, 2), (2, 0)]:
                gd.add_edge(u, v)
            assert gd.has_cycle()

            g = Graph()   # undirected
            g.add_edge(0, 1)
            g.add_edge(1, 2)
            assert not g.has_cycle()   # path graph, no cycle
            g.add_edge(2, 0)
            assert g.has_cycle()
        """
        if self.directed:
            return self.topological_sort() is None

        # Undirected: DFS with parent tracking.
        visited: set[Node] = set()

        def _dfs(v: Node, parent: Optional[Node]) -> bool:
            visited.add(v)
            for u in self.successors(v):
                if u not in visited:
                    if _dfs(u, v):
                        return True
                elif u != parent:
                    # Back-edge to a non-parent ancestor → cycle.
                    return True
            return False

        for n in self.nodes:
            if n not in visited:
                if _dfs(n, None):
                    return True
        return False

    # ------------------------------------------------------------------
    # Mode conversion & export
    # ------------------------------------------------------------------

    def to_mode(self, new_mode: GraphMode) -> "Graph":
        """Return a new :class:`Graph` equivalent to *self* stored in ``new_mode``.

        The returned graph preserves the same :attr:`directed` setting.
        When ``new_mode`` equals the current mode *self* is returned unchanged
        (no copy is made).

        Args:
            new_mode: The desired :class:`GraphMode` for the returned graph.

        Returns:
            A :class:`Graph` with identical nodes, edges, and directedness
            stored in ``new_mode`` format.

        Example::

            gd = Graph(directed=True)
            gd.add_edge(0, 1)
            gm = gd.to_mode(GraphMode.MATRIX)
            assert gm.has_edge(0, 1)
            assert not gm.has_edge(1, 0)
        """
        if new_mode == self.mode:
            return self

        converted = Graph(new_mode, self.directed)
        # Track edges already added to avoid duplicates for undirected graphs.
        seen_edges: set[tuple[Node, Node]] = set()

        for u in self.nodes:
            converted.add_node(u)
            for v in self.successors(u):
                # For undirected graphs, successors(u) already contains v and
                # successors(v) will later contain u, so deduplicate here.
                canonical = (u, v) if self.directed else tuple(sorted((str(u), str(v))))
                if canonical not in seen_edges:
                    seen_edges.add(canonical)  # type: ignore[arg-type]
                    converted.add_edge(u, v)

        return converted

    def get_matrix(self) -> tuple[list[Node], list[list[int]]]:
        """Return the adjacency matrix representation regardless of current mode.

        The returned data are independent copies; mutations do not affect the
        graph.  For undirected graphs the matrix is always symmetric.

        Returns:
            A tuple ``(nodes, matrix)`` where ``nodes`` is the ordered list of
            node identifiers and ``matrix[i][j] == 1`` indicates an edge from
            ``nodes[i]`` to ``nodes[j]``.

        Example::

            g = Graph()
            g.add_edge(0, 1)
            nodes, mat = g.get_matrix()
            i, j = nodes.index(0), nodes.index(1)
            assert mat[i][j] == mat[j][i] == 1   # symmetric (undirected)
        """
        tmp = self.to_mode(GraphMode.MATRIX)
        return list(tmp._nodes), [row[:] for row in tmp._matrix]

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def get_zero_indegree_node(self) -> Optional[Node]:
        """Return the first node whose in-degree is zero, or ``None``.

        Iterates over :attr:`nodes` in insertion order.  For directed graphs
        this is useful as a seed for topological processing (e.g. Kahn's
        algorithm).  For undirected graphs it returns the first isolated node
        (degree zero), since in-degree equals out-degree.

        Returns:
            The first node with in-degree zero, or ``None`` if every node has
            at least one incoming edge or the graph is empty.

        Example::

            gd = Graph(directed=True)
            gd.add_edge(1, 2)
            assert gd.get_zero_indegree_node() == 1
        """
        for n in self.nodes:
            if self.in_degree(n) == 0:
                return n
        return None

    # ------------------------------------------------------------------
    # Private matrix helpers
    # ------------------------------------------------------------------

    def _matrix_add_node(self, n: Node) -> None:
        """Expand the adjacency matrix to accommodate a new node.

        Appends a zero column to every existing row, then appends a new
        all-zero row.  If ``n`` is already present the method returns
        immediately.

        Args:
            n: Node identifier to register in the matrix.
        """
        if n in self._index:
            return
        idx = len(self._nodes)
        self._nodes.append(n)
        self._index[n] = idx
        for row in self._matrix:
            row.append(0)
        self._matrix.append([0] * len(self._nodes))

    def _matrix_del_node(self, n: Node) -> None:
        """Remove a node's row and column from the adjacency matrix.

        After deletion the indices of nodes that followed ``n`` in insertion
        order are decremented by one so the mapping remains contiguous.  If
        ``n`` is absent the method returns immediately.

        Args:
            n: Node identifier to remove from the matrix.
        """
        if n not in self._index:
            return
        idx = self._index.pop(n)
        self._nodes.pop(idx)
        self._matrix.pop(idx)
        for row in self._matrix:
            row.pop(idx)
        # Shift down the stored index for every node that followed n.
        for node, i in self._index.items():
            if i > idx:
                self._index[node] = i - 1