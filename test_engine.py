# ==========================================
# TEST HARNESS (Run this locally to verify)
# ==========================================

def run_tests():
    print("--- Running Weiwen's Law Causal Engine Tests ---")
    
    # Engine initialize karo (Max 2 mutations allowed per session for testing)
    engine = CausalGuardrailEngine(max_mutations_per_session=2)
    session = CausalSession(session_id="session_001")
    
    # TEST 1: Normal Valid Action
    action1 = ActionUnit(call_id="call_1", intent="WRITE", target="db_users", payload={"name": "Rehan"})
    res1 = engine.decide_core(action1, session)
    if res1 == Decision.PASS:
        session.record_execution(action1) # Record if passed
    print(f"Test 1 (Valid Action): {res1.value} -> Expected: PASS")

    # TEST 2: Signpost 3 (UNDETERMINED via structural absence - empty target)
    action2 = ActionUnit(call_id="call_2", intent="READ", target="", payload={})
    res2 = engine.decide_core(action2, session)
    print(f"Test 2 (Missing Target): {res2.value} -> Expected: UNDETERMINED")

    # TEST 3: Signpost 2 (Nested Call with VALID Parent)
    action3 = ActionUnit(call_id="call_3", intent="READ", target="db_logs", payload={}, parent_id="call_1")
    res3 = engine.decide_core(action3, session)
    print(f"Test 3 (Valid Nested Call): {res3.value} -> Expected: PASS")

    # TEST 4: Signpost 2 (Nested Call with INVALID/Broken Parent)
    action4 = ActionUnit(call_id="call_4", intent="READ", target="db_logs", payload={}, parent_id="ghost_call")
    res4 = engine.decide_core(action4, session)
    print(f"Test 4 (Broken Causal Link): {res4.value} -> Expected: UNDETERMINED")

    # TEST 5: Signpost 1 (Cumulative State Limit Exceeded)
    # Record a second write to hit the limit (limit is 2)
    action5 = ActionUnit(call_id="call_5", intent="WRITE", target="db_orders", payload={"data": "A"})
    engine.decide_core(action5, session)
    session.record_execution(action5) 
    
    # Third write should be blocked
    action6 = ActionUnit(call_id="call_6", intent="WRITE", target="db_orders", payload={"data": "B"})
    res6 = engine.decide_core(action6, session)
    print(f"Test 5 (Cumulative Boundary Exceeded): {res6.value} -> Expected: BLOCK")
    print("------------------------------------------------")

if __name__ == "__main__":
    run_tests()