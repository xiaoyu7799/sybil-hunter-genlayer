# Mechanism

## What consensus decides

Whether a target address behaves like a sybil-cluster member or a human,
judged from behaviour evidence. The verdict is one of `SYBIL`, `HUMAN`,
`UNCERTAIN`. The consequences are deterministic:

| Verdict | Airdrop weight (stored, scaled x1,000,000) | Hunter reward |
| --- | --- | --- |
| `SYBIL` | `0` | hunter may claim 500 mGEN (simulated) from the reward pool, once per case |
| `HUMAN` | `1000000` (1.0) | none |
| `UNCERTAIN` | `500000` (0.5) | none |

Weights are stored as scaled integers. Only the three values above can
ever be stored: the weight is produced by a fixed mapping from the
verdict, never by arithmetic on a score.

## How the verdict is produced

1. A hunter submits a case: a target address and an `https://` URL
   pointing at behaviour evidence (prose: an analyst note or an
   explorer-derived behaviour report).
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
   - `HUMAN` iff at least 2 human signals and 0 sybil signals
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
is reached, nothing is stored, and the case stays `EVALUATING` for a
retry. A wrong value is never stored.

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

## Challenge and finality

- While a case is `EVALUATING` (a pending verdict exists, not yet
  finalized), anyone except the hunter may challenge with an alternative
  signal set. The claimed signals must map to the claimed verdict under
  the same deterministic rules, and must differ from the pending result.
- A second evaluation then runs and finalizes directly. If the second
  verdict equals the first, the challenge fails and the challenger loses
  5 reputation. If it differs, the first pending verdict and its signals
  are appended to the case witness list and the second verdict is
  finalized. Across rounds there is still exactly one stored weight at
  any time; the superseded pending verdict survives only as a witness.
- `finalize_case` is permissionless and may be called by anyone once a
  pending verdict exists and no challenge is open. A `FINALIZED` verdict
  is immutable: evaluating, challenging, or finalizing it again is
  rejected.
- A hunter may not judge their own case: `evaluate_case` and
  `challenge_case` reject the case hunter as caller.

## Reputation and rewards

- Reputation starts at 100 on first participation (submitting a case or
  challenging one). A failed challenge costs 5 reputation (floor 0); a
  successful challenge (second verdict differs) gains 5.
- `claim_demo_funds` credits 10000 simulated mGEN once per address.
  The hunter reward is a fixed 500 simulated mGEN per finalized `SYBIL`
  case, paid from a reward pool seeded at 100000 simulated mGEN at
  deployment, once per case per hunter. If the pool is empty, the claim
  fails. All balances are ledger entries inside this contract only.
- The leaderboard ranks hunters by rewards earned, then by finalized
  sybil cases, then by address.

## Failure behaviour

- Evidence fetch failure (non-200, empty body, unreachable URL) raises
  before any state is written, so the case stays in its previous state
  and the evaluation can be retried.
- An LLM answer outside the fixed vocabulary, or a verdict that does not
  match its signal set under the deterministic rules, is rejected the
  same way.
- No floats cross the nondet boundary: signals are strings, the verdict
  is a string, the evidence binding is a hex string, and weights are
  integers. Hashing uses a pure-Python SHA-256 implemented in the
  contract, verified against the standard library on test vectors in the
  local mock tests.
