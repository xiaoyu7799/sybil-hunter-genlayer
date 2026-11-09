# Live verification

Network: Stable Studionet (chain 61999). Contract: `0x568b113a7553D8b2D62D26779F7a7cb0a725F376`
Explorer: https://explorer-studio.genlayer.com/address/0x568b113a7553D8b2D62D26779F7a7cb0a725F376
Checked at: 2026-11-09T11:36:36.522Z

Previous contract `0xAA9667d41895928f7DE2AACC2fd0F1764f6c6EE4` is superseded: it used a ledger with no real GEN movement. Three interim deployments of this version are also superseded: `0x2CaF1BC4Ecf1d47853695a5734d4955042Bdf918` (aborted run: a flow-script bug in the challenge claim, hunter key lost with the aborted process), `0xdc343813A233A43C2Db47Ee9df848e6a583C09CE` (ledger invariant broken by 1 GEN of stray from a rejected payable call, before sweep_stray_gen existed; its 105 GEN of faucet GEN stays locked there), and `0x3acFa1C7Ec773e5026b0E0f9ec58cB6754f53F34` (aborted run: the VM restarted mid-flow after funding + 3 submits + 1 evaluation; its 100 GEN of faucet GEN stays locked there). This deployment replaces them.

## Transactions (all FINALIZED)

- deposit_funding 100 GEN (D): `0x942b952657b40c48559338c35dde236192f72eb01df0364bdb9c11673f924024` — FINALIZED
- submit_case 0 (sybil): `0x97eaafb96b73cbc72cc4bd90ac7906a446f7538d7a4eefdbfe6253ad36ff6cd3` — FINALIZED
- submit_case 1 (human): `0xf37a40f8668cb67234db1626357c345266eff2616cd76c3c7b71cfc014d492b6` — FINALIZED
- submit_case 2 (thin): `0x75cdfb0eae12f6237b999a680a03afe07c6baa367a68b10be3760a608c4c6442` — FINALIZED
- evaluate_case 0 (first) (attempt 1): `0x01d6dad838ddddeb0b2379854fc9496357c89fba6c99e73895d884957751b8c9` — FINALIZED
- challenge_case 0 (claim HUMAN, 3 GEN): `0xe4e30bddb6a18fa602757a46fe95cd797721103f7a77b8863e9157239b0de508` — FINALIZED
- sweep_stray_gen (stray from wrong-stake probe): `0xf35ab3e5515d218a7c89c6ec916b0453c2126251df8ae35934475152a688bf6a` — FINALIZED
- evaluate_case 0 (second, finalizes) (attempt 1): `0x9f953b74003cadea950de6d889ac525081809a05f5f9b8326bd9b72b58f33845` — FINALIZED
- claim_case_reward 0 (5 GEN credit): `0x0035c96f8ab30b8e470818c36e4cafcee5c1aac7e816b512435a3837a79a5cad` — FINALIZED
- evaluate_case 1 (attempt 1): `0xfd59e2f0f755d54b6f235efccfbe103bc4c161649de064e87b4b9ed230e180d2` — FINALIZED
- finalize_case 1: `0xa992ff8af93b974c2b9301dbcc2990e51c84ca7aa05d64fe19f25f487dec32e4` — FINALIZED
- close_case 1 (no reward): `0xd0c72da84e2ff491349b8c04a28fe3523c55c41290abfe7bfcf8cf8955a8a5fb` — FINALIZED
- evaluate_case 2 (attempt 1): `0x860579afe315e2988be4da8b2428e4ff79bd74c21278377620c9931f485169d4` — FINALIZED
- finalize_case 2: `0x0995fc80412d0ac20afa77731352265331d6dfaba40bbf6e157fa6efbc4df212` — FINALIZED
- close_case 2 (no reward): `0xa0c04cb553f1be4cbe7b40c82fdb2c2daf6c630255c848a86f591393a9fc2afc` — FINALIZED
- submit_case 3 (borderline A): `0x28160e5566e4c90adfe84412d1af5887cc20f8d151e0b3c1bb55e773949af177` — FINALIZED
- evaluate_case 3 (first) (attempt 1): `0x5d8d7961d0fd4981b74c0da5cf8983037569f2cf5cfdedb89fa8dd698ef55148` — FINALIZED
- challenge_case 3 (claim SYBIL, 3 GEN): `0xa6dce23010f329e3b68ed1209e9f642c9d2455980fb3971b93e25d749403131f` — FINALIZED
- evaluate_case 3 (second, finalizes) (attempt 1): `0xc8074defedefd2dc13bd9eaa549bd0293557cf227873214c6f4924c035112d4c` — FINALIZED
- close_case 3 (no reward): `0x37cf8d770eced78e5f3613fe88848a932461ffec5f2bc4d49d69e975be9c4e88` — FINALIZED
- submit_case 4 (borderline B): `0x956e135f8be59b9ca2ef25c11e5eb40ad3273d9b1284cde982bd724d8a5b1796` — FINALIZED
- evaluate_case 4 (first) (attempt 1): `0xd079d70e1bc428f875b99c47e785c27bb88fb23b147c1f701d750c075cddeb3c` — FINALIZED
- challenge_case 4 (claim SYBIL, 3 GEN): `0xef9b84355eea62869a443d927ef7680048794dbf438dcf8730a04bb072e55870` — FINALIZED
- evaluate_case 4 (second, finalizes) (attempt 1): `0xcba41503b7b0b94e398ba0d4df7f307ff29d0344ac33b6915081ccf714ddad78` — FINALIZED
- close_case 4 (no reward): `0xa84f977ad54ed32a2690786ee7664f2b15c0e67ebd469931a8818733f703cab1` — FINALIZED
- submit_case 5 (borderline C): `0x88cfcbe2dcd332ba136abdddd513e1bf436a534da5d6e7458ad0594d3699ae85` — FINALIZED
- evaluate_case 5 (first) (attempt 1): `0x95cd0d662321124cea6032e40787272df5a69abc7458ce40887c504daa9215f5` — FINALIZED
- challenge_case 5 (claim UNCERTAIN, 3 GEN): `0xff84c571b88c75cda2f0ddac2a47fdfa9cb96cde30052c862de3208d3f224328` — FINALIZED
- evaluate_case 5 (second, finalizes) (attempt 1): `0xa568ca919897fbcbd31a9a436cd9efd050cb2ee1b96524d460484f91b44a0a65` — FINALIZED
- claim_case_reward 5 (5 GEN credit): `0xac3475e0e2a2984806cbde855965572300165ac2281b58f50fcecafcfaa4694c` — FINALIZED
- withdraw_reward (A): `0x7031c049e81eb4109d3c591fc133c5081784062befbe731459ddf808b1a9a787` — FINALIZED

