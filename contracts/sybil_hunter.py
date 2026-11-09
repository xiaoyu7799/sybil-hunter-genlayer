# v0.2.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

# contracts/sybil_hunter.py
# GenLayer Intelligent Contract: Sybil Hunter — airdrop sybil scoring primitive.
# Target Network: GenLayer Stable Studionet (Chain ID 61999, RPC https://studio.genlayer.com/api)
#
# Real testnet GEN economics (Studionet GEN is free from the faucet, zero
# cash cost; 1 GEN = 10^18 wei). There is no demo ledger and no free
# funds: the reward pool is filled with real GEN by deposit_funding, the
# hunter reward is a real GEN credit, and the challenge stake is real GEN.
#
# What this contract does
# -----------------------
# 1. Anyone funds the reward pool with real GEN: deposit_funding (payable).
#    Hunters submit cases for free: a target address plus a URL pointing
#    at behaviour evidence (an analyst note, explorer-derived behaviour
#    report, or similar prose evidence).
# 2. Anyone except the case hunter triggers an evaluation. The leader and
#    every validator independently fetch the same evidence URL and ask an
#    LLM to map the prose evidence onto a FIXED vocabulary of 8 signal
#    codes (4 sybil codes, 4 human codes). The verdict is then a pure
#    deterministic function of that signal set — there is no continuous
#    score and no tolerance band anywhere:
#      SYBIL     iff at least 3 sybil signals and 0 human signals
#      HUMAN     iff at least 2 human signals and 0 sybil signals
#      UNCERTAIN otherwise (thin evidence, conflicting signals, no signals)
# 3. Equivalence requires EXACT equality of the whole sorted signal set,
#    the verdict, and the SHA-256 of the fetched evidence bytes. A leader
#    output that differs by even one signal code is rejected. Two
#    validator-compatible outputs therefore cannot store different
#    weights: the spread in the stored weight is exactly 0. If the
#    judges disagree, nothing is stored and the case stays EVIDENCE_REVIEW.
# 4. While EVIDENCE_REVIEW (before finalize), anyone except the hunter may
#    challenge with an alternative signal set, staking 3 GEN. A second
#    evaluation then runs and finalizes directly. If the second verdict
#    equals the first, the challenge fails and the 3 GEN stake is
#    forfeited into the funding pool. If it differs, the first pending
#    verdict is kept as a CONTRADICTION witness, the challenger is
#    refunded the 3 GEN stake plus a 2 GEN reward (credited, withdrawable),
#    and the second verdict is finalized. A finalized verdict is never
#    changed.
# 5. Finalizing writes the airdrop weight: SYBIL -> 0, UNCERTAIN -> 500000
#    (0.5 scaled by 1,000,000), HUMAN -> 1000000 (1.0). No other weight
#    can ever be stored. A hunter whose case finalizes as SYBIL may claim
#    a fixed 5 GEN reward credit from the funding pool (once per case),
#    then withdraw it to their own address with withdraw_reward.
#    HUMAN and UNCERTAIN cases close with no reward.
# 6. All GEN movement is pull-payment: finalization only records a credit
#    (wei integer); the beneficiary withdraws it themselves with
#    withdraw_reward, which zeroes the credit before transferring. The
#    ledger invariant is:
#      total_received == total_paid_out + funding_pool + challenge_reserved
#                         + open_stakes + reward_credits
#    and the contract balance equals total_received - total_paid_out.
# 7. Case lifecycle: OPEN -> EVIDENCE_REVIEW -> VERDICT_SYBIL /
#    VERDICT_HUMAN / VERDICT_UNCERTAIN -> REWARD_PAID / CLOSED_NO_REWARD.
#    Hunter evolution is tracked as cases_submitted / sybil_finalized /
#    rewards_earned (wei), plus challenge wins and losses.

import json

from genlayer import *

# =============================================================================
# PURE-PYTHON SHA-256 (no dependency on unverified stdlib hashlib in GenVM)
# =============================================================================
_K256 = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]


