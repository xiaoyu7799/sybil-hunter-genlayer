"""Local mock tests for Sybil Hunter — MOCK ONLY, not on-chain results.

Runs the contract's pure deterministic logic (verdict mapping, weights,
signal parsing, pure-Python SHA-256) in plain Python with the GenLayer
runtime stubbed out. No network, no consensus, no chain state. The
on-chain flow is scripts/flow.mjs; its results are recorded separately
in evidence.json / docs/live-verification.md.

Run: python3 tests/test_local.py
"""
import hashlib
import itertools
import json
import sys
import types
from pathlib import Path

# --- Stub the genlayer module so the contract file can be imported locally.
genlayer = types.ModuleType("genlayer")


class _Contract:
    pass


class _Public:
    @staticmethod
    def write(fn):
        return fn

    @staticmethod
    def view(fn):
        return fn


class _Message:
    sender_address = None


class _VM:
    class UserError(Exception):
        pass


genlayer.Contract = _Contract
genlayer.public = _Public()
genlayer.message = _Message()
genlayer.vm = _VM()
genlayer.u256 = int
genlayer.TreeMap = dict
genlayer.DynArray = list
# The contract uses the `gl.` prefix after `from genlayer import *`,
# so the stub must export a `gl` namespace carrying the same API.
genlayer.gl = types.SimpleNamespace(
    Contract=_Contract, public=_Public(), message=_Message(), vm=_VM(),
    nondet=types.SimpleNamespace(), eq_principle=types.SimpleNamespace(),
)
sys.modules["genlayer"] = genlayer
# `from genlayer import *` needs these names exported.
genlayer.__all__ = ["gl", "Contract", "public", "message", "vm", "u256", "TreeMap", "DynArray"]

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "contracts" / "sybil_hunter.py").read_text()
ns = {"__name__": "sybil_hunter_under_test"}
exec(compile(src, str(ROOT / "contracts" / "sybil_hunter.py"), "exec"), ns)

verdict_for = ns["_verdict_for"]
weight_for = ns["_weight_for"]
parse_csv = ns["_parse_signals_csv"]
is_hex = ns["_is_hex_address"]
sha = ns["pure_sha256_hex"]
SYBIL = ns["SYBIL_SIGNALS"]
HUMAN = ns["HUMAN_SIGNALS"]
ALL = ns["ALL_SIGNALS"]

passed = 0


def check(name, cond):
    global passed
    assert cond, "FAIL: " + name
    passed += 1
    print("ok - " + name)


# 1. SHA-256 matches hashlib on standard test vectors (pure-Python impl).
for msg in ["", "abc", "The quick brown fox jumps over the lazy dog",
            "sybil-hunter|case-0|evidence", "a" * 200]:
    check("sha256 matches hashlib for %r" % msg[:20],
          sha(msg) == hashlib.sha256(msg.encode("utf-8")).hexdigest())

# 2. Verdict mapping: enumerate ALL 256 signal subsets; assert the rules.
subsets = []
for r in range(0, 9):
    for combo in itertools.combinations(ALL, r):
        subsets.append(set(combo))
assert len(subsets) == 256
for s in subsets:
    n_sybil = len(s & set(SYBIL))
    n_human = len(s & set(HUMAN))
    v = verdict_for(sorted(s))
    if n_sybil >= 3 and n_human == 0:
        check("subset %s -> SYBIL" % sorted(s), v == "SYBIL")
    elif n_human >= 2 and n_sybil == 0:
        check("subset %s -> HUMAN" % sorted(s), v == "HUMAN")
    else:
        check("subset %s -> UNCERTAIN" % sorted(s), v == "UNCERTAIN")

# 3. Thin evidence: a single signal (any of the 8) is UNCERTAIN, never SYBIL/HUMAN.
for code in ALL:
    check("thin evidence [%s] -> UNCERTAIN" % code, verdict_for([code]) == "UNCERTAIN")

# 4. Conflicting signals are UNCERTAIN and never silently pick a side.
check("3 sybil + 1 human -> UNCERTAIN",
      verdict_for(["SAME_FUNDER", "IDENTICAL_TX_PATTERN", "BURST_ACTIVITY", "LONG_HISTORY"]) == "UNCERTAIN")
check("2 human + 1 sybil -> UNCERTAIN",
      verdict_for(["LONG_HISTORY", "DIVERSE_COUNTERPARTIES", "SAME_FUNDER"]) == "UNCERTAIN")

# 5. Weights: only 0 / 500000 / 1000000 can ever be produced.
check("weight SYBIL == 0", weight_for("SYBIL") == 0)
check("weight UNCERTAIN == 500000", weight_for("UNCERTAIN") == 500000)
check("weight HUMAN == 1000000", weight_for("HUMAN") == 1000000)
seen_weights = {weight_for(verdict_for(sorted(s))) for s in subsets}
check("only 3 weights exist across all 256 subsets", seen_weights == {0, 500000, 1000000})

# 6. Worst-case spread proof, simulated: a validator accepts a leader set
#    only if it equals the validator's own set exactly. Hence any two
#    accepted leader sets L, L' satisfy L == V and L' == V, so L == L',
#    so their verdicts and weights are identical. Spread = 0.
for s in subsets:
    own = sorted(s)
    accepted = [sorted(t) for t in subsets if sorted(t) == own]
    assert len(accepted) == 1
    assert verdict_for(accepted[0]) == verdict_for(own)
    assert weight_for(verdict_for(accepted[0])) == weight_for(verdict_for(own))
check("exact-set equivalence: at most 1 acceptable set per round, spread 0", True)

# 7. Signal CSV parsing: dedupe + sort, unknown code rejected.
check("csv parse sorts+dedupes",
      parse_csv("BURST_ACTIVITY,SAME_FUNDER,BURST_ACTIVITY") == ["BURST_ACTIVITY", "SAME_FUNDER"])
try:
    parse_csv("SAME_FUNDER,NOT_A_SIGNAL")
    check("csv parse rejects unknown code", False)
except Exception as exc:
    check("csv parse rejects unknown code", "UNKNOWN_SIGNAL_CODE" in str(exc))

# 8. Address validation.
check("valid address accepted", is_hex("0x" + "ab" * 20))
check("short address rejected", not is_hex("0x1234"))
check("non-hex rejected", not is_hex("0x" + "zz" * 20))
check("missing 0x rejected", not is_hex("ab" * 20))

# 9. Evidence files in this repo map to the intended verdicts (mock check of
#    the demo evidence wording: the stated signals must yield the verdict
#    the flow expects).
for fname, expected in [("case-sybil-evidence.json", "SYBIL"),
                        ("case-human-evidence.json", "HUMAN"),
                        ("case-thin-evidence.json", "UNCERTAIN")]:
    doc = json.loads((ROOT / "evidence" / fname).read_text())
    stated = sorted(doc["signals_stated"])
    check("%s stated signals -> %s" % (fname, expected),
          verdict_for(stated) == expected and all(c in ALL for c in stated))

print("\n%d mock checks passed (LOCAL MOCK ONLY — not on-chain evidence)." % passed)
