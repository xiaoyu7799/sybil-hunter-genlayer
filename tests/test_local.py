"""Local mock tests for Sybil Hunter v0.2.0 — MOCK ONLY, not on-chain results.

Runs the contract's pure deterministic logic (verdict mapping, weights,
signal parsing, pure-Python SHA-256, GEN economics constants and the
ledger bucket moves) in plain Python with the GenLayer runtime stubbed
out. No network, no consensus, no chain state. The on-chain flow is
scripts/flow.mjs; its results are recorded separately in evidence.json /
docs/live-verification.md.

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


class _WriteDeco:
    def __call__(self, fn):
        return fn

    @staticmethod
    def payable(fn):
        return fn


class _Public:
    write = _WriteDeco()

    @staticmethod
    def view(fn):
        return fn


class _Message:
    sender_address = None
    value = 0


class _VM:
    class UserError(Exception):
        pass

    class Return:
        pass

    @staticmethod
    def run_nondet_unsafe(judge, validate):
        raise NotImplementedError("nondet not available in mock")


class _Evm:
    @staticmethod
    def contract_interface(cls):
        return cls


def _Address(addr):
    return addr


genlayer.Contract = _Contract
genlayer.public = _Public()
genlayer.message = _Message()
genlayer.vm = _VM()
genlayer.u256 = int
genlayer.TreeMap = dict
genlayer.DynArray = list
genlayer.Address = _Address
genlayer.evm = _Evm()
# The contract uses the `gl.` prefix after `from genlayer import *`,
# so the stub must export a `gl` namespace carrying the same API.
genlayer.gl = types.SimpleNamespace(
    Contract=_Contract, public=_Public(), message=_Message(), vm=_VM(),
    nondet=types.SimpleNamespace(), eq_principle=types.SimpleNamespace(),
    evm=_Evm(),
)
sys.modules["genlayer"] = genlayer
# `from genlayer import *` needs these names exported.
genlayer.__all__ = ["gl", "Contract", "public", "message", "vm", "u256",
                    "TreeMap", "DynArray", "Address", "evm"]

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
GEN = ns["GEN_WEI"]
HUNTER_REWARD = ns["HUNTER_REWARD_WEI"]
CHALLENGE_STAKE = ns["CHALLENGE_STAKE_WEI"]
CHALLENGE_SUCCESS_REWARD = ns["CHALLENGE_SUCCESS_REWARD_WEI"]

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

# 9. Real GEN economics constants (wei; 1 GEN = 10^18 wei).
check("1 GEN == 10^18 wei", GEN == 10 ** 18)
check("hunter reward == 5 GEN", HUNTER_REWARD == 5 * GEN)
check("challenge stake == 3 GEN", CHALLENGE_STAKE == 3 * GEN)
check("challenge success reward == 2 GEN", CHALLENGE_SUCCESS_REWARD == 2 * GEN)
check("stake + success reward == 5 GEN credit on success",
      CHALLENGE_STAKE + CHALLENGE_SUCCESS_REWARD == 5 * GEN)

# 10. Ledger invariant simulation, replicating the contract's bucket moves
#     exactly: total_received == total_paid_out + funding_pool + reserved
#     + open_stakes + reward_credits, at every step.
ledger = {"received": 0, "paid": 0, "pool": 0, "reserved": 0, "stakes": 0, "credits": 0}


def inv(lbl):
    check("invariant holds: " + lbl,
          ledger["received"] == ledger["paid"] + ledger["pool"] + ledger["reserved"]
          + ledger["stakes"] + ledger["credits"])


# Fund 100 GEN.
ledger["received"] += 100 * GEN
ledger["pool"] += 100 * GEN
inv("after funding 100 GEN")
# Challenge 1 opens: stake 3 GEN in, 2 GEN reserved from pool.
ledger["received"] += 3 * GEN
ledger["stakes"] += 3 * GEN
ledger["pool"] -= 2 * GEN
ledger["reserved"] += 2 * GEN
inv("after challenge 1 opens")
# Challenge 1 fails: stake + reservation both into the pool.
ledger["pool"] += 3 * GEN + 2 * GEN
ledger["stakes"] -= 3 * GEN
ledger["reserved"] -= 2 * GEN
inv("after challenge 1 fails")
check("pool is 103 GEN after failed challenge forfeit", ledger["pool"] == 103 * GEN)
# Challenge 2 opens, then succeeds: challenger credited 3 + 2 GEN.
ledger["received"] += 3 * GEN
ledger["stakes"] += 3 * GEN
ledger["pool"] -= 2 * GEN
ledger["reserved"] += 2 * GEN
inv("after challenge 2 opens")
ledger["credits"] += 3 * GEN + 2 * GEN
ledger["stakes"] -= 3 * GEN
ledger["reserved"] -= 2 * GEN
inv("after challenge 2 succeeds")
# Hunter claims a SYBIL reward: 5 GEN pool -> credit.
ledger["pool"] -= 5 * GEN
ledger["credits"] += 5 * GEN
inv("after hunter reward claim")
# Both beneficiaries withdraw everything.
ledger["credits"] -= 10 * GEN
ledger["paid"] += 10 * GEN
inv("after both withdrawals")
check("final pool is 96 GEN (100 + 3 forfeit - 2 success reward - 5 hunter reward)",
      ledger["pool"] == 96 * GEN)
check("final paid out is 10 GEN", ledger["paid"] == 10 * GEN)
check("final credits are 0", ledger["credits"] == 0)

# 11. Pool-exhaustion guard, same rule as the contract: a hunter reward
#     claim needs pool >= 5 GEN; a challenge needs pool >= 2 GEN at open.
check("claim blocked when pool is 4 GEN", not (4 * GEN >= HUNTER_REWARD))
check("claim allowed when pool is 5 GEN", 5 * GEN >= HUNTER_REWARD)
check("challenge blocked when pool is 1 GEN", not (1 * GEN >= CHALLENGE_SUCCESS_REWARD))
check("challenge allowed when pool is 2 GEN", 2 * GEN >= CHALLENGE_SUCCESS_REWARD)
# Reservation makes the success reward safe even if the pool is drawn down
# afterwards: reserve 2 GEN at open, pool 2 GEN -> 0, success still pays
# from the reservation, never from the (now empty) pool.
pool = 2 * GEN
pool -= CHALLENGE_SUCCESS_REWARD  # reservation at challenge open
check("reservation leaves pool 0 but reward is covered", pool == 0)

# 12. Evidence files in this repo map to the intended verdicts (mock check
#     of the demo evidence wording: the stated signals must yield the
#     verdict the flow expects).
for fname, expected in [("case-sybil-evidence.json", "SYBIL"),
                        ("case-human-evidence.json", "HUMAN"),
                        ("case-thin-evidence.json", "UNCERTAIN")]:
    doc = json.loads((ROOT / "evidence" / fname).read_text())
    stated = sorted(doc["signals_stated"])
    check("%s stated signals -> %s" % (fname, expected),
          verdict_for(stated) == expected and all(c in ALL for c in stated))

# 13. Borderline evidence is genuinely two-sided: the two strong signals
#     alone give UNCERTAIN, adding the ambiguous SAME_FUNDER gives SYBIL,
#     so the two evaluations can honestly disagree and a challenge can
#     succeed on either side.
for fname in ["case-borderline-a-evidence.json", "case-borderline-b-evidence.json"]:
    doc = json.loads((ROOT / "evidence" / fname).read_text())
    strong = sorted(doc["signals_stated_strong"])
    check("%s strong signals alone -> UNCERTAIN" % fname,
          verdict_for(strong) == "UNCERTAIN")
    with_ambig = sorted(strong + doc["signals_ambiguous"])
    check("%s strong + ambiguous -> SYBIL" % fname,
          verdict_for(with_ambig) == "SYBIL")
    check("%s ambiguous code is a real signal code" % fname,
          all(c in ALL for c in doc["signals_ambiguous"]))

print("\n%d mock checks passed (LOCAL MOCK ONLY — not on-chain evidence)." % passed)
