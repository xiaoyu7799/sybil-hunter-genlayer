# Known limitations

- **LLM judgement variance.** The leader and validators each ask an LLM
  to map prose evidence onto the fixed 8-code signal vocabulary. If the
  judges derive different signal sets, consensus is not reached, nothing
  is stored, and the case stays `EVIDENCE_REVIEW` for a retry. The
  mechanism guarantees that a disagreement can never store a wrong
  weight; it does not guarantee that any single evaluation attempt
  reaches consensus. The live run in `evidence.json` shows the attempts
  that succeeded.
- **Evidence is prose, judged as written.** The contract checks that the
  evidence URL is reachable and binds the result to the SHA-256 of the
  fetched bytes, but it cannot verify that the prose report itself is
  truthful. A fabricated evidence document would be judged as written.
  The weight is only as good as the evidence submitted for the case.
- **Reward pool can run dry.** The hunter reward (5 GEN) and the
  challenge success reward (2 GEN) are paid from the funding pool,
  which is filled only by `deposit_funding`. If the pool holds less
  than 5 GEN, a `SYBIL` reward claim fails until the pool is topped up;
  the verdict itself is unaffected and the case stays `VERDICT_SYBIL`.
  A challenge cannot be opened while the pool holds less than 2 GEN.
  The deployment in `evidence.json` funded the pool with 100 GEN.
- **No appeal after finality.** A decided verdict is immutable by
  design. A wrong decided verdict can only be superseded by a new case
  for the same target address; the old decided verdict stays on chain
  as history.
- **Single evidence URL per case.** Each case carries one evidence URL.
  Additional sources must be combined into one document before
  submission.
- **Script accounts only.** The on-chain flow was run with ephemeral
  generated accounts through `genlayer-js`. No browser wallet flow was
  used for this contract-only primitive.
