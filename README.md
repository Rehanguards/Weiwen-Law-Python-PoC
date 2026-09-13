# Weiwen's Law - Python Causal Guardrail Engine (PoC)

A lightweight, zero-LLM in-process Python implementation of **Weiwen's Law** causal adjudication framework. Engineered for deterministic tool call gating, session-bounded cumulative state tracking, and strict structural fail-closed behavior.

### Architecture & Credits
- **Theoretical Architecture & Discovery:** Shaky77 (Weiwen's Law / KISS's Law)
- **Python Engineering & Implementation:** Rehan | Spatial App Studio

### Key Architectural Boundaries
1. **Session-Bounded Accumulation:** State lives strictly within `CausalSession` execution scope to prevent infinite escalation or amnesia.
2. **Nested Invocation Tracking:** Validates parent-child tool execution chains via explicit `parent_id` structural verification.
3. **Tri-State Determinism:** Enforces `PASS`, `BLOCK`, and `UNDETERMINED` based strictly on structural presence/absence rather than floating confidence scores.

### Running Verification Tests
Zero external dependencies required (Uses Python Standard Library):

```bash
python test_engine.py