## Rejected calls (all rejected before any state change; state re-read and confirmed unchanged)

- reject: deposit_funding 0 GEN — rejected at `receipt` (tx `0x640f1d69ffeb9cc136b328b1b4782480049bf3d0159e09dffb534bb6ce175557`)
- reject: submit_case invalid target address — rejected at `receipt` (tx `0x940a4eca40fe58146c2cc4435041ffd3fd7fd813670e5985f0bf2efe9e410920`)
- reject: withdraw_reward with no credit — rejected at `receipt` (tx `0x6fbf4b915cc70100751e6f1f9d110a64ace31a1f6e2ebd448e5eaef85f331f2a`)
- reject: hunter evaluates own case — rejected at `receipt` (tx `0x8fad0e8ac277f9623a17573a7d359602757ae6773252ed391155a314277960af`)
- reject: finalize_case with open challenge — rejected at `receipt` (tx `0x19549fe5bb97a40f68d5273633700bc70084dac79c71fc2905742e60a9e03005`)
- reject: challenge_case with 1 GEN stake (must be 3 GEN) — rejected at `receipt-wait` (tx `0x209665ecbf0e6f53bae35b37f45a30af92374093c8cbf814ccf5544a903928c7`): the receipt could not be parsed client-side (Do not know how to serialize a BigInt), but the call was rejected on-chain: state unchanged, and its 1 GEN stayed in the contract balance and was recovered by the sweep below
- reject: claim_case_reward 0 twice — rejected at `receipt` (tx `0x0b616f25d429b9eac2dc7639a2592e58678c42ebbdcb5137d9bccd32b9e3aa9d`)
- reject: withdraw_reward (B) with no credit — rejected at `receipt` (tx `0xc763a0fb6e4c3b3e75ef7e119ad724ec8afb48c0d015d8b93da3f1f06e226db6`)

