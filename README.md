# Sybil Hunter

Validators judge address-behaviour evidence and score airdrop sybil risk on chain: `SYBIL` / `HUMAN` / `UNCERTAIN` decide the airdrop weight (0 / 1 / 0.5). A confirmed sybil pays the hunter a fixed 5 GEN reward in real testnet GEN; a challenger stakes 3 GEN and wins it back plus 2 GEN when a second evaluation overturns the first verdict.

- Contract: see [`deployment.json`](deployment.json) (previous contract `0xAA9667d41895928f7DE2AACC2fd0F1764f6c6EE4` is superseded — it used a simulated ledger with no real GEN movement)
- Network: Stable Studionet, chain 61999, RPC `https://studio.genlayer.com/api`

## How it works

1. Anyone funds the reward pool with real testnet GEN via `deposit_funding` (payable). Studionet GEN is free from the faucet, zero cash cost.
2. A hunter submits a case for free: a target address plus a URL pointing at behaviour evidence (prose report).
3. Validators independently fetch the same evidence and map it onto a fixed vocabulary of 8 signal codes (4 sybil, 4 human). The verdict is a deterministic function of the signal set: `SYBIL` needs at least 3 sybil signals and no human signal; `HUMAN` needs at least 2 human signals and no sybil signal; anything else — thin evidence, conflicting signals, no signals — is `UNCERTAIN`.
4. Equivalence requires exact equality of the whole signal set, the verdict, and the SHA-256 of the fetched evidence. Two validator-compatible outputs cannot store different weights: the worst-case spread in the stored weight is exactly 0 (see `docs/mechanism.md` for the proof and the full edge table).
5. While a case is `EVIDENCE_REVIEW`, anyone except the hunter may challenge with an alternative signal set, staking 3 GEN. A second evaluation finalizes directly: a matching second verdict fails the challenge and the 3 GEN stake is forfeited into the funding pool; a differing one is kept as a `CONTRADICTION` witness and the challenger is credited the 3 GEN stake back plus a 2 GEN reward. A decided verdict never changes.
6. Finalizing writes the airdrop weight: `SYBIL` → 0, `UNCERTAIN` → 500000 (0.5 scaled by 1,000,000), `HUMAN` → 1000000 (1.0). The hunter of a finalized `SYBIL` case may claim a fixed 5 GEN reward credit from the pool, once per case, and withdraw it with `withdraw_reward` (pull payment: the credit is zeroed before the transfer). `HUMAN` and `UNCERTAIN` cases close with no reward.
7. Case lifecycle: `OPEN` → `EVIDENCE_REVIEW` → `VERDICT_SYBIL` / `VERDICT_HUMAN` / `VERDICT_UNCERTAIN` → `REWARD_PAID` / `CLOSED_NO_REWARD`. The ledger invariant `total_received == total_paid_out + funding_pool + challenge_reserved + open_stakes + reward_credits` is readable via `get_ledger`.

## Contract

- Source: [`contracts/sybil_hunter.py`](contracts/sybil_hunter.py)
- Deployment manifest: [`deployment.json`](deployment.json) (network, address, deploy transaction, source commit, source SHA-256)
- Mechanism and worst-case proof: [`docs/mechanism.md`](docs/mechanism.md)
- Known limitations: [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md)

## Transactions and evidence

- Live verification (every core transaction FINALIZED + read-back): [`docs/live-verification.md`](docs/live-verification.md)
- Machine-readable evidence: [`evidence.json`](evidence.json)
- Reviewer fast path: [`docs/reviewer-fast-path.md`](docs/reviewer-fast-path.md)

## Usage

Call examples (JavaScript, `genlayer-js` 1.1.8) and the scripted end-to-end run are in [`docs/call-examples.md`](docs/call-examples.md):

```bash
npm install
node scripts/deploy.mjs   # deploys, writes deployment.json
node scripts/flow.mjs     # full business flow on-chain, writes evidence.json
python3 tests/test_local.py   # local mock tests only (not on-chain evidence)
```

All rewards, stakes and the funding pool are real testnet GEN on Stable Studionet (faucet-funded, zero cash cost). Amounts are wei integers on chain (1 GEN = 10^18 wei); weights are numbers for airdrop allocation logic, not a token distribution.
