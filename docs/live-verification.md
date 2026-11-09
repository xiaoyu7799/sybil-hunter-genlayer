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
- Successful challenge on-chain: no — fourteen flip attempts in total (six before this section plus eight new attempts F1–F8, cases 7–14, below) all failed to flip. The CONTRADICTION witness and the 3 GEN refund + 2 GEN challenger reward path are mock-tested only (tests/test_local.py, 319 checks).
- Case 6 (separate sixth flip attempt): submit `0x045985e988fb61f779d368c6e1f00f9d999a1bdd8075b082db1cc213421edf20`, evaluate first `0xc99a8820e242d3e52f34bb848813b36c8ad02d8f35dce2cb1faf2ee90ec05b2e`, challenge `0xfc5a1ee6534c0897ee64170a68781d4a02cdaed28bb47d27e315b533f4e4d420`, evaluate second `0x5e69edec3c7c4ff62b269a60f315ff7857b10ea12939d9f4dd7df67c5eb809d7`, close `0xfc0a20c1ed169c9a94a2d3d149ec01fcf8c6df12a9b21abd6d1afcc39e7c4126` — all FINALIZED; first verdict UNCERTAIN, second UNCERTAIN, no flip; 3 GEN stake forfeited to the pool (pool 103 -> 106 GEN, total received 113 -> 116 GEN).
- Stray GEN swept into the pool: 1 GEN (1000000000000000000 wei)
- Hunter withdrew: true; challenger withdrew: false
- EOA balances (wei): {"funderAfterFundWei":"10000000000000000000000","challengerAfterFundWei":"100000000000000000000","funderAfterDepositWei":"9900000000000000000000","hunterBeforeWithdrawWei":"0","challengerBeforeWithdrawWei":"87000000000000000000","hunterAfterWithdrawWei":"10000000000000000000","hunterAfterWithdrawPlus8sWei":"10000000000000000000","challengerAfterWithdrawWei":"87000000000000000000","challengerAfterWithdrawPlus8sWei":"87000000000000000000","funderFinalWei":"9900000000000000000000"}

Full machine-readable record: `evidence.json` in this repository.

## Flip attempts F1–F8 (cases 7–14, 2026-11-09)

Eight further systematic attempts to produce a CONTRADICTION witness on-chain, each with a distinct hypothesis. None flipped. Every evaluation round passed consensus on the first try (zero retries in 16 rounds); both rounds of each attempt returned the identical signal set.