## Read-back (via RPC, after the flow)

- Case 0: status `REWARD_PAID`, verdict `SYBIL`, signals `["BURST_ACTIVITY","FRESH_NO_HISTORY","IDENTICAL_TX_PATTERN","SAME_FUNDER"]`, weight `0`, witnesses `1`
- Case 1: status `CLOSED_NO_REWARD`, verdict `HUMAN`, signals `["DIVERSE_COUNTERPARTIES","LONG_HISTORY","UNIQUE_BEHAVIOUR"]`, weight `1000000`, witnesses `0`
- Case 2: status `CLOSED_NO_REWARD`, verdict `UNCERTAIN`, signals `["BURST_ACTIVITY"]`, weight `500000`, witnesses `0`
- Case 3: status `CLOSED_NO_REWARD`, verdict `UNCERTAIN`, signals `["BURST_ACTIVITY","IDENTICAL_TX_PATTERN"]`, weight `500000`, witnesses `1`
- Case 4: status `CLOSED_NO_REWARD`, verdict `UNCERTAIN`, signals `["BURST_ACTIVITY","IDENTICAL_TX_PATTERN"]`, weight `500000`, witnesses `1`
- Case 5: status `REWARD_PAID`, verdict `SYBIL`, signals `["BURST_ACTIVITY","IDENTICAL_TX_PATTERN","SAME_FUNDER"]`, weight `0`, witnesses `1`
- Case 6: status `CLOSED_NO_REWARD`, verdict `UNCERTAIN`, signals `["LONG_HISTORY"]`, weight `500000`, witnesses `1`
- Weights: {"sybil":{"weight_scaled":0,"verdict":"SYBIL","case_id":0},"human":{"weight_scaled":1000000,"verdict":"HUMAN","case_id":1},"thin":{"weight_scaled":500000,"verdict":"UNCERTAIN","case_id":2},"borderA":{"weight_scaled":500000,"verdict":"UNCERTAIN","case_id":3},"borderB":{"weight_scaled":500000,"verdict":"UNCERTAIN","case_id":4},"borderC":{"weight_scaled":0,"verdict":"SYBIL","case_id":5},"borderHuman":{"weight_scaled":500000,"verdict":"UNCERTAIN","case_id":6}}
- Ledger: {"total_received_wei":116000000000000000000,"total_paid_out_wei":10000000000000000000,"funding_pool_wei":106000000000000000000,"challenge_reserved_wei":0,"open_stakes_wei":0,"reward_credits_wei":0,"contract_balance_wei":106000000000000000000,"accounted_wei":106000000000000000000,"stray_wei":0,"invariant_ok":true} (after case 6; before case 6 it was 113 received / 103 pool / 103 balance)
- GEN reconciliation: {"totalReceivedGen":"116","totalPaidOutGen":"10","fundingPoolGen":"106","challengeReservedGen":"0","openStakesGen":"0","rewardCreditsGen":"0","contractBalanceGen":"106","hunterWithdrawnGen":"10","challengerWithdrawnGen":"0","invariantOk":true} (in 116 == out 10 + pool 106; in = 100 funding + 15 stakes (5 challenges x 3 GEN) + 1 swept stray)
- Funding pool: {"funding_pool_wei":106000000000000000000,"hunter_reward_wei":5000000000000000000,"challenge_stake_wei":3000000000000000000,"challenge_success_reward_wei":2000000000000000000}
- Hunter reward credit (after withdraw): {"address":"0xa5abe100cfadb0f2ad07c5a0b88407f985091145","credit_wei":0}
- Challenger reward credit (after withdraw): {"address":"0xa5bc06a5ac0a6ef177a44539c8a9c723d421d2fc","credit_wei":0}
- Hunter stats: {"hunter":"0xa5abe100cfadb0f2ad07c5a0b88407f985091145","cases_submitted":6,"sybil_finalized":2,"rewards_earned_wei":10000000000000000000,"challenges_won":0,"challenges_lost":0,"challenge_rewards_earned_wei":0}
- Challenger stats: {"hunter":"0xa5bc06a5ac0a6ef177a44539c8a9c723d421d2fc","cases_submitted":0,"sybil_finalized":0,"rewards_earned_wei":0,"challenges_won":0,"challenges_lost":4,"challenge_rewards_earned_wei":0}
- Case 6 hunter stats: {"hunter":"0xd9149acffa18ce935db0a4246cb4b4069058dfcd","cases_submitted":1,"sybil_finalized":0,"rewards_earned_wei":0,"challenges_won":0,"challenges_lost":0,"challenge_rewards_earned_wei":0}
- Case 6 challenger stats: {"hunter":"0xca18ecd7bc37778ce5303a1e8d3ca776401c57d8","cases_submitted":0,"sybil_finalized":0,"rewards_earned_wei":0,"challenges_won":0,"challenges_lost":1,"challenge_rewards_earned_wei":0}
- Leaderboard: [{"hunter":"0xa5abe100cfadb0f2ad07c5a0b88407f985091145","cases_submitted":6,"sybil_finalized":2,"rewards_earned_wei":10000000000000000000,"challenges_won":0,"challenges_lost":0,"challenge_rewards_earned_wei":0,"total_rewards_wei":10000000000000000000},{"hunter":"0xa5bc06a5ac0a6ef177a44539c8a9c723d421d2fc","cases_submitted":0,"sybil_finalized":0,"rewards_earned_wei":0,"challenges_won":0,"challenges_lost":4,"challenge_rewards_earned_wei":0,"total_rewards_wei":0}]
- Case count: 7
- Successful challenge on-chain: no — all four attempts on this contract failed to flip (borderline A, B, C sybil-side + human-side case 6); two further attempts on the superseded 0xdc343813A233A43C2Db47Ee9df848e6a583C09CE contract also failed to flip, for six failed attempts in total. See evidence.json borderlineAttempts and flipAttempt6. The CONTRADICTION witness and the 3 GEN refund + 2 GEN challenger reward path are mock-tested only (tests/test_local.py, 319 checks).
- Case 6 (separate sixth flip attempt): submit `0x045985e988fb61f779d368c6e1f00f9d999a1bdd8075b082db1cc213421edf20`, evaluate first `0xc99a8820e242d3e52f34bb848813b36c8ad02d8f35dce2cb1faf2ee90ec05b2e`, challenge `0xfc5a1ee6534c0897ee64170a68781d4a02cdaed28bb47d27e315b533f4e4d420`, evaluate second `0x5e69edec3c7c4ff62b269a60f315ff7857b10ea12939d9f4dd7df67c5eb809d7`, close `0xfc0a20c1ed169c9a94a2d3d149ec01fcf8c6df12a9b21abd6d1afcc39e7c4126` — all FINALIZED; first verdict UNCERTAIN, second UNCERTAIN, no flip; 3 GEN stake forfeited to the pool (pool 103 -> 106 GEN, total received 113 -> 116 GEN).
- Stray GEN swept into the pool: 1 GEN (1000000000000000000 wei)
- Hunter withdrew: true; challenger withdrew: false
- EOA balances (wei): {"funderAfterFundWei":"10000000000000000000000","challengerAfterFundWei":"100000000000000000000","funderAfterDepositWei":"9900000000000000000000","hunterBeforeWithdrawWei":"0","challengerBeforeWithdrawWei":"87000000000000000000","hunterAfterWithdrawWei":"10000000000000000000","hunterAfterWithdrawPlus8sWei":"10000000000000000000","challengerAfterWithdrawWei":"87000000000000000000","challengerAfterWithdrawPlus8sWei":"87000000000000000000","funderFinalWei":"9900000000000000000000"}

Full machine-readable record: `evidence.json` in this repository.
