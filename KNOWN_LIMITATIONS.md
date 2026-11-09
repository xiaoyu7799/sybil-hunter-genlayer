# Known limitations

- **LLM judgement variance.** The leader and validators each ask an LLM
  to map prose evidence onto the fixed 8-code signal vocabulary. If the
  judges derive different signal sets, consensus is not reached, nothing
  is stored, and the case stays `EVALUATING` for a retry. The mechanism
  guarantees that a disagreement can never store a wrong weight; it does
  not guarantee that any single evaluation attempt reaches consensus.
  The live run in `evidence.json` shows the attempts that succeeded.
- **Evidence is prose, judged as written.** The contract checks that the
  evidence URL is reachable and binds the result to the SHA-256 of the
  fetched bytes, but it cannot verify that the prose report itself is
  truthful. A fabricated evidence document would be judged as written.
  The weight is only as good as the evidence submitted for the case.
- **Simulated mGEN only.** All balances, the faucet, and hunter rewards
  are ledger entries inside this contract, denominated in simulated mGEN.
  No real GEN moves, and the weights are numbers for airdrop allocation
  logic, not a token distribution.
- **No appeal after finality.** A `FINALIZED` verdict is immutable by
  design. A wrong finalized verdict can only be superseded by a new case
  for the same target address; the old finalized verdict stays on chain
  as history.
- **Single evidence URL per case.** Each case carries one evidence URL.
  Additional sources must be combined into one document before
  submission.
- **Script accounts only.** The on-chain flow was run with ephemeral
  generated accounts through `genlayer-js`. No browser wallet flow was
  used for this contract-only primitive.
