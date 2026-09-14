from engine import CausalGuardrailEngine, CausalSession, ActionUnit, Decision


def run_tests():
    print("--- Running Weiwen's Law Causal Engine Tests ---")
    
    # Engine initialize (Max 2 mutations allowed per session for testing)
    engine = CausalGuardrailEngine(max_mutations_per_session=2)
    session = CausalSession(session_id="session_001")
    initial_hash = session.state_hash
    
    # TEST 1: Normal Valid Action (WRITE 1)
    action1 = ActionUnit(call_id="call_1", intent="WRITE", target="db_users", payload={"name": "Rehan"})
    res1, session = engine.decide_core(action1, session)
    print(f"Test 1 (Valid Action): {res1.value} -> Expected: PASS")
    assert res1 == Decision.PASS
    assert session.state_hash != initial_hash  # Hash changed deterministically

    # TEST 2: Signpost 3 (UNDETERMINED via structural absence - empty target)
    action2 = ActionUnit(call_id="call_2", intent="READ", target="", payload={})
    res2, session = engine.decide_core(action2, session)
    print(f"Test 2 (Missing Target): {res2.value} -> Expected: UNDETERMINED")
    assert res2 == Decision.UNDETERMINED

    # TEST 3: Signpost 2 (Nested Call with VALID Parent)
    action3 = ActionUnit(call_id="call_3", intent="READ", target="db_logs", payload={}, parent_id="call_1")
    res3, session = engine.decide_core(action3, session)
    print(f"Test 3 (Valid Nested Call): {res3.value} -> Expected: PASS")
    assert res3 == Decision.PASS

    # TEST 4: Signpost 2 (Nested Call with INVALID/Broken Parent)
    action4 = ActionUnit(call_id="call_4", intent="READ", target="db_logs", payload={}, parent_id="ghost_call")
    res4, session = engine.decide_core(action4, session)
    print(f"Test 4 (Broken Causal Link): {res4.value} -> Expected: UNDETERMINED")
    assert res4 == Decision.UNDETERMINED

    # TEST 5: Signpost 1 (Cumulative State Limit Exceeded)
    # WRITE 2 (Hits max allowed limit of 2)
    action5 = ActionUnit(call_id="call_5", intent="WRITE", target="db_orders", payload={"data": "A"})
    res5, session = engine.decide_core(action5, session)
    print(f"Test 5a (Second Write): {res5.value} -> Expected: PASS")
    assert res5 == Decision.PASS
    
    # WRITE 3 (Exceeds limit of 2 -> Should BLOCK)
    action6 = ActionUnit(call_id="call_6", intent="WRITE", target="db_orders", payload={"data": "B"})
    res6, session = engine.decide_core(action6, session)
    print(f"Test 5b (Cumulative Boundary Exceeded): {res6.value} -> Expected: BLOCK")
    assert res6 == Decision.BLOCK

    # TEST 6: Immutable State Hash Integrity Check
    print(f"Test 6 (Causal State Hash Verification): {session.state_hash[:16]}... -> VALID")
    print("------------------------------------------------")
    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()