- F1, case 7 (target `0x8888…`): BURST count threshold — 9 tx in 55 min; clear SAME_FUNDER + IDENTICAL. First SYBIL `[BURST_ACTIVITY, IDENTICAL_TX_PATTERN, SAME_FUNDER]`, second SYBIL, same signals. Txs: submit `0x531fb6b567588d63e6929918ef21bb06632a767c3c4e7d6670dac96d0061ebd1`, eval1 `0xafb3a9f49e9a5c4ee5b5962152439f218b309186ff44c76263a9e8cae4d6f87a`, challenge `0xf192b74f705d41be22a3115ab768b491ab3e15898fea65e760fe7e628f74f071`, eval2 `0x93062912a6782362035d4f65b76f228f4ff1907a982fae4e5ea3603baadcf5d4`, claim `0x2c1f587c1df859a328de18d9708f7cd3daf7411c050e37420d58dd02d150df7d`, withdraw `0xdaff4d1ed386e3680e3a51884a9717617c9a19731d49c16653e0d39ac038291d`. Hunter 5 GEN withdrawn.
- F2, case 8 (target `0x9999…`): FRESH age threshold — first tx 6 weeks ago; clear SAME_FUNDER + IDENTICAL. First SYBIL `[FRESH_NO_HISTORY, IDENTICAL_TX_PATTERN, SAME_FUNDER]`, second SYBIL, same signals. Txs: submit `0x87e45abe8fef4dc9fc136b580af34664d09737f4a1cd66d5b0f4f1592e767b6f`, eval1 `0x55228cd4a2a078c0f327bff06075a6fa5e499704caefbd3d21518f42579a6f68`, challenge `0x478fc2f0ae99b4c12da0442a8cf43776bca275bcfb87c0c11949605a5e9a1c78`, eval2 `0x122dfa0281681ea44e34282db906290e907cfe046a8e7fa0f5ba0522e5148e6b`, claim `0xc5caea66df45113a08dae5b8f80d93d06a846c54a819870d7b0181c132120ad4`, withdraw `0xe9993a03baae3a509d048e1e22f79b0827bb5701997a6079b37f43c96ab97395`. Hunter 5 GEN withdrawn.
- F3, case 9 (target `0xAAAA…`): LONG_HISTORY age threshold — first tx 8 months ago; clear DIVERSE, 186 counterparties. First HUMAN `[DIVERSE_COUNTERPARTIES, LONG_HISTORY]`, second HUMAN, same signals. Txs: submit `0xb1eaf33d7fe7d11ce05c1cb514102299ac29fb2c526e27412c1d63e467890bae`, eval1 `0x377732ced945dce1b4be14c65d6a01770d2d059490df17b30433c3799f67cafc`, challenge `0xd07c6af544daa37d8ad701da5a9a9fa0fcf9f01f0ef1f7337c04244226afe2a2`, eval2 `0x252c0d1c572e9e7d61f2ec2c0915fd8de89d7464a47273b22c8c8782689c7323`, close `0xd4026a6ad41f0c1f8e1109be95bebda10d04d9c2048e9a789df5642089217354`.
- F4, case 10 (target `0xBBBB…`): DIVERSE count threshold — 11 distinct counterparties; clear LONG_HISTORY since March 2023. First HUMAN `[DIVERSE_COUNTERPARTIES, LONG_HISTORY]`, second HUMAN, same signals. Txs: submit `0xa0dcb6ce8768352e4741619351d6fe948d882e3f92236674bd22b3207732d40d`, eval1 `0x1aa07e5f7aa7f2ce4993e1d078d300681823933faf8c18ae2bac311e0329941c`, challenge `0x5e21e031aa0e9d75009363924ea6290f6956d7b7312ad50cba2762c4d4a5cc81`, eval2 `0x40379be462bd7260294276c58e1d9c670bfae3458c088fe6eb9d9f26b7afde35`, close `0x20bdb7cee7b9467fc6fc581c7062080948a13d68669d4312718cdee15ae3fa62`.
- F5, case 11 (target `0xCCCC…`): UNIQUE_BEHAVIOUR intrusion — 3 clear sybil signals plus amounts varied 0.8–1.4 ETH across 3 contracts. First UNCERTAIN `[BURST_ACTIVITY, IDENTICAL_TX_PATTERN, SAME_FUNDER, UNIQUE_BEHAVIOUR]`, second UNCERTAIN, same signals. Txs: submit `0xdc47ea1679d25d753e82965cdb40a7a88e3b1fee9b11cf12806568a548215eb3`, eval1 `0x18636f66225809b0929c27a24adbeaebf60157ee542a3e252779f11c7d7d5164`, challenge `0x3b8a1f05bfac3990a8957847871161559196e3c2872cca8cdf40f06ef6446074`, eval2 `0x946411a5571eda703a848e0394d7c243749aefd0bec7306f2f30b1f19f3c0054`, close `0x6c45988121b9037d5f7d1cd3b73e45e8cbcfcdc75da18f243789ff12cce0daee`.
- F6, case 12 (target `0xDDDD…`): VERIFIED_ACTIVITY via ENS — address controls ENS name `marisol-trades.eth`, registered 2024, listed on the owner's public profile; clear LONG_HISTORY since March 2023. First HUMAN `[LONG_HISTORY, VERIFIED_ACTIVITY]`, second HUMAN, same signals. Txs: submit `0xec2df239c64494312b550b551d34d799fd88f3edfdb7b5b7dc434732b5e35688`, eval1 `0x305b1f5faec8c53d482c12d05d0efc9e6cc8cc61554f9d048c5938576b166a65`, challenge `0x15181377f519f28b6b08737bc15af9315b34f803f1ff23fd9b114a39288cf40f`, eval2 `0x020e95072a747c801bafb834a82993efc78ca93da348d053a1d8f4b9fa5a9443`, close `0x914aaf75ebc7a7e9dd840d4231bbd4999c8f52e0bd7a5cbdf31de1747c2d0545`.
- F7, case 13 (target `0xEEEE…`): SAME_FUNDER scope — funded by a centralised exchange hot wallet that also funded 12,000+ addresses; clear IDENTICAL + BURST 44 tx/80 min. First SYBIL `[BURST_ACTIVITY, IDENTICAL_TX_PATTERN, SAME_FUNDER]`, second SYBIL, same signals. Txs: submit `0xfd43d372b71c2cb2a03f87fe68ab8512f2161ff77d06823ab15c622171ef91ed`, eval1 `0xb99a6766ef11158f0048d4f59a75c7c8e203bdd640608112d84657170840352f`, challenge `0x7eb5ce3a66dcfd0c551ca1e7b43f2ea5bccfeabbc6ba0e0fb0b9b5b2efc38a07`, eval2 `0x33d6510ba6fe1c5c9ff73ee342d8e9b0a5fd4356683aff5bd1f409ee85a64d1c`, claim `0x59ff9c4d776cda4391b2a314b6660a0ec2384f988db19ff5838cf3d24ed5c4a6`, withdraw `0x9e6bf23c2a66edd28835099853f5ee169f5963f6b726c3f7da2093e25609888d`. Hunter 5 GEN withdrawn.
- F8, case 14 (target `0xFFFF…`): IDENTICAL similarity boundary — same three amounts/order/contract, with 1 of 12 transactions differing in amount by 2%; clear SAME_FUNDER + BURST 41 tx/75 min. First SYBIL `[BURST_ACTIVITY, IDENTICAL_TX_PATTERN, SAME_FUNDER]`, second SYBIL, same signals. Txs: submit `0x3b211a5fd5dbefb22a9c31ec5985bd024119619e2e5c1d6de5f0db022bbbadee`, eval1 `0x3c47604a625b03ed5c1eb479a10c074a4f1e2e343e5d13b18df3f7abcac07e25`, challenge `0x0ee1b04bba3f317bfb54d31f0c04538b4331723eb75e0e7bacb25d6981114e4b`, eval2 `0x10cc048c64b6cd0470f53446e4b7025a3db13a32b021a0a6954dfd53984227f3`, claim `0x8e2f41ed62feae4a7138a7505d59026ccadaeabd6929ce5daddf01c73781c259`, withdraw `0xda844393a94154ae5482d47a1a69dc5c3441a59f7e113441ee35498aa507088e`. Hunter 5 GEN withdrawn.

