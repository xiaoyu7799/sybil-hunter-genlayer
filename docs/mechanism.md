# Mechanism

## What consensus decides

Whether a target address behaves like a sybil-cluster member or a human,
judged from behaviour evidence. The verdict is one of `SYBIL`, `HUMAN`,
`UNCERTAIN`. The consequences are deterministic:

| Verdict | Airdrop weight (stored, scaled x1,000,000) | Hunter reward |
| --- | --- | --- |
| `SYBIL` | `0` | hunter may claim a fixed 5 GEN reward credit from the funding pool, once per case, then withdraw it |
| `HUMAN` | `1000000` (1.0) | none |
| `UNCERTAIN` | `500000` (0.5) | none |

Weights are stored as scaled integers. Only the three values above can
ever be stored: the weight is produced by a fixed mapping from the
verdict, never by arithmetic on a score.

All money is real testnet GEN on Stable Studionet (free from the faucet,
zero cash cost; 1 GEN = 10^18 wei). There is no demo ledger: the reward
pool is filled with real GEN by `deposit_funding`, the hunter reward is
a real GEN credit, and the challenge stake is real GEN.

## How the verdict is produced

1. Anyone funds the reward pool with real GEN via `deposit_funding`
   (payable). A hunter submits a case for free: a target address and an
   `https://` URL pointing at behaviour evidence (prose: an analyst note
   or an explorer-derived behaviour report).
2. An evaluation is triggered by anyone except the hunter. The leader and
   every validator independently fetch the same evidence URL and ask an
   LLM to map the prose onto a fixed vocabulary of 8 signal codes:

   - Sybil codes: `SAME_FUNDER`, `IDENTICAL_TX_PATTERN`,
     `BURST_ACTIVITY`, `FRESH_NO_HISTORY`
   - Human codes: `LONG_HISTORY`, `DIVERSE_COUNTERPARTIES`,
     `UNIQUE_BEHAVIOUR`, `VERIFIED_ACTIVITY`

   The LLM returns only the signal codes whose supporting fact is stated
   explicitly in the evidence. There is no continuous score.
3. The verdict is a pure deterministic function of the signal set:

   - `SYBIL` iff at least 3 sybil signals and 0 human signals
   - `HUMAN` iff at least 2 human signals and no sybil signal
   - `UNCERTAIN` otherwise

   Thin evidence (a single signal of either kind) is `UNCERTAIN`, never
   `SYBIL` or `HUMAN`. Conflicting signals (at least one of each kind)
   are `UNCERTAIN`, and the conflict is preserved, never silently
   resolved toward one side.

## Worst-case spread: exactly 0

Equivalence requires EXACT equality of the whole sorted signal set, the
verdict, and the SHA-256 of the fetched evidence bytes. There is no
numeric tolerance anywhere in the check — the band width is exactly 0.

Proof by transitivity of exact equality. Let `V` be any validator's
independently derived signal set. A leader output `L` passes `V` only if
`L == V`. Another leader output `L'` passes `V` only if `L' == V`.
Hence `L == L' == V`: at most one signal set can pass per evaluation
round, so at most one verdict and one weight can be stored per round.
The spread in the stored weight is exactly 0 — not 2%, not half a step,
exactly 0.

The only failure mode is liveness: if the judges disagree, no consensus
is reached, nothing is stored, and the case stays `EVIDENCE_REVIEW` for
a retry. A wrong value is never stored.

Edge table (every boundary, not only the happy path):

| Signals present | #sybil | #human | Verdict | Weight |
| --- | --- | --- | --- | --- |
| none | 0 | 0 | `UNCERTAIN` | 500000 |
| 1 sybil only (thin) | 1 | 0 | `UNCERTAIN` | 500000 |
| 2 sybil only | 2 | 0 | `UNCERTAIN` | 500000 |
| 3 sybil, 0 human | 3 | 0 | `SYBIL` | 0 |
| 4 sybil, 0 human | 4 | 0 | `SYBIL` | 0 |
| 3 sybil + 1 human (conflict) | 3 | 1 | `UNCERTAIN` | 500000 |
| 1 human only (thin) | 0 | 1 | `UNCERTAIN` | 500000 |
| 2 human, 0 sybil | 0 | 2 | `HUMAN` | 1000000 |
| 2 human + 1 sybil (conflict) | 1 | 2 | `UNCERTAIN` | 500000 |

All 256 signal subsets were enumerated in the local mock tests
(`tests/test_local.py`): every subset maps to exactly one verdict and
one of the three weights, and the exact-set equivalence property holds
for all of them.

## Case lifecycle

`OPEN` -> `EVIDENCE_REVIEW` -> `VERDICT_SYBIL` / `VERDICT_HUMAN` /
`VERDICT_UNCERTAIN` -> `REWARD_PAID` / `CLOSED_NO_REWARD`.

