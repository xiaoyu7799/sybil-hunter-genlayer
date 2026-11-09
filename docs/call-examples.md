# Call examples

Network: Stable Studionet, chain 61999, RPC `https://studio.genlayer.com/api`.
Contract address: see `deployment.json` / `README.md`.
All amounts are simulated mGEN ledger units inside the contract, not real GEN.

## JavaScript (genlayer-js 1.1.8)

```js
import { createClient, createAccount, generatePrivateKey } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const address = "<CONTRACT_ADDRESS>";
const account = createAccount(generatePrivateKey()); // ephemeral test account
const client = createClient({ chain: studionet, account });

// 1. Credit 10000 simulated mGEN once per address.
await client.writeContract({ address, functionName: "claim_demo_funds", args: [], value: 0n });

// 2. Submit a case: target address + behaviour-evidence URL + short note.
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
//    and must agree on the exact signal set; the case becomes EVALUATING.
await client.writeContract({ address, functionName: "evaluate_case", args: [0n], value: 0n });

// 4. Challenge while EVALUATING (anyone except the hunter). Claimed
//    signals must map to the claimed verdict under the documented rules.
await client.writeContract({
  address,
  functionName: "challenge_case",
  args: [0n, "LONG_HISTORY,DIVERSE_COUNTERPARTIES", "HUMAN"],
  value: 0n,
});

// 5. Second evaluation finalizes directly (challenge open).
await client.writeContract({ address, functionName: "evaluate_case", args: [0n], value: 0n });

// 6. Or finalize directly when no challenge is open (permissionless).
await client.writeContract({ address, functionName: "finalize_case", args: [1n], value: 0n });

// 7. Hunter claims the 500 mGEN reward for a finalized SYBIL case.
await client.writeContract({ address, functionName: "claim_hunter_reward", args: [0n], value: 0n });

// Reads (no wallet needed):
const kase = await client.readContract({ address, functionName: "get_case", args: [0n] });
const weight = await client.readContract({ address, functionName: "get_weight", args: ["0x1111111111111111111111111111111111111111"] });
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
  stays `EVALUATING` and the call can be repeated. `scripts/flow.mjs`
  retries up to 4 times.
- `claim_demo_funds` and `claim_hunter_reward` each enforce once-per
  address / once-per-case; a second call is rejected.
- A hunter cannot call `evaluate_case` or `challenge_case` on their own case.