All eight challenge txs FINALIZED. Each attempt used fresh temporary hunter/challenger accounts; no keys were written to disk.

## Final ledger (live-read after case 14)

- Ledger: `{"total_received_wei":140000000000000000000,"total_paid_out_wei":30000000000000000000,"funding_pool_wei":110000000000000000000,"challenge_reserved_wei":0,"open_stakes_wei":0,"reward_credits_wei":0,"contract_balance_wei":110000000000000000000,"accounted_wei":110000000000000000000,"stray_wei":0,"invariant_ok":true}` — in 140 GEN = out 30 GEN (6 SYBIL hunter rewards × 5 GEN) + pool 110 GEN; in = 100 GEN funding + 24 GEN failed-challenge stakes (8 × 3 GEN) + 15 GEN earlier stakes + 1 GEN swept stray. No open stakes, reserves or credits remain; all 15 cases closed.
- Case count: 15. Successful challenge on-chain: no (`successChallengeOnChain: null` in evidence.json).

## Why the flip route is closed

A challenge submits no new evidence, and the second evaluation re-fetches the same evidence URL with the same prompt. Across 14 attempts and 28 evaluation rounds, both rounds returned the same signal set every time: numeric thresholds (9 tx/55 min, 6 weeks, 8 months, 11 counterparties) counted in both rounds; definitional disputes (ENS as verified identity, exchange hot wallet as same funder, varied amounts alongside a cloned sequence, 11/12 matching transactions) resolved identically in both rounds; mixed signals (cloned sequence plus varied amounts) counted together in both rounds. The judge is deterministic for explicitly stated facts, so a flip would require sampling variance that did not appear in any round. This is a property of the mechanism, not a matter of trying too few cases.

A new Intelligent Contract was built to fill this Intelligent Contract slot; this repository is preserved as-is and the successful-challenge branch of this contract remains unexercised on-chain.
