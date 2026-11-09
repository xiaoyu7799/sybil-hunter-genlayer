# Sybil Hunter

Validators judge address-behaviour evidence and score airdrop sybil risk on chain: `SYBIL` / `HUMAN` / `UNCERTAIN` decide the airdrop weight (0 / 1 / 0.5) and pay the hunter a reward for a confirmed sybil.

- Contract: `0xAA9667d41895928f7DE2AACC2fd0F1764f6c6EE4`
- Explorer: `https://explorer-studio.genlayer.com/address/0xAA9667d41895928f7DE2AACC2fd0F1764f6c6EE4`
- Network: Stable Studionet, chain 61999, RPC `https://studio.genlayer.com/api`

## How it works

1. A hunter submits a case: a target address plus a URL pointing at
   behaviour evidence (prose report).
2. Validators independently fetch the same evidence and map it onto a
   fixed vocabulary of 8 signal codes (4 sybil, 4 human). The verdict is
   a deterministic function of the signal set: `SYBIL` needs at least 3
   sybil signals and no human signal; `HUMAN` needs at least 2 human
   signals and no sybil signal; anything else — thin evidence,
   conflicting signals, no signals — is `UNCERTAIN`.
3. Equivalence requires exact equality of the whole signal set, the
   verdict, and the SHA-256 of the fetched evidence. Two
   validator-compatible outputs cannot store different weights: the
   worst-case spread in the stored weight is exactly 0 (see
   `docs/mechanism.md` for the proof and the full edge table).
4. While a case is `EVALUATING`, anyone except the hunter may challenge
   with an alternative signal set. A second evaluation finalizes
   directly: a matching second verdict fails the challenge (challenger
   −5 reputation); a differing one is kept as a witness and the second
   verdict is finalized. A `FINALIZED` verdict never changes.
5. Finalizing writes the airdrop weight: `SYBIL` → 0, `UNCERTAIN` →
   500000 (0.5 scaled by 1,000,000), `HUMAN` → 1000000 (1.0). The hunter
   of a finalized `SYBIL` case may claim a fixed 500 simulated mGEN
   reward from the pool, once per case. Reputation starts at 100 on
   first participation.

## Contract

- Source: [`contracts/sybil_hunter.py`](contracts/sybil_hunter.py)
- Deployment manifest: [`deployment.json`](deployment.json) (network,
  address, deploy transaction, source commit, source SHA-256)
- Mechanism and worst-case proof: [`docs/mechanism.md`](docs/mechanism.md)
- Known limitations: [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md)

## Transactions and evidence

- Live verification (every core transaction FINALIZED + read-back):
  [`docs/live-verification.md`](docs/live-verification.md)
- Machine-readable evidence: [`evidence.json`](evidence.json)
- Reviewer fast path: [`docs/reviewer-fast-path.md`](docs/reviewer-fast-path.md)

## Usage

Call examples (JavaScript, `genlayer-js` 1.1.8) and the scripted
end-to-end run are in [`docs/call-examples.md`](docs/call-examples.md):

```bash
npm install
node scripts/deploy.mjs   # deploys, writes deployment.json
node scripts/flow.mjs     # full business flow on-chain, writes evidence.json
python3 tests/test_local.py   # local mock tests only (not on-chain evidence)
```

All balances and rewards are simulated mGEN ledger units inside the
contract. No real GEN moves; weights are numbers for airdrop allocation,
not a token distribution.