def _rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def pure_sha256_hex(msg_str: str) -> str:
    data = bytearray(msg_str.encode("utf-8"))
    bit_len = len(data) * 8
    data.append(0x80)
    while (len(data) % 64) != 56:
        data.append(0x00)
    for i in range(7, -1, -1):
        data.append((bit_len >> (i * 8)) & 0xFF)
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    for offset in range(0, len(data), 64):
        w = [0] * 64
        for i in range(16):
            j = offset + i * 4
            w[i] = (data[j] << 24) | (data[j + 1] << 16) | (data[j + 2] << 8) | data[j + 3]
        for i in range(16, 64):
            s0 = _rotr(w[i - 15], 7) ^ _rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = _rotr(w[i - 2], 17) ^ _rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF
        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            S1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            ch = (e & f) ^ ((~e & 0xFFFFFFFF) & g)
            temp1 = (hh + S1 + ch + _K256[i] + w[i]) & 0xFFFFFFFF
            S0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF
            hh, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xFFFFFFFF, c, b, a, (temp1 + temp2) & 0xFFFFFFFF
        h = [(h[idx] + val) & 0xFFFFFFFF for idx, val in enumerate([a, b, c, d, e, f, g, hh])]
    hex_chars = "0123456789abcdef"
    out = []
    for word in h:
        for shift in (28, 24, 20, 16, 12, 8, 4, 0):
            out.append(hex_chars[(word >> shift) & 0xF])
    return "".join(out)


# =============================================================================
# SIGNAL VOCABULARY, VERDICT RULES, WEIGHTS (all exact integers, no float)
# =============================================================================
SYBIL_SIGNALS = ("SAME_FUNDER", "IDENTICAL_TX_PATTERN", "BURST_ACTIVITY", "FRESH_NO_HISTORY")
HUMAN_SIGNALS = ("LONG_HISTORY", "DIVERSE_COUNTERPARTIES", "UNIQUE_BEHAVIOUR", "VERIFIED_ACTIVITY")
ALL_SIGNALS = SYBIL_SIGNALS + HUMAN_SIGNALS

WEIGHT_SYBIL = 0
WEIGHT_UNCERTAIN = 500000
WEIGHT_HUMAN = 1000000
WEIGHT_SCALE = 1000000

# Real GEN economics, in wei (1 GEN = 10^18 wei).
GEN_WEI = 10 ** 18
HUNTER_REWARD_WEI = 5 * GEN_WEI
CHALLENGE_STAKE_WEI = 3 * GEN_WEI
CHALLENGE_SUCCESS_REWARD_WEI = 2 * GEN_WEI


def _verdict_for(signals) -> str:
    sybil_count = 0
    human_count = 0
    for code in signals:
        if code in SYBIL_SIGNALS:
            sybil_count += 1
        elif code in HUMAN_SIGNALS:
            human_count += 1
    if sybil_count >= 3 and human_count == 0:
        return "SYBIL"
    if human_count >= 2 and sybil_count == 0:
        return "HUMAN"
    return "UNCERTAIN"


def _weight_for(verdict: str) -> int:
    if verdict == "SYBIL":
        return WEIGHT_SYBIL
    if verdict == "HUMAN":
        return WEIGHT_HUMAN
    return WEIGHT_UNCERTAIN


def _is_hex_address(addr: str) -> bool:
    if len(addr) != 42:
        return False
    if addr[0] != "0" or addr[1] != "x":
        return False
    for ch in addr[2:]:
        ok = (ch >= "0" and ch <= "9") or (ch >= "a" and ch <= "f") or (ch >= "A" and ch <= "F")
        if not ok:
            return False
    return True


def _parse_signals_csv(csv: str):
    raw = [part.strip() for part in csv.split(",")]
    out = []
    for code in raw:
        if code == "":
            continue
        if code not in ALL_SIGNALS:
            raise Exception("UNKNOWN_SIGNAL_CODE:" + code)
        if code not in out:
            out.append(code)
    out.sort()
    return out


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


