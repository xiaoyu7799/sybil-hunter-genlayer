# Call examples

Network: Stable Studionet, chain 61999, RPC `https://studio.genlayer.com/api`.
Contract address: see `deployment.json` / `README.md`.
All GEN amounts are wei integers (1 GEN = 10^18 wei); testnet GEN is free
from the faucet, zero cash cost.

## JavaScript (genlayer-js 1.1.8)

```js
import { createClient, createAccount, generatePrivateKey } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const address = "<CONTRACT_ADDRESS>";
const account = createAccount(generatePrivateKey()); // ephemeral test account
const client = createClient({ chain: studionet, account });
const GEN = 10n ** 18n;

// 1. Fund the reward pool with real testnet GEN (payable).
await client.writeContract({
  address, functionName: "deposit_funding", args: [],
  value: 100n * GEN,
});

// 2. Submit a case for free: target address + behaviour-evidence URL + note.
const submitTx = await client.writeContract({
  address,
  functionName: "submit_case",
  args: [
    "0x1111111111111111111111111111111111111111",
    "https://raw.githubusercontent.com/xiaoyu7799/sybil-hunter-genlayer/main/evidence/case-sybil-evidence.json",
    "Cluster candidate: shared funder, identical pattern, burst, fresh.",
  ],
  value: 0n,
});

// 3. Evaluate (anyone except the hunter). Validators fetch the evidence
//    and must agree on the exact signal set; the case becomes
//    EVIDENCE_REVIEW with a pending verdict.
await client.writeContract({ address, functionName: "evaluate_case", args: [0n], value: 0n });

// 4. Challenge while EVIDENCE_REVIEW (anyone except the hunter), staking
//    exactly 3 GEN. Claimed signals must map to the claimed verdict
//    under the documented rules and differ from the pending result.
await client.writeContract({
  address,
  functionName: "challenge_case",
  args: [0n, "LONG_HISTORY,DIVERSE_COUNTERPARTIES", "HUMAN"],
  value: 3n * GEN,
});

// 5. Second evaluation finalizes directly (challenge open).
await client.writeContract({ address, functionName: "evaluate_case", args: [0n], value: 0n });

// 6. Or finalize directly when no challenge is open (permissionless).
await client.writeContract({ address, functionName: "finalize_case", args: [1n], value: 0n });

// 7. Close a HUMAN / UNCERTAIN case with no reward.
await client.writeContract({ address, functionName: "close_case", args: [1n], value: 0n });

// 8. Hunter claims the 5 GEN reward credit for a finalized SYBIL case.
await client.writeContract({ address, functionName: "claim_case_reward", args: [0n], value: 0n });

// 9. Withdraw the credit to your own address (pull payment).
await client.writeContract({ address, functionName: "withdraw_reward", args: [], value: 0n });

// Reads (no wallet needed):
const kase = await client.readContract({ address, functionName: "get_case", args: [0n] });
const weight = await client.readContract({ address, functionName: "get_weight", args: ["0x1111111111111111111111111111111111111111"] });
const ledger = await client.readContract({ address, functionName: "get_ledger", args: [] });
const board = await client.readContract({ address, functionName: "get_leaderboard", args: [10n] });
```

## Scripted end-to-end run

```bash
npm install
node scripts/deploy.mjs   # deploys, writes deployment.json
node scripts/flow.mjs     # full business flow on-chain, writes evidence.json
python3 tests/test_local.py   # local mock tests only (not on-chain evidence)
```

## Notes

- `evaluate_case` may need a retry if the LLM judges disagree: the case
  stays `EVIDENCE_REVIEW` and the call can be repeated. `scripts/flow.mjs`
  retries up to 4 times.
- `challenge_case` requires exactly 3 GEN and a funding pool of at least
  2 GEN (the success reward is reserved at challenge time).
- `claim_case_reward` requires the pool to hold at least 5 GEN; if the
  pool is short, top it up with `deposit_funding` and retry.
- A hunter cannot call `evaluate_case` or `challenge_case` on their own case.
- Fund a test account with testnet GEN via
  `sim_fundAccount` (see `scripts/flow.mjs`) or the faucet at
  `https://studio.genlayer.com/validators`.