- `submit_case` creates the case as `OPEN`.
- The first `evaluate_case` stores the pending verdict and moves the
  case to `EVIDENCE_REVIEW`.
- `finalize_case` (permissionless, once a pending verdict exists and no
  challenge is open) moves the case to `VERDICT_SYBIL`, `VERDICT_HUMAN`
  or `VERDICT_UNCERTAIN` and writes the weight.
- A `VERDICT_SYBIL` case moves to `REWARD_PAID` when the hunter claims
  the 5 GEN reward credit with `claim_case_reward`.
- A `VERDICT_HUMAN` or `VERDICT_UNCERTAIN` case moves to
  `CLOSED_NO_REWARD` with `close_case`. No reward is paid for these.
- A decided verdict is immutable: evaluating, challenging, finalizing,
  claiming or closing it again is rejected.

## Challenge and finality

- While a case is `EVIDENCE_REVIEW` (a pending verdict exists, not yet
  finalized), anyone except the hunter may challenge with an alternative
  signal set, staking exactly 3 GEN (`challenge_case` is payable and
  rejects any other amount). The claimed signals must map to the claimed
  verdict under the same deterministic rules, and must differ from the
  pending result. Opening a challenge also requires the funding pool to
  hold at least 2 GEN, and immediately reserves that 2 GEN from the
  pool, so a successful challenge can always be paid even if the pool is
  drawn down before the second evaluation.
- A second evaluation then runs and finalizes directly. If the second
  verdict equals the first, the challenge fails: the 3 GEN stake and the
  2 GEN reservation both go into the funding pool, and the challenger
  gets nothing. If it differs, the first pending verdict and its signals
  are appended to the case witness list as a `CONTRADICTION` witness,
  the challenger is credited the 3 GEN stake back plus a 2 GEN reward
  (5 GEN total, withdrawable), and the second verdict is finalized.
  Across rounds there is still exactly one stored weight at any time;
  the superseded pending verdict survives only as a witness.
- `finalize_case` is permissionless and may be called by anyone once a
  pending verdict exists and no challenge is open.
- A hunter may not judge their own case: `evaluate_case` and
  `challenge_case` reject the case hunter as caller.

## Rewards, stakes, and the GEN ledger

- The funding pool starts empty at deployment. It is filled only by
  `deposit_funding` (payable, any amount of GEN above zero). The
  deployment in `evidence.json` funded it with 100 GEN.
- A hunter whose case finalizes as `SYBIL` may claim a fixed 5 GEN
  reward credit with `claim_case_reward`, once per case, from the
  funding pool. If the pool holds less than 5 GEN at claim time, the
  claim fails and the case stays `VERDICT_SYBIL` until the pool is
  topped up; the verdict itself is unaffected.
- All GEN movement is pull-payment. Finalization and claims only record
  a credit (wei integer). The beneficiary withdraws it themselves with
  `withdraw_reward`, which zeroes the credit BEFORE transferring, so a
  failed or re-entered transfer can never pay twice. No GEN is ever
  pushed to an address during finalization.
- Ledger invariant (checked by the `get_ledger` view):

  `total_received == total_paid_out + funding_pool + challenge_reserved
  + open_stakes + reward_credits`

  and the contract balance equals `total_received - total_paid_out`.
  `total_received` counts every GEN that entered (funding deposits and
  challenge stakes); `total_paid_out` counts every GEN that left via
  `withdraw_reward`. The live run reconciles this in `evidence.json`.

- Hunter evolution is tracked per address as `cases_submitted`,
  `sybil_finalized`, `rewards_earned_wei`, plus `challenges_won`,
  `challenges_lost` and `challenge_rewards_earned_wei`. The leaderboard
  ranks by total rewards earned (hunter rewards + challenge rewards),
  then by finalized sybil cases, then by address. There is no generic
  reputation score.

## Failure behaviour

- Evidence fetch failure (non-200, empty body, unreachable URL) raises
  before any state is written, so the case stays in its previous state
  and the evaluation can be retried.
- An LLM answer outside the fixed vocabulary, or a verdict that does not
  match its signal set under the deterministic rules, is rejected the
  same way.
- A challenge with the wrong stake amount, a challenge while the pool
  cannot cover the success reward, a reward claim while the pool is
  short, and a withdrawal with no credit all raise before any state is
  written.
- No floats cross the nondet boundary: signals are strings, the verdict
  is a string, the evidence binding is a hex string, and weights and GEN
  amounts are integers (wei). Hashing uses a pure-Python SHA-256
  implemented in the contract, verified against the standard library on
  test vectors in the local mock tests.