class SybilHunter(gl.Contract):
    state_json: str

    def __init__(self):
        state = {
            "next_case_id": 0,
            "funding_pool_wei": 0,
            "total_received_wei": 0,
            "total_paid_out_wei": 0,
            "hunter_reward_wei": HUNTER_REWARD_WEI,
            "challenge_stake_wei": CHALLENGE_STAKE_WEI,
            "challenge_success_reward_wei": CHALLENGE_SUCCESS_REWARD_WEI,
            "cases": {},
            "case_order": [],
            "weights": {},
            "reward_credits": {},
            "hunter_stats": {},
        }
        self.state_json = json.dumps(state)

    # -- deterministic helpers --------------------------------------------

    def _load(self):
        return json.loads(self.state_json)

    def _save(self, state):
        self.state_json = json.dumps(state)

    def _sender(self) -> str:
        return gl.message.sender_address.as_hex.lower()

    def _ensure_hunter_stats(self, state, addr: str):
        if addr not in state["hunter_stats"]:
            state["hunter_stats"][addr] = {
                "cases_submitted": 0,
                "sybil_finalized": 0,
                "rewards_earned_wei": 0,
                "challenges_won": 0,
                "challenges_lost": 0,
                "challenge_rewards_earned_wei": 0,
            }

    def _load_case(self, state, case_id: u256):
        key = str(int(case_id))
        if key not in state["cases"]:
            raise Exception("CASE_NOT_FOUND")
        return state["cases"][key]

    def _apply_final(self, state, case, verdict: str, signals):
        case["final_verdict"] = verdict
        case["final_signals"] = list(signals)
        case["final_weight_scaled"] = _weight_for(verdict)
        case["status"] = "VERDICT_" + verdict
        target = case["target_address"].lower()
        state["weights"][target] = {
            "weight_scaled": _weight_for(verdict),
            "verdict": verdict,
            "case_id": int(case["case_id"]),
        }
        hunter = case["hunter"]
        self._ensure_hunter_stats(state, hunter)
        if verdict == "SYBIL":
            stats = state["hunter_stats"][hunter]
            stats["sybil_finalized"] = int(stats["sybil_finalized"]) + 1

    # -- writes -------------------------------------------------------------

    @gl.public.write.payable
    def deposit_funding(self) -> str:
        value = int(gl.message.value)
        if value == 0:
            raise Exception("FUNDING_MUST_SEND_GEN")
        sender = self._sender()
        state = self._load()
        state["total_received_wei"] = int(state["total_received_wei"]) + value
        state["funding_pool_wei"] = int(state["funding_pool_wei"]) + value
        self._save(state)
        return json.dumps({
            "funder": sender,
            "deposited_wei": value,
            "deposited_gen": value // GEN_WEI,
            "funding_pool_wei": int(state["funding_pool_wei"]),
        })

    @gl.public.write
    def submit_case(self, target_address: str, evidence_url: str, evidence_note: str) -> u256:
        if not _is_hex_address(target_address):
            raise Exception("INVALID_TARGET_ADDRESS")
        if not evidence_url.startswith("https://"):
            raise Exception("EVIDENCE_URL_MUST_BE_HTTPS")
        if len(evidence_url) > 300:
            raise Exception("EVIDENCE_URL_TOO_LONG")
        if len(evidence_note) > 500:
            raise Exception("EVIDENCE_NOTE_TOO_LONG")
        sender = self._sender()
        state = self._load()
        self._ensure_hunter_stats(state, sender)
        case_id = int(state["next_case_id"])
        state["next_case_id"] = case_id + 1
        case = {
            "case_id": case_id,
            "target_address": target_address.lower(),
            "hunter": sender,
            "evidence_url": evidence_url,
            "evidence_note": evidence_note,
            "status": "OPEN",
            "pending_verdict": None,
            "pending_signals": [],
            "pending_round": 0,
            "evaluations": 0,
            "final_verdict": None,
            "final_signals": [],
            "final_weight_scaled": None,
            "challenge": None,
            "witnesses": [],
        }
        state["cases"][str(case_id)] = case
        state["case_order"].append(case_id)
        state["hunter_stats"][sender]["cases_submitted"] = int(state["hunter_stats"][sender]["cases_submitted"]) + 1
        self._save(state)
        return u256(case_id)

    @gl.public.write
    def evaluate_case(self, case_id: u256) -> str:
        sender = self._sender()
        state = self._load()
        case = self._load_case(state, case_id)
        if case["status"] in ("VERDICT_SYBIL", "VERDICT_HUMAN", "VERDICT_UNCERTAIN", "REWARD_PAID", "CLOSED_NO_REWARD"):
            raise Exception("CASE_ALREADY_DECIDED")
        if sender == case["hunter"]:
            raise Exception("HUNTER_MAY_NOT_JUDGE_OWN_CASE")
        if case["status"] == "EVIDENCE_REVIEW" and case["challenge"] is None:
            raise Exception("ALREADY_EVALUATED_USE_FINALIZE_OR_CHALLENGE")
        evidence_url = case["evidence_url"]
        challenged = case["challenge"] is not None

        def judge():
            try:
                response = gl.nondet.web.request(evidence_url, method="GET")
            except Exception:
                raise Exception("EVIDENCE_FETCH_FAILED_PENDING_RETRY")
            if response.status != 200:
                raise Exception("EVIDENCE_FETCH_FAILED_PENDING_RETRY")
            body = response.body
            if isinstance(body, bytes):
                text = body.decode("utf-8")
            else:
                text = str(body)
            if len(text) == 0:
                raise Exception("EVIDENCE_EMPTY_PENDING_RETRY")
            excerpt = text[:6000]
            prompt = (
                "You are a strict airdrop-sybil analyst. Read the behaviour evidence below and map it onto "
                "the fixed signal vocabulary. Return ONLY the signal codes whose supporting fact is stated "
                "explicitly in the evidence text. Do not infer a signal from a vague hint, and never invent "
                "a code outside the vocabulary.\n"
                "Sybil codes: SAME_FUNDER (address funded by the same source as many sibling addresses), "
                "IDENTICAL_TX_PATTERN (same amounts, same order, same contracts as siblings), "
                "BURST_ACTIVITY (many transactions in a very short window), "
                "FRESH_NO_HISTORY (first transaction very recent, no prior history).\n"
                "Human codes: LONG_HISTORY (first transaction long ago, sustained activity), "
                "DIVERSE_COUNTERPARTIES (many distinct counterparties), "
                "UNIQUE_BEHAVIOUR (varied amounts, timing and contracts, no cloned pattern), "
                "VERIFIED_ACTIVITY (linked to a verified public identity or attested activity).\n"
                "Respond with ONLY a JSON object, no prose: {\"signals\": [\"CODE\", ...]}. "
                "If no code is explicitly supported, return {\"signals\": []}.\n"
                "Evidence:\n" + excerpt
            )
            parsed = gl.nondet.exec_prompt(prompt, response_format="json")
            if isinstance(parsed, str):
                parsed = json.loads(parsed)
            if not isinstance(parsed, dict) or "signals" not in parsed:
                raise Exception("INVALID_JUDGE_OUTPUT_PENDING_RETRY")
            raw_signals = parsed["signals"]
            if not isinstance(raw_signals, list):
                raise Exception("INVALID_JUDGE_OUTPUT_PENDING_RETRY")
            clean = []
            for code in raw_signals:
                if not isinstance(code, str) or code not in ALL_SIGNALS:
                    raise Exception("INVALID_JUDGE_OUTPUT_PENDING_RETRY")
                if code not in clean:
                    clean.append(code)
            clean.sort()
            verdict = _verdict_for(clean)
            return {
                "signals": clean,
                "verdict": verdict,
                "evidence_sha256": pure_sha256_hex(text),
            }

        def validate(leader_result):
            if isinstance(leader_result, gl.vm.UserError):
                try:
                    judge()
                except Exception:
                    return True
                return False
            if not isinstance(leader_result, gl.vm.Return):
                return False
            leader = leader_result.calldata
            if not isinstance(leader, dict):
                return False
            try:
                own = judge()
            except Exception:
                return False
            if leader.get("verdict") != own["verdict"]:
                return False
            if leader.get("evidence_sha256") != own["evidence_sha256"]:
                return False
            if leader.get("signals") != own["signals"]:
                return False
            return True

        result = gl.vm.run_nondet_unsafe(judge, validate)
        signals = result["signals"]
        verdict = result["verdict"]
        if _verdict_for(signals) != verdict:
            raise Exception("VERDICT_MISMATCH_WITH_SIGNALS")

        state = self._load()
        case = self._load_case(state, case_id)
        if case["status"] in ("VERDICT_SYBIL", "VERDICT_HUMAN", "VERDICT_UNCERTAIN", "REWARD_PAID", "CLOSED_NO_REWARD"):
            raise Exception("CASE_ALREADY_DECIDED")
        case["evaluations"] = int(case["evaluations"]) + 1
        case["pending_round"] = int(case["pending_round"]) + 1
        if challenged:
            challenge = case["challenge"]
            first_verdict = case["pending_verdict"]
            first_signals = list(case["pending_signals"])
            challenger = challenge["challenger"]
            stake_wei = int(challenge["stake_wei"])
            reserved_wei = int(challenge["reserved_wei"])
            self._ensure_hunter_stats(state, challenger)
            challenger_stats = state["hunter_stats"][challenger]
            if verdict == first_verdict:
                # Challenge failed: the 3 GEN stake and the 2 GEN reservation
                # both go into the funding pool; no credit for the challenger.
                state["funding_pool_wei"] = int(state["funding_pool_wei"]) + stake_wei + reserved_wei
                challenger_stats["challenges_lost"] = int(challenger_stats["challenges_lost"]) + 1
                case["witnesses"].append({
                    "witness_id": "wit-" + str(case_id) + "-r" + str(case["pending_round"]),
                    "round": int(case["pending_round"]),
                    "kind": "FAILED_CHALLENGE",
                    "challenger": challenger,
                    "claimed_verdict": challenge["claimed_verdict"],
                    "claimed_signals": list(challenge["claimed_signals"]),
                    "first_verdict": first_verdict,
                    "second_verdict": verdict,
                    "stake_forfeited_wei": stake_wei,
                    "note": "Second evaluation agreed with the first verdict; challenge failed; 3 GEN stake forfeited to the funding pool.",
                })
            else:
                # Challenge succeeded: the challenger is credited the 3 GEN
                # stake back plus a 2 GEN reward (the reservation made at
                # challenge time covers the reward, so the pool is never
                # overdrawn). The first pending verdict survives as a witness.
                credit = stake_wei + reserved_wei
                prev = int(state["reward_credits"].get(challenger, 0))
                state["reward_credits"][challenger] = prev + credit
                challenger_stats["challenges_won"] = int(challenger_stats["challenges_won"]) + 1
                challenger_stats["challenge_rewards_earned_wei"] = int(challenger_stats["challenge_rewards_earned_wei"]) + reserved_wei
                case["witnesses"].append({
                    "witness_id": "wit-" + str(case_id) + "-r" + str(case["pending_round"]),
                    "round": int(case["pending_round"]),
                    "kind": "CONTRADICTION",
                    "challenger": challenger,
                    "claimed_verdict": challenge["claimed_verdict"],
                    "claimed_signals": list(challenge["claimed_signals"]),
                    "first_verdict": first_verdict,
                    "first_signals": first_signals,
                    "second_verdict": verdict,
                    "challenger_credit_wei": credit,
                    "note": "Second evaluation disagreed with the first pending verdict; first verdict kept as witness only; challenger credited 3 GEN stake refund + 2 GEN reward.",
                })
            case["challenge"] = None
            self._apply_final(state, case, verdict, signals)
        else:
            case["pending_verdict"] = verdict
            case["pending_signals"] = list(signals)
            case["status"] = "EVIDENCE_REVIEW"
        self._save(state)
        return json.dumps(self._load_case(self._load(), case_id))

    @gl.public.write.payable
    def challenge_case(self, case_id: u256, claimed_signals_csv: str, claimed_verdict: str) -> str:
        value = int(gl.message.value)
        if value != CHALLENGE_STAKE_WEI:
            raise Exception("CHALLENGE_STAKE_MUST_BE_3_GEN")
        sender = self._sender()
        state = self._load()
        case = self._load_case(state, case_id)
        if case["status"] != "EVIDENCE_REVIEW":
            raise Exception("CHALLENGE_ONLY_WHILE_EVIDENCE_REVIEW")
        if case["challenge"] is not None:
            raise Exception("CHALLENGE_ALREADY_OPEN")
        if sender == case["hunter"]:
            raise Exception("HUNTER_MAY_NOT_CHALLENGE_OWN_CASE")
        if int(state["funding_pool_wei"]) < CHALLENGE_SUCCESS_REWARD_WEI:
            raise Exception("FUNDING_POOL_TOO_LOW_FOR_CHALLENGE_REWARD")
        claimed_signals = _parse_signals_csv(claimed_signals_csv)
        if _verdict_for(claimed_signals) != claimed_verdict:
            raise Exception("CLAIMED_VERDICT_MISMATCH_WITH_SIGNALS")
        if claimed_verdict == case["pending_verdict"] and claimed_signals == list(case["pending_signals"]):
            raise Exception("CHALLENGE_MUST_DIFFER_FROM_PENDING")
        self._ensure_hunter_stats(state, sender)
        # Reserve the 2 GEN success reward from the pool now, so a later
        # successful challenge can always be paid even if the pool is
        # drawn down in between. The stake itself is held in the case.
        state["funding_pool_wei"] = int(state["funding_pool_wei"]) - CHALLENGE_SUCCESS_REWARD_WEI
        state["total_received_wei"] = int(state["total_received_wei"]) + value
        case["challenge"] = {
            "challenger": sender,
            "claimed_signals": claimed_signals,
            "claimed_verdict": claimed_verdict,
            "stake_wei": value,
            "reserved_wei": CHALLENGE_SUCCESS_REWARD_WEI,
        }
        self._save(state)
        return json.dumps(self._load_case(self._load(), case_id))

    @gl.public.write
    def finalize_case(self, case_id: u256) -> str:
        state = self._load()
        case = self._load_case(state, case_id)
        if case["status"] != "EVIDENCE_REVIEW":
            raise Exception("FINALIZE_ONLY_WHILE_EVIDENCE_REVIEW")
        if case["challenge"] is not None:
            raise Exception("OPEN_CHALLENGE_MUST_BE_EVALUATED_FIRST")
        if case["pending_verdict"] is None:
            raise Exception("NO_PENDING_VERDICT")
        self._apply_final(state, case, case["pending_verdict"], list(case["pending_signals"]))
        self._save(state)
        return json.dumps(self._load_case(self._load(), case_id))

    @gl.public.write
    def claim_case_reward(self, case_id: u256) -> str:
        sender = self._sender()
        state = self._load()
        case = self._load_case(state, case_id)
        if case["status"] != "VERDICT_SYBIL":
            raise Exception("REWARD_ONLY_FOR_VERDICT_SYBIL")
        if sender != case["hunter"]:
            raise Exception("ONLY_CASE_HUNTER_MAY_CLAIM")
        if int(state["funding_pool_wei"]) < HUNTER_REWARD_WEI:
            raise Exception("FUNDING_POOL_INSUFFICIENT")
        state["funding_pool_wei"] = int(state["funding_pool_wei"]) - HUNTER_REWARD_WEI
        prev = int(state["reward_credits"].get(sender, 0))
        state["reward_credits"][sender] = prev + HUNTER_REWARD_WEI
        self._ensure_hunter_stats(state, sender)
        stats = state["hunter_stats"][sender]
        stats["rewards_earned_wei"] = int(stats["rewards_earned_wei"]) + HUNTER_REWARD_WEI
        case["status"] = "REWARD_PAID"
        self._save(state)
        return json.dumps({
            "hunter": sender,
            "case_id": int(case_id),
            "reward_wei": HUNTER_REWARD_WEI,
            "reward_gen": HUNTER_REWARD_WEI // GEN_WEI,
            "credit_wei": int(state["reward_credits"][sender]),
            "funding_pool_wei": int(state["funding_pool_wei"]),
        })

    @gl.public.write
    def close_case(self, case_id: u256) -> str:
        state = self._load()
        case = self._load_case(state, case_id)
        if case["status"] not in ("VERDICT_HUMAN", "VERDICT_UNCERTAIN"):
            raise Exception("CLOSE_ONLY_AFTER_HUMAN_OR_UNCERTAIN_VERDICT")
        case["status"] = "CLOSED_NO_REWARD"
        self._save(state)
        return json.dumps(self._load_case(self._load(), case_id))

    @gl.public.write
    def withdraw_reward(self) -> str:
        sender = self._sender()
        state = self._load()
        amount = int(state["reward_credits"].get(sender, 0))
        if amount == 0:
            raise Exception("NO_REWARD_CREDIT")
        # Pull payment: zero the credit BEFORE transferring, so a failed
        # or re-entered transfer can never pay twice.
        state["reward_credits"][sender] = 0
        state["total_paid_out_wei"] = int(state["total_paid_out_wei"]) + amount
        self._save(state)
        _Recipient(Address(sender)).emit_transfer(value=u256(amount))
        return json.dumps({
            "beneficiary": sender,
            "withdrawn_wei": amount,
            "withdrawn_gen": amount // GEN_WEI,
            "total_paid_out_wei": int(state["total_paid_out_wei"]),
        })

    # -- views --------------------------------------------------------------

    @gl.public.view
    def get_case(self, case_id: u256) -> str:
        state = self._load()
        return json.dumps(self._load_case(state, case_id))

    @gl.public.view
    def get_case_count(self) -> u256:
        state = self._load()
        return u256(len(state["case_order"]))

    @gl.public.view
    def list_cases(self, offset: u256, limit: u256) -> str:
        if limit < 1 or limit > 20:
            raise Exception("LIMIT_MUST_BE_1_TO_20")
        state = self._load()
        order = state["case_order"]
        total = len(order)
        start = int(offset)
        if start >= total:
            return json.dumps([])
        end = start + int(limit)
        if end > total:
            end = total
        out = []
        index = start
        while index < end:
            out.append(state["cases"][str(order[index])])
            index += 1
        return json.dumps(out)

    @gl.public.view
    def get_weight(self, target_address: str) -> str:
        state = self._load()
        key = target_address.lower()
        if key not in state["weights"]:
            return json.dumps({"target_address": key, "weight_scaled": None, "verdict": None, "case_id": None})
        return json.dumps(state["weights"][key])

    @gl.public.view
    def get_reward_credit(self, address: str) -> str:
        state = self._load()
        key = address.lower()
        return json.dumps({"address": key, "credit_wei": int(state["reward_credits"].get(key, 0))})

    @gl.public.view
    def get_funding_pool(self) -> str:
        state = self._load()
        return json.dumps({
            "funding_pool_wei": int(state["funding_pool_wei"]),
            "hunter_reward_wei": HUNTER_REWARD_WEI,
            "challenge_stake_wei": CHALLENGE_STAKE_WEI,
            "challenge_success_reward_wei": CHALLENGE_SUCCESS_REWARD_WEI,
        })

    @gl.public.view
    def get_hunter_stats(self, address: str) -> str:
        state = self._load()
        key = address.lower()
        self._ensure_hunter_stats(state, key)
        stats = state["hunter_stats"][key]
        return json.dumps({
            "hunter": key,
            "cases_submitted": int(stats["cases_submitted"]),
            "sybil_finalized": int(stats["sybil_finalized"]),
            "rewards_earned_wei": int(stats["rewards_earned_wei"]),
            "challenges_won": int(stats["challenges_won"]),
            "challenges_lost": int(stats["challenges_lost"]),
            "challenge_rewards_earned_wei": int(stats["challenge_rewards_earned_wei"]),
        })

    @gl.public.view
    def get_ledger(self) -> str:
        state = self._load()
        credits_total = 0
        for amount in state["reward_credits"].values():
            credits_total += int(amount)
        stakes_total = 0
        reserved_total = 0
        for case in state["cases"].values():
            challenge = case.get("challenge")
            if challenge is not None:
                stakes_total += int(challenge["stake_wei"])
                reserved_total += int(challenge["reserved_wei"])
        total_received = int(state["total_received_wei"])
        total_paid_out = int(state["total_paid_out_wei"])
        funding_pool = int(state["funding_pool_wei"])
        contract_balance = int(self.balance)
        accounted = total_received - total_paid_out
        invariant = (
            total_received == total_paid_out + funding_pool + reserved_total + stakes_total + credits_total
            and contract_balance == accounted
        )
        return json.dumps({
            "total_received_wei": total_received,
            "total_paid_out_wei": total_paid_out,
            "funding_pool_wei": funding_pool,
            "challenge_reserved_wei": reserved_total,
            "open_stakes_wei": stakes_total,
            "reward_credits_wei": credits_total,
            "contract_balance_wei": contract_balance,
            "accounted_wei": accounted,
            "invariant_ok": invariant,
        })

    @gl.public.view
    def get_leaderboard(self, limit: u256) -> str:
        if limit < 1 or limit > 20:
            raise Exception("LIMIT_MUST_BE_1_TO_20")
        state = self._load()
        rows = []
        for hunter, stats in state["hunter_stats"].items():
            total_rewards = int(stats["rewards_earned_wei"]) + int(stats["challenge_rewards_earned_wei"])
            rows.append({
                "hunter": hunter,
                "cases_submitted": int(stats["cases_submitted"]),
                "sybil_finalized": int(stats["sybil_finalized"]),
                "rewards_earned_wei": int(stats["rewards_earned_wei"]),
                "challenges_won": int(stats["challenges_won"]),
                "challenges_lost": int(stats["challenges_lost"]),
                "challenge_rewards_earned_wei": int(stats["challenge_rewards_earned_wei"]),
                "total_rewards_wei": total_rewards,
            })
        rows.sort(key=lambda r: (-r["total_rewards_wei"], -r["sybil_finalized"], r["hunter"]))
        return json.dumps(rows[:int(limit)])
