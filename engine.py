"""
Weiwen's Law - Python Causal Guardrail Engine (PoC)
---------------------------------------------------
Engineering & Python Implementation: Rehan | Spatial App Studio
Theoretical Architecture & Reference: Shaky77 (Weiwen's Law / KISS's Law)

This module provides a deterministic, zero-LLM in-process ASGI adjudication 
gate for AI agent tool calls, evaluating strict structural causality, 
nested boundaries, and cumulative state.
"""

import enum
from typing import Dict, Any, Optional

# 1. Tri-State Return (Strictly enforced)
class Decision(enum.Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNDETERMINED = "UNDETERMINED"

# 2. Unit of Adjudication (The Tool Call)
class ActionUnit:
    def __init__(self, call_id: str, intent: str, target: str, payload: Dict[str, Any], parent_id: Optional[str] = None):
        self.call_id = call_id
        self.intent = intent
        self.target = target
        self.payload = payload
        self.parent_id = parent_id  # Signpost 2: Solves Nested Calls

# 3. Cumulative State Scope (Signpost 1: Bounded Memory)
class CausalSession:
    """
    State lives and dies with the agent's session boundary. 
    Prevents infinite escalation or instant amnesia.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.executed_calls: Dict[str, ActionUnit] = {}
        self.cumulative_mutations = 0

    def record_execution(self, action: ActionUnit):
        self.executed_calls[action.call_id] = action
        if action.intent == "WRITE":
            self.cumulative_mutations += 1

class CausalGuardrailEngine:
    def __init__(self, max_mutations_per_session: int = 3):
        self.max_mutations = max_mutations_per_session

    def decide_core(self, action: ActionUnit, session: CausalSession) -> Decision:
        # SIGNPOST 3: UNDETERMINED triggered by structural absence
        if not action.call_id or not action.intent or not action.target:
            return Decision.UNDETERMINED

        # SIGNPOST 2: Nested Call Causal Link Verification
        if action.parent_id:
            if action.parent_id not in session.executed_calls:
                return Decision.UNDETERMINED

        # SIGNPOST 1: Cumulative State Adjudication
        if action.intent == "WRITE":
            if session.cumulative_mutations >= self.max_mutations:
                return Decision.BLOCK

        # Baseline structural rule validation
        if action.intent == "UNAUTHORIZED_EXEC":
            return Decision.BLOCK

        return Decision.PASS

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