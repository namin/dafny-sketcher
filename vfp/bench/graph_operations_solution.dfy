// Graph operations: path, reachable, cycle detection

type Node = nat

datatype Graph = Graph(nodes: set<Node>, edges: set<(Node, Node)>)

predicate {:spec} validGraph(g: Graph)
{
  forall e :: e in g.edges ==> e.0 in g.nodes && e.1 in g.nodes
}

predicate {:spec} hasEdge(g: Graph, from: Node, to: Node)
  requires validGraph(g)
{
  (from, to) in g.edges
}

function {:spec} neighbors(g: Graph, n: Node): set<Node>
  requires validGraph(g)
  requires n in g.nodes
{
  set m | m in g.nodes && (n, m) in g.edges
}

predicate {:spec} isPath(g: Graph, path: seq<Node>)
  requires validGraph(g)
{
  |path| > 0 &&
  (forall i :: 0 <= i < |path| ==> path[i] in g.nodes) &&
  (forall i :: 0 <= i < |path| - 1 ==> hasEdge(g, path[i], path[i+1]))
}

ghost predicate {:spec} reachable(g: Graph, from: Node, to: Node)
  requires validGraph(g)
  requires from in g.nodes && to in g.nodes
{
  exists path :: isPath(g, path) && |path| >= 1 &&
    path[0] == from && path[|path| - 1] == to
}

ghost predicate {:spec} hasCycle(g: Graph)
  requires validGraph(g)
{
  exists path :: isPath(g, path) && |path| > 1 && path[0] == path[|path| - 1]
}

ghost predicate {:spec} isAcyclic(g: Graph)
  requires validGraph(g)
{
  !hasCycle(g)
}

ghost predicate {:spec} isTree(g: Graph)
  requires validGraph(g)
{
  isAcyclic(g) &&
  |g.edges| == |g.nodes| - 1 &&
  forall n, m :: n in g.nodes && m in g.nodes && n != m ==> reachable(g, n, m)
}

function {:spec} inDegree(g: Graph, n: Node): nat
  requires validGraph(g)
  requires n in g.nodes
{
  |set m | m in g.nodes && (m, n) in g.edges|
}

function {:spec} outDegree(g: Graph, n: Node): nat
  requires validGraph(g)
  requires n in g.nodes
{
  |neighbors(g, n)|
}

ghost predicate {:spec} isConnected(g: Graph)
  requires validGraph(g)
{
  forall n, m :: n in g.nodes && m in g.nodes ==> reachable(g, n, m)
}

// Simplified version without recursion
ghost function {:spec} graphDistance(g: Graph, from: Node, to: Node): nat
  requires validGraph(g)
  requires from in g.nodes && to in g.nodes
  requires reachable(g, from, to)
{
  var path :| isPath(g, path) && |path| >= 1 &&
    path[0] == from && path[|path| - 1] == to;
  |path| - 1
}

lemma SelfReachable(g: Graph, n: Node)
  requires validGraph(g)
  requires n in g.nodes
  ensures reachable(g, n, n)
{
  var path := [n];
  assert |path| == 1;
  assert |path| >= 1;
  assert path[0] == n;
  assert path[|path| - 1] == n;

  // Show isPath
  forall i | 0 <= i < |path|
    ensures path[i] in g.nodes
  {
    assert path[i] == n;
  }

  forall i | 0 <= i < |path| - 1
    ensures hasEdge(g, path[i], path[i+1])
  {
    assert false;  // No such i exists since |path| == 1
  }

  assert isPath(g, path);
}

lemma DirectEdgeReachable(g: Graph, a: Node, b: Node)
  requires validGraph(g)
  requires a in g.nodes && b in g.nodes
  requires hasEdge(g, a, b)
  ensures reachable(g, a, b)
{
  assert b in neighbors(g, a);
  if a == b {
    SelfReachable(g, a);
  } else {
    var path := [a, b];
    assert |path| == 2;
    assert |path| >= 1;
    assert path[0] == a;
    assert path[|path| - 1] == b;

    // Show isPath
    forall i | 0 <= i < |path|
      ensures path[i] in g.nodes
    {
      if i == 0 { assert path[i] == a; }
      else { assert path[i] == b; }
    }

    forall i | 0 <= i < |path| - 1
      ensures hasEdge(g, path[i], path[i+1])
    {
      assert i == 0;
      assert path[i] == a && path[i+1] == b;
    }

    assert isPath(g, path);
  }
}

lemma PathOfLengthTwo(g: Graph, path: seq<Node>)
  requires validGraph(g)
  requires isPath(g, path)
  requires |path| == 2
  ensures path[0] in g.nodes && path[1] in g.nodes
  ensures hasEdge(g, path[0], path[1])
{
  assert 0 <= 0 < |path|;
  assert path[0] in g.nodes;
  assert 0 <= 1 < |path|;
  assert path[1] in g.nodes;
  assert 0 <= 0 < |path| - 1;
  assert hasEdge(g, path[0], path[1]);
}

lemma TreeNoCycle(g: Graph)
  requires validGraph(g)
  requires isTree(g)
  ensures isAcyclic(g)
{
  // By definition of isTree
}

lemma EmptyGraphAcyclic(g: Graph)
  requires validGraph(g)
  requires g.edges == {}
  ensures isAcyclic(g)
{
  if hasCycle(g) {
    var path :| isPath(g, path) && |path| > 1 && path[0] == path[|path| - 1];
    assert |path| >= 2;
    assert hasEdge(g, path[0], path[1]);
    assert (path[0], path[1]) in g.edges;
    assert false;
  }
}

lemma SingleNodeAcyclic(g: Graph)
  requires validGraph(g)
  requires |g.nodes| == 1
  requires g.edges == {}
  ensures isAcyclic(g)
{
  EmptyGraphAcyclic(g);
}

lemma ValidGraphSubgraph(g: Graph, removed: Node)
  requires validGraph(g)
  requires removed in g.nodes
  ensures validGraph(Graph(g.nodes - {removed},
    set e | e in g.edges && e.0 != removed && e.1 != removed))
{
  var g' := Graph(g.nodes - {removed},
    set e | e in g.edges && e.0 != removed && e.1 != removed);
  forall e | e in g'.edges
    ensures e.0 in g'.nodes && e.1 in g'.nodes
  {
    assert e in g.edges;
    assert e.0 != removed && e.1 != removed;
    assert e.0 in g.nodes && e.1 in g.nodes;
    assert e.0 in g'.nodes && e.1 in g'.nodes;
  }
}