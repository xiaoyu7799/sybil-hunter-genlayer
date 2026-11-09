# Live verification

Network: Stable Studionet (chain 61999). Contract: `0xAA9667d41895928f7DE2AACC2fd0F1764f6c6EE4`
Explorer: https://explorer-studio.genlayer.com/address/0xAA9667d41895928f7DE2AACC2fd0F1764f6c6EE4
Checked at: 2026-11-09T07:52:54.630Z

## Transactions (all FINALIZED)

- claim_demo_funds (A): `0x058add19a146af89ec1a98fcc4ba3dc520a4315f7c1dc285ce0813a537a5767f` — FINALIZED
- submit_case 0 (sybil): `0x9289a7a371f75f1ed6c73cfdda3ad5d821ff2e653b39e5d98fe85ae33ecca833` — FINALIZED
- submit_case 1 (human): `0x38d8701aae148277661a745a1bd641d3bf837d183fa4c591034c092b541d0a8c` — FINALIZED
- submit_case 2 (thin): `0x0254818cc9c892ea6552484406cfd658bef4796ea97bdd8cf47817ac66c7481f` — FINALIZED
- evaluate_case 0 (first) (attempt 1): `0xa5126354ffbe88bc1d6d16cb1979c841db96a688d11b1cc8baf8c5b0a24000c4` — FINALIZED
- challenge_case 0 (claim HUMAN): `0xfd54c2ff2e78f21c0e6a320608c438ebf86b30ff897f578c64b3182e11dfbbb0` — FINALIZED
- evaluate_case 0 (second, finalizes) (attempt 1): `0x7a64d07025112c92288c40d055389a2768aafe9a4e32d1744cf718a5334b63b8` — FINALIZED
- evaluate_case 1 (attempt 1): `0xf88f1aec15a24f4fc236bd87a6b83b01ca59d6c03327c59d3134c2118d9ed84c` — FINALIZED
- finalize_case 1: `0xb57caf295acc18b30864a5d079f016deb223195d868865351da04a178d2c7695` — FINALIZED
- evaluate_case 2 (attempt 1): `0x11080b5349331a2a1cd4d0cf83403f7ba2a3ca8a2732ccc64ff286c5b894a30a` — FINALIZED
- finalize_case 2: `0x477f236da7f247670a9e6fc11e331afd81e65606e4c1ddc65a0c5b870540f519` — FINALIZED
- claim_hunter_reward 0: `0x92b69b11587744891905747a4b044a59f61bfcfb83b59b9bfb1076fed2e0ae14` — FINALIZED

## Read-back (via RPC, after the flow)

- Case 0: status `FINALIZED`, verdict `SYBIL`, signals `["BURST_ACTIVITY","FRESH_NO_HISTORY","IDENTICAL_TX_PATTERN","SAME_FUNDER"]`, weight `0`, witnesses `1`
- Case 1: status `FINALIZED`, verdict `HUMAN`, signals `["DIVERSE_COUNTERPARTIES","LONG_HISTORY","UNIQUE_BEHAVIOUR"]`, weight `1000000`
- Case 2: status `FINALIZED`, verdict `UNCERTAIN`, signals `["BURST_ACTIVITY"]`, weight `500000`
- Weights: sybil target `{"weight_scaled":0,"verdict":"SYBIL","case_id":0}`, human target `{"weight_scaled":1000000,"verdict":"HUMAN","case_id":1}`, thin target `{"weight_scaled":500000,"verdict":"UNCERTAIN","case_id":2}`
- Hunter balance: `{"address":"0x2b311e317291323371c5f2eb531204fd0d8dd904","balance":10500,"unit":"mGEN (simulated)"}`; reward claimed: `true`
- Challenger reputation: `{"address":"0x773bf6a99db03ddeca9b60b2c300ad96e13570ac","reputation":95}`
- Reward pool: `{"reward_pool":99500,"hunter_reward":500,"unit":"mGEN (simulated)"}`
- Leaderboard: `[{"hunter":"0x2b311e317291323371c5f2eb531204fd0d8dd904","cases_submitted":3,"sybil_finalized":1,"rewards_earned":500,"reputation":100},{"hunter":"0x773bf6a99db03ddeca9b60b2c300ad96e13570ac","cases_submitted":0,"sybil_finalized":0,"rewards_earned":0,"reputation":95}]`
- Case count: `3`

Full machine-readable record: `evidence.json` in this repository.
