# Reviewer fast path

Fastest way to recheck this contract (about 10 minutes):

1. Read `docs/mechanism.md` — the verdict rules, the real-GEN economics,
   and the worst-case spread proof (exactly 0, by exact signal-set
   equality).
2. Read `contracts/sybil_hunter.py` — one file. The verdict function
   `_verdict_for`, the equivalence check in `evaluate_case`, the
   challenge stake/reservation rules, and the pull-payment
   `withdraw_reward` are the core.
3. Open `deployment.json` — network (Stable Studionet, 61999), contract
   address, deploy transaction, deploy source commit, and the SHA-256 of
   the deployed source file (verified against `gen_getContractCode`).
4. Verify the deployed code matches the repository: fetch the contract
   source from the explorer page for the address in `deployment.json`
   and compare its SHA-256 with `contractSha256` in `deployment.json`
   and with `sha256sum contracts/sybil_hunter.py` at the deploy commit.
5. Open `evidence.json` — every core transaction hash with FINALIZED
   status, the read-back values (cases, weights, ledger, credits, EOA
   balances), and the GEN reconciliation table.
6. Recheck on chain (no wallet needed, read-only):
   - `get_case` for ids 0, 1, 2 — verdicts, signals, weights, witnesses.
   - `get_weight` for `0x1111…1111`, `0x2222…2222`, `0x3333…3333` —
     expect 0, 1000000, 500000.
   - `get_ledger` — expect `invariant_ok` true and the funding pool,
     credits and paid-out totals to reconcile with `evidence.json`.
     `stray_wei` should be 0 after the sweep in the live run.
   - `get_leaderboard` with limit 10.
7. Re-run the local mock tests (mock only, not chain evidence):
   `python3 tests/test_local.py` — 319 checks, including all 256 signal
   subsets, the SHA-256 test vectors, and the ledger invariant and
   stray-sweep simulations.
