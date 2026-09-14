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
import hashlib
import json
from typing import Dict, Any, Optional, Tuple


# 1. Tri-State Return (Strictly enforced)
class Decision(enum.Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNDETERMINED = "UNDETERMINED"


# 2. Unit of Adjudication (The Tool Call)
class ActionUnit:
    def __init__(self, call_id: str, intent: str, target: str, payload: Optional[Dict[str, Any]] = None, parent_id: Optional[str] = None):
        self.call_id = call_id
        self.intent = intent
        self.target = target
        self.payload = payload or {}
        self.parent_id = parent_id  # Signpost 2: Solves Nested Calls


# 3. Cumulative State Scope & Causal Hash (Signpost 1: Bounded Memory & Anti-Reset)
class CausalSession:
    """
    State lives and dies with the agent's session boundary.
    Employs an immutable causal state hash to prevent session reset exploits.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.executed_calls: Dict[str, ActionUnit] = {}
        self.cumulative_mutations = 0
        # Initialize immutable causal state hash sequence
        self.state_hash = hashlib.sha256(session_id.encode('utf-8')).hexdigest()

    def record_execution(self, action: ActionUnit) -> "CausalSession":
        """Record execution state and compute next immutable state hash."""
        self.executed_calls[action.call_id] = action
        if action.intent == "WRITE":
            self.cumulative_mutations += 1

        # Chain state transition deterministically
        payload_repr = json.dumps(action.payload, sort_keys=True)
        transition = f"{self.state_hash}:{action.call_id}:{action.intent}:{payload_repr}".encode('utf-8')
        self.state_hash = hashlib.sha256(transition).hexdigest()
        return self


class CausalGuardrailEngine:
    def __init__(self, max_mutations_per_session: int = 3):
        self.max_mutations = max_mutations_per_session

    def decide_core(self, action: ActionUnit, session: CausalSession) -> Tuple[Decision, CausalSession]:
        """
        Pure-functional state-coupled adjudication gate.
        Returns a tuple: (Decision, updated_session)
        """
        # SIGNPOST 3: Structural Absence Check (Returns UNDETERMINED without state mutation)
        if not action.call_id or not action.intent or not action.target:
            return Decision.UNDETERMINED, session

        # SIGNPOST 2: Nested Call Causal Link Verification
        if action.parent_id and action.parent_id not in session.executed_calls:
            return Decision.UNDETERMINED, session

        # SIGNPOST 1: Cumulative State Adjudication
        if action.intent == "WRITE" and session.cumulative_mutations >= self.max_mutations:
            return Decision.BLOCK, session

        # Baseline Structural Rule & Payload Bounds Adjudication
        if action.intent == "UNAUTHORIZED_EXEC" or action.payload.get("blocked", False):
            return Decision.BLOCK, session

        # STATE COUPLING FIX: Pass decision explicitly binds state write to engine output
        updated_session = session.record_execution(action)
        return Decision.PASS, updated_session

