// DPLL SAT Solver
// Inspired by older DPLL work based on Adam's Chlipala textbook exercise: https://github.com/namin/coq-sandbox/blob/master/Dpll.v

// ============ CORE TYPES ============
type Var = nat
datatype Lit = Lit(polarity: bool, variable: Var)
type Clause = seq<Lit>
type Formula = seq<Clause>
type Assignment = Var -> bool
type AList = seq<Lit>

// ============ BASIC PREDICATES ============
predicate satLit(l: Lit, a: Assignment)
{
  a(l.variable) == l.polarity
}

predicate satClause(cl: Clause, a: Assignment)
{
  exists l :: l in cl && satLit(l, a)
}

predicate satFormula(fm: Formula, a: Assignment)
{
  forall cl :: cl in fm ==> satClause(cl, a)
}

// ============ BASIC OPERATIONS ============
function negate(l: Lit): Lit
{
  Lit(!l.polarity, l.variable)
}

function upd(a: Assignment, l: Lit): Assignment
{
  (v: Var) => if v == l.variable then l.polarity else a(v)
}

predicate hasEmptyClause(fm: Formula)
{
  exists cl :: cl in fm && cl == []
}

function interpAList(al: AList): Assignment
{
  if al == [] then (v: Var) => true
  else upd(interpAList(al[1..]), al[0])
}

// ============ FORMULA MANIPULATION (Pure Functions) ============

// Remove literal from clause
function removeFromClause(cl: Clause, l: Lit): Clause
{
  if cl == [] then []
  else if cl[0] == l then removeFromClause(cl[1..], l)
  else [cl[0]] + removeFromClause(cl[1..], l)
}

