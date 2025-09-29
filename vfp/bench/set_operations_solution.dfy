// Set operations: union, intersection, difference, subset

function {:spec} setUnion<T>(s1: set<T>, s2: set<T>): set<T>
{
  s1 + s2
}

function {:spec} setIntersection<T>(s1: set<T>, s2: set<T>): set<T>
{
  s1 * s2
}

function {:spec} setDifference<T>(s1: set<T>, s2: set<T>): set<T>
{
  s1 - s2
}

predicate {:spec} isSubset<T>(s1: set<T>, s2: set<T>)
{
  s1 <= s2
}

predicate {:spec} isProperSubset<T>(s1: set<T>, s2: set<T>)
{
  s1 < s2
}

predicate {:spec} areDisjoint<T>(s1: set<T>, s2: set<T>)
{
  s1 !! s2
}

// Powerset is defined as a ghost function since it's not compilable
// due to the nondeterministic choice of element
ghost function {:spec} powerset<T>(s: set<T>): set<set<T>>
  decreases s
{
  if s == {} then {{}}
  else
    var x :| x in s;
    var rest := s - {x};
    var restPower := powerset(rest);
    restPower + set ps | ps in restPower :: ps + {x}
}

function {:spec} setSize<T>(s: set<T>): nat
{
  |s|
}

predicate {:spec} isEmpty<T>(s: set<T>)
{
  s == {}
}

function {:spec} setSingleton<T>(x: T): set<T>
{
  {x}
}

lemma UnionCommutative<T>(s1: set<T>, s2: set<T>)
  ensures setUnion(s1, s2) == setUnion(s2, s1)
{
  // Dafny proves this automatically
}

lemma UnionAssociative<T>(s1: set<T>, s2: set<T>, s3: set<T>)
  ensures setUnion(setUnion(s1, s2), s3) == setUnion(s1, setUnion(s2, s3))
{
  // Dafny proves this automatically
}

lemma UnionIdentity<T>(s: set<T>)
  ensures setUnion(s, {}) == s
  ensures setUnion({}, s) == s
{
  // Dafny proves this automatically
}

lemma IntersectionCommutative<T>(s1: set<T>, s2: set<T>)
  ensures setIntersection(s1, s2) == setIntersection(s2, s1)
{
  // Dafny proves this automatically
}

lemma IntersectionAssociative<T>(s1: set<T>, s2: set<T>, s3: set<T>)
  ensures setIntersection(setIntersection(s1, s2), s3) == setIntersection(s1, setIntersection(s2, s3))
{
  // Dafny proves this automatically
}

lemma IntersectionDistributive<T>(s1: set<T>, s2: set<T>, s3: set<T>)
  ensures setIntersection(s1, setUnion(s2, s3)) == setUnion(setIntersection(s1, s2), setIntersection(s1, s3))
{
  // Dafny proves this automatically
}

lemma UnionDistributive<T>(s1: set<T>, s2: set<T>, s3: set<T>)
  ensures setUnion(s1, setIntersection(s2, s3)) == setIntersection(setUnion(s1, s2), setUnion(s1, s3))
{
  // Dafny proves this automatically
}

lemma DifferenceProperties<T>(s1: set<T>, s2: set<T>)
  ensures setDifference(s1, s2) <= s1
  ensures areDisjoint(setDifference(s1, s2), s2)
  ensures setUnion(setDifference(s1, s2), setIntersection(s1, s2)) == s1
{
  // Dafny proves this automatically
}

lemma SubsetTransitive<T>(s1: set<T>, s2: set<T>, s3: set<T>)
  requires isSubset(s1, s2) && isSubset(s2, s3)
  ensures isSubset(s1, s3)
{
  // Dafny proves this automatically
}

lemma SubsetAntisymmetric<T>(s1: set<T>, s2: set<T>)
  requires isSubset(s1, s2) && isSubset(s2, s1)
  ensures s1 == s2
{
  // Dafny proves this automatically
}

lemma PowersetEmpty<T>(s: set<T>)
  requires s == {}
  ensures powerset(s) == {{}}
{
  // By definition
}

lemma PowersetSubsetProperty<T>(s: set<T>)
  ensures forall t :: t in powerset(s) ==> t <= s
  decreases s
{
  if s == {} {
    assert powerset(s) == {{}};
  } else {
    var x :| x in s;
    var rest := s - {x};
    PowersetSubsetProperty(rest);
  }
}

function Power(base: nat, exp: nat): nat
{
  if exp == 0 then 1
  else base * Power(base, exp - 1)
}

lemma PowerProduct(base: nat, exp: nat)
  requires exp > 0
  ensures Power(base, exp) == base * Power(base, exp - 1)
{
  // By definition
}

lemma DeMorgan<T>(s1: set<T>, s2: set<T>, universe: set<T>)
  requires s1 <= universe && s2 <= universe
  ensures setDifference(universe, setUnion(s1, s2)) == setIntersection(setDifference(universe, s1), setDifference(universe, s2))
  ensures setDifference(universe, setIntersection(s1, s2)) == setUnion(setDifference(universe, s1), setDifference(universe, s2))
{
  // Dafny proves this automatically
}