// Simplify formula by setting literal l to true
function simplifyFormula(fm: Formula, l: Lit): Formula
  decreases |fm|
{
  if fm == [] then []
  else
    var cl := fm[0];
    var rest := fm[1..];
    if l in cl then
      // Clause satisfied - skip it
      simplifyFormula(rest, l)
    else
      // Remove negation of l and keep clause
      var cl' := removeFromClause(cl, negate(l));
      [cl'] + simplifyFormula(rest, l)
}

// Find a unit clause
function findUnitClause(fm: Formula): (Lit, bool)
{
  if fm == [] then 
    (Lit(true, 0), false)
  else if |fm[0]| == 1 then
    (fm[0][0], true)
  else
    findUnitClause(fm[1..])
}

// Choose split variable
function chooseSplit(fm: Formula): Lit
{
  if fm != [] && fm[0] != [] then fm[0][0]
  else Lit(true, 0)
}

// ============ DPLL ALGORITHM ============
datatype SATResult = SAT(assignment: AList) | UNSAT | Timeout

function dpll(fuel: nat, fm: Formula): SATResult
  decreases fuel
{
  if fuel == 0 then
    Timeout
  else if fm == [] then
    SAT([])
  else if hasEmptyClause(fm) then
    UNSAT
  else
    var (unit, hasUnit) := findUnitClause(fm);
    if hasUnit then
      // Unit propagation
      var fm' := simplifyFormula(fm, unit);
      var res := dpll(fuel - 1, fm');
      match res {
        case SAT(al) => SAT([unit] + al)
        case UNSAT => UNSAT
        case Timeout => Timeout
      }
    else
      // Splitting
      var split := chooseSplit(fm);
      var fm_pos := simplifyFormula(fm, split);
      var res_pos := dpll(fuel - 1, fm_pos);
      match res_pos {
        case SAT(al) => SAT([split] + al)
        case UNSAT =>
          var fm_neg := simplifyFormula(fm, negate(split));
          var res_neg := dpll(fuel - 1, fm_neg);
          match res_neg {
            case SAT(al) => SAT([negate(split)] + al)
            case UNSAT => UNSAT
            case Timeout => Timeout
          }
        case Timeout => Timeout
      }
}

// ============ CORRECTNESS LEMMAS (Separate from Functions) ============

// Lemma: removeFromClause preserves all literals except l
lemma RemoveFromClauseCorrect(cl: Clause, l: Lit)
  ensures forall x :: x in removeFromClause(cl, l) ==> x in cl && x != l
  ensures forall x :: x in cl && x != l ==> x in removeFromClause(cl, l)
  ensures l !in removeFromClause(cl, l)
{
  // Proof by induction on cl
}

// Lemma: interpAList properties
lemma InterpAListEmpty()
  ensures interpAList([]) == ((v: Var) => true)
{
}

lemma InterpAListCons(l: Lit, al: AList)
  ensures interpAList([l] + al) == upd(interpAList(al), l)
{
}

// Lemma: Unit clause finding is correct
lemma FindUnitClauseCorrect(fm: Formula)
  ensures var (l, found) := findUnitClause(fm);
          found ==> exists cl :: cl in fm && cl == [l]
  ensures var (l, found) := findUnitClause(fm);
          !found ==> forall cl :: cl in fm ==> |cl| != 1
{
  var (l, found) := findUnitClause(fm);
  if fm == [] {
    assert !found;
  } else if |fm[0]| == 1 {
    assert found;
    assert l == fm[0][0];
    assert fm[0] in fm;
    assert fm[0] == [l];
  } else {
    FindUnitClauseCorrect(fm[1..]);
    var (l', found') := findUnitClause(fm[1..]);
    if found' {
      assert found;
      assert l == l';
      var cl :| cl in fm[1..] && cl == [l'];
      assert cl in fm;
      assert cl == [l];
    } else {
      assert !found;
      assert |fm[0]| != 1;
      forall cl | cl in fm
      ensures |cl| != 1
      {
        if cl == fm[0] {
          assert |cl| != 1;
        } else {
          assert cl in fm[1..];
          assert |cl| != 1;
        }
      }
    }
  }
}

// Lemma: Empty clause means unsatisfiable
lemma EmptyClauseUnsatisfiable(fm: Formula)
  requires hasEmptyClause(fm)
  ensures forall a :: !satFormula(fm, a)
{
  var empty_cl :| empty_cl in fm && empty_cl == [];
  forall a
  ensures !satFormula(fm, a)
  {
    assert !satClause(empty_cl, a);
  }
}

// Lemma: Empty formula is satisfiable
lemma EmptyFormulaSatisfiable()
  ensures satFormula([], (v: Var) => true)
  ensures forall a :: satFormula([], a)
{
}

// ============ MAIN CORRECTNESS THEOREMS ============

// Soundness: If DPLL returns SAT, the formula is satisfiable
lemma DpllSoundness(fuel: nat, fm: Formula)
  ensures dpll(fuel, fm).SAT? ==> 
          satFormula(fm, interpAList(dpll(fuel, fm).assignment))
  decreases fuel
{
  if fuel == 0 {
    assert dpll(fuel, fm) == Timeout;
  } else if fm == [] {
    assert dpll(fuel, fm) == SAT([]);
    EmptyFormulaSatisfiable();
  } else if hasEmptyClause(fm) {
    assert dpll(fuel, fm) == UNSAT;
  } else {
    var (unit, hasUnit) := findUnitClause(fm);
    if hasUnit {
      var fm' := simplifyFormula(fm, unit);
      var res := dpll(fuel - 1, fm');
      DpllSoundness(fuel - 1, fm');
      
      if res.SAT? {
        var al := res.assignment;
        assert dpll(fuel, fm) == SAT([unit] + al);
        // Need to prove: satFormula(fm, interpAList([unit] + al))
        // This requires a lemma about simplifyFormula preserving satisfiability
        SoundnessSimplifyFormula(fm, unit, al);
      }
    } else {
      var split := chooseSplit(fm);
      var fm_pos := simplifyFormula(fm, split);
      var res_pos := dpll(fuel - 1, fm_pos);
      DpllSoundness(fuel - 1, fm_pos);
      
      if res_pos.SAT? {
        var al := res_pos.assignment;
        assert dpll(fuel, fm) == SAT([split] + al);
        SoundnessSimplifyFormula(fm, split, al);
      } else if res_pos.UNSAT? {
        var fm_neg := simplifyFormula(fm, negate(split));
        var res_neg := dpll(fuel - 1, fm_neg);
        DpllSoundness(fuel - 1, fm_neg);
        
        if res_neg.SAT? {
          var al := res_neg.assignment;
          assert dpll(fuel, fm) == SAT([negate(split)] + al);
          SoundnessSimplifyFormula(fm, negate(split), al);
        }
      }
    }
  }
}

// Helper for soundness: simplification preserves satisfiability
lemma SoundnessSimplifyFormula(fm: Formula, l: Lit, al: AList)
  requires satFormula(simplifyFormula(fm, l), interpAList(al))
  ensures satFormula(fm, interpAList([l] + al))
{
  var a := interpAList([l] + al);
  var a' := interpAList(al);
  InterpAListCons(l, al);
  assert a == upd(a', l);
  assert satLit(l, a);
  
  forall cl | cl in fm
  ensures satClause(cl, a)
  {
    if l in cl {
      // Clause is satisfied by l
      assert satClause(cl, a);
    } else {
      // Clause was simplified
      var cl' := removeFromClause(cl, negate(l));
      assert cl' in simplifyFormula(fm, l) by {
        SimplifyFormulaStructure(fm, l, cl, cl');
      }
      assert satClause(cl', a');
      // Need to show satClause(cl, a) from satClause(cl', a')
      ClauseMonotonic(cl, cl', l, a', a);
    }
  }
}

// Helper lemma: structure of simplified formula
lemma SimplifyFormulaStructure(fm: Formula, l: Lit, cl: Clause, cl': Clause)
  requires cl in fm
  requires cl' == removeFromClause(cl, negate(l))
  requires l !in cl
  ensures cl' in simplifyFormula(fm, l)
{
  // By induction on fm structure
}

// Helper lemma: clause satisfaction monotonicity
lemma ClauseMonotonic(cl: Clause, cl': Clause, l: Lit, a': Assignment, a: Assignment)
  requires cl' == removeFromClause(cl, negate(l))
  requires satClause(cl', a')
  requires a == upd(a', l)
  ensures satClause(cl, a)
{
  var wit :| wit in cl' && satLit(wit, a');
  RemoveFromClauseCorrect(cl, negate(l));
  assert wit in cl;
  assert wit != negate(l);
  // wit's satisfaction is preserved in a
  if wit.variable == l.variable {
    assert wit == l;  // Since wit != negate(l)
    assert satLit(wit, a);
  } else {
    assert a(wit.variable) == a'(wit.variable);
    assert satLit(wit, a);
  }
  assert satClause(cl, a);
}

// Helper: When literal is true, simplification preserves satisfiability
lemma SimplifyPreservesSat(fm: Formula, l: Lit, a: Assignment)
  requires satLit(l, a)
  requires satFormula(fm, a)
  ensures satFormula(simplifyFormula(fm, l), a)
  decreases |fm|
{
  if fm == [] {
    assert simplifyFormula(fm, l) == [];
  } else {
    var cl := fm[0];
    var rest := fm[1..];
    
    if l in cl {
      // Clause is satisfied by l, so it's removed from simplified formula
      assert satClause(cl, a);  // Already satisfied
      assert satFormula(rest, a);  // Rest must be satisfied
      SimplifyPreservesSat(rest, l, a);
      assert satFormula(simplifyFormula(rest, l), a);
      assert simplifyFormula(fm, l) == simplifyFormula(rest, l);
    } else {
      // Remove negate(l) from clause
      var cl' := removeFromClause(cl, negate(l));
      assert satClause(cl, a);  // Original clause is satisfied
      
      // Show cl' is also satisfied
      var wit :| wit in cl && satLit(wit, a);
      if wit == negate(l) {
        // Can't happen because satLit(l, a) means !satLit(negate(l), a)
        assert a(l.variable) == l.polarity;
        assert negate(l).variable == l.variable;
        assert negate(l).polarity == !l.polarity;
        assert !satLit(negate(l), a);
        assert false;
      }
      RemoveFromClauseCorrect(cl, negate(l));
      assert wit != negate(l) ==> wit in cl';
      assert wit in cl';
      assert satLit(wit, a);
      assert satClause(cl', a);
      
      assert satFormula(rest, a);
      SimplifyPreservesSat(rest, l, a);
      assert satFormula(simplifyFormula(rest, l), a);
      assert simplifyFormula(fm, l) == [cl'] + simplifyFormula(rest, l);
      assert satFormula(simplifyFormula(fm, l), a);
    }
  }
}

// Completeness: If DPLL returns UNSAT, the formula is unsatisfiable
lemma DpllCompleteness(fuel: nat, fm: Formula)
  ensures dpll(fuel, fm).UNSAT? ==> forall a :: !satFormula(fm, a)
  decreases fuel
{
  if fuel == 0 {
    assert dpll(fuel, fm) == Timeout;
  } else if fm == [] {
    assert dpll(fuel, fm) == SAT([]);
  } else if hasEmptyClause(fm) {
    assert dpll(fuel, fm) == UNSAT;
    EmptyClauseUnsatisfiable(fm);
  } else {
    var (unit, hasUnit) := findUnitClause(fm);
    if hasUnit {
      var fm' := simplifyFormula(fm, unit);
      var res := dpll(fuel - 1, fm');
      DpllCompleteness(fuel - 1, fm');
      
      if res.UNSAT? {
        assert dpll(fuel, fm) == UNSAT;
        // Need to prove: forall a :: !satFormula(fm, a)
        // We know: forall a :: !satFormula(fm', a)
        FindUnitClauseCorrect(fm);
        var unitClause :| unitClause in fm && unitClause == [unit];
        CompletenessUnitPropagation(fm, unit, fm', unitClause);
      }
    } else {
      var split := chooseSplit(fm);
      var fm_pos := simplifyFormula(fm, split);
      var res_pos := dpll(fuel - 1, fm_pos);
      DpllCompleteness(fuel - 1, fm_pos);
      
      if res_pos.UNSAT? {
        var fm_neg := simplifyFormula(fm, negate(split));
        var res_neg := dpll(fuel - 1, fm_neg);
        DpllCompleteness(fuel - 1, fm_neg);
        
        if res_neg.UNSAT? {
          assert dpll(fuel, fm) == UNSAT;
          // Need to prove: forall a :: !satFormula(fm, a)
          // We know: forall a :: !satFormula(fm_pos, a) and forall a :: !satFormula(fm_neg, a)
          CompletenessSplitting(fm, split, fm_pos, fm_neg);
        }
      }
    }
  }
}

// Helper: Unit propagation preserves unsatisfiability
lemma CompletenessUnitPropagation(fm: Formula, unit: Lit, fm': Formula, unitClause: Clause)
  requires unitClause in fm && unitClause == [unit]
  requires fm' == simplifyFormula(fm, unit)
  requires forall a :: !satFormula(fm', a)
  ensures forall a :: !satFormula(fm, a)
{
  forall a
  ensures !satFormula(fm, a)
  {
    if !satLit(unit, a) {
      // Unit clause is not satisfied
      assert !satClause(unitClause, a);
      assert !satFormula(fm, a);
    } else {
      // Unit is satisfied, we need to show fm is still unsatisfiable
      assert satLit(unit, a);
      
      // Use contrapositive: if satFormula(fm, a), then satFormula(fm', a)
      if satFormula(fm, a) {
        // Show that satFormula(fm', a) would hold
        SimplifyPreservesSat(fm, unit, a);
        assert satFormula(fm', a);
        // But this contradicts our requirement that forall a :: !satFormula(fm', a)
        assert false;
      }
      assert !satFormula(fm, a);
    }
  }
}

// Helper lemma for contradiction in splitting
lemma SplittingContradiction(fm: Formula, split: Lit, fm_simplified: Formula, a: Assignment)
  requires fm_simplified == simplifyFormula(fm, split) || fm_simplified == simplifyFormula(fm, negate(split))
  requires satFormula(fm_simplified, a)
  requires forall a' :: !satFormula(fm_simplified, a')
  ensures false
{
  // We have satFormula(fm_simplified, a) 
  // But also forall a' :: !satFormula(fm_simplified, a')
  // Instantiate the forall with a' := a
  assert !satFormula(fm_simplified, a);
  // Contradiction
  assert false;
}

// Helper: Splitting preserves unsatisfiability  
lemma CompletenessSplitting(fm: Formula, split: Lit, fm_pos: Formula, fm_neg: Formula)
  requires fm_pos == simplifyFormula(fm, split)
  requires fm_neg == simplifyFormula(fm, negate(split))
  requires forall a :: !satFormula(fm_pos, a)
  requires forall a :: !satFormula(fm_neg, a)
  ensures forall a :: !satFormula(fm, a)
{
  forall a | true
  ensures !satFormula(fm, a)
  {
    CompletenessSplittingForAssignment(fm, split, fm_pos, fm_neg, a);
  }
}

// Helper: Show unsatisfiability for a specific assignment
lemma CompletenessSplittingForAssignment(fm: Formula, split: Lit, fm_pos: Formula, fm_neg: Formula, a: Assignment)
  requires fm_pos == simplifyFormula(fm, split)
  requires fm_neg == simplifyFormula(fm, negate(split))
  requires forall a :: !satFormula(fm_pos, a)
  requires forall a :: !satFormula(fm_neg, a)
  ensures !satFormula(fm, a)
{
  // Proof by contradiction
  if satFormula(fm, a) {
    // Either split is true or false under a
    if a(split.variable) == split.polarity {
      // split is true under a
      assert satLit(split, a);
      
      // Then fm_pos would be satisfiable
      SimplifyPreservesSat(fm, split, a);
      assert satFormula(fm_pos, a);
      
      // But fm_pos is unsatisfiable for all assignments
      SplittingContradiction(fm, split, fm_pos, a);
      // Reaches false
    } else {
      // negate(split) is true under a
      assert a(split.variable) != split.polarity;
      assert a(split.variable) == !split.polarity;
      
      // Verify negate(split) is satisfied
      assert satLit(negate(split), a) by {
        assert negate(split).variable == split.variable;
        assert negate(split).polarity == !split.polarity;
        assert a(negate(split).variable) == a(split.variable);
        assert a(split.variable) == !split.polarity;
      }
      
      // Then fm_neg would be satisfiable
      SimplifyPreservesSat(fm, negate(split), a);
      assert satFormula(fm_neg, a);
      
      // But fm_neg is unsatisfiable for all assignments
      SplittingContradiction(fm, negate(split), fm_neg, a);
      // Reaches false
    }
  }
}

// Main Correctness Theorem
lemma DpllCorrectness(fuel: nat, fm: Formula)
  ensures dpll(fuel, fm).SAT? ==> 
          satFormula(fm, interpAList(dpll(fuel, fm).assignment))
  ensures dpll(fuel, fm).UNSAT? ==> 
          forall a :: !satFormula(fm, a)
{
  DpllSoundness(fuel, fm);
  DpllCompleteness(fuel, fm);
}

// ============ TESTING ============
method TestCleanDesign()
{
  // Create a simple formula: (p ∨ ¬q) ∧ (¬p ∨ q)
  var p := Lit(true, 0);
  var q := Lit(true, 1);
  var fm := [[p, negate(q)], [negate(p), q]];
  
  // The DPLL function is just a pure computation
  var result := dpll(10, fm);
  
  // Correctness is proven separately in lemmas
  match result {
    case SAT(al) =>
      print "SAT with assignment: ", al, "\n";
      // The soundness lemma guarantees this is correct
      DpllSoundness(10, fm);
      assert satFormula(fm, interpAList(al));
      
    case UNSAT =>
      print "UNSAT\n";
      // The completeness lemma guarantees no solution exists
      DpllCompleteness(10, fm);
      assert forall a :: !satFormula(fm, a);
      
    case Timeout =>
      print "Timeout\n";
  }
  
  // Test an unsatisfiable formula: p ∧ ¬p
  var fm2 := [[p], [negate(p)]];
  var result2 := dpll(10, fm2);
  
  match result2 {
    case SAT(al) =>
      print "ERROR: p ∧ ¬p should be UNSAT\n";
    case UNSAT =>
      print "Correctly identified p ∧ ¬p as UNSAT\n";
    case Timeout =>
      print "Timeout on p ∧ ¬p\n";
  }
}

method Main()
{
  print "DPLL SAT Solver - Clean Design\n";
  print "===============================\n\n";
  TestCleanDesign();
}
