/* End-to-end on-chain flow against an already-deployed Sybil Hunter contract.
 *
 * Usage:
 *   CONTRACT_ADDRESS=0x... node scripts/flow.mjs
 *   # Accounts are ephemeral and generated for this run only (Studionet is
 *   # gasless). No key is ever written to disk.
 *
 * Flow (minimum txs for full coverage):
 *   A = hunter: claim_demo_funds, submit 3 cases (sybil / human / thin)
 *   B = challenger/evaluator: evaluate case 0 -> SYBIL (pending)
 *   B: challenge case 0, claiming HUMAN
 *   B: evaluate case 0 again -> second evaluation finalizes directly
 *      (expected: SYBIL again, challenge fails, B reputation 100 -> 95)
 *   B: evaluate case 1 -> HUMAN, finalize case 1 -> weight 1000000
 *   B: evaluate case 2 -> UNCERTAIN, finalize case 2 -> weight 500000
 *   A: claim_hunter_reward(0) if case 0 finalized SYBIL -> +500 mGEN
 *   Read back every case, weight, balance, reputation, pool, leaderboard.
 *   Writes evidence.json (tx hashes, FINALIZED status, read-back values)
 *   and docs/live-verification.md.
 *
 * If any evaluate step fails to reach consensus, it is retried up to 4
 * times; a persistent failure stops the run with a clear error instead
 * of recording a success that did not happen.
 */
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createClient, createAccount, generatePrivateKey } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const deployment = JSON.parse(readFileSync(path.join(root, "deployment.json"), "utf-8"));
const address = process.env.CONTRACT_ADDRESS || deployment.contractAddress;
if (!address) throw new Error("No contract address: set CONTRACT_ADDRESS or run deploy first");

const REPO = "xiaoyu7799/sybil-hunter-genlayer";
const ev = (name) =>
  `https://raw.githubusercontent.com/${REPO}/main/evidence/${name}`;

const TARGET_SYBIL = "0x1111111111111111111111111111111111111111";
const TARGET_HUMAN = "0x2222222222222222222222222222222222222222";
const TARGET_THIN = "0x3333333333333333333333333333333333333333";

const hunter = createAccount(generatePrivateKey());
const challenger = createAccount(generatePrivateKey());
console.log("Hunter (A):", hunter.address);
console.log("Challenger/evaluator (B):", challenger.address);
console.log("Contract:", address);

const clientA = createClient({ chain: studionet, account: hunter });
const clientB = createClient({ chain: studionet, account: challenger });

const STATUS_NAMES = { 0: "UNINITIALIZED", 1: "PENDING", 2: "PROPOSING", 3: "COMMITTING", 4: "REVEALING", 5: "ACCEPTED", 6: "UNDETERMINED", 7: "FINALIZED", 8: "CANCELED" };
const txs = [];
function note(label, hash, receipt) {
  const status = receipt.statusName ?? STATUS_NAMES[receipt.status] ?? String(receipt.status ?? "");
  console.log(`${label}: ${hash} -> ${status}`);
  txs.push({ label, txHash: hash, status });
  if (status !== "FINALIZED") throw new Error(`${label} did not FINALIZE (status ${status})`);
}

async function waitFinal(client, hash, label) {
  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.FINALIZED,
    retries: 180,
    interval: 5000,
  });
  note(label, hash, receipt);
  return receipt;
}

async function write(client, functionName, args, label) {
  const hash = await client.writeContract({ address, functionName, args, value: 0n, leaderOnly: false });
  await waitFinal(client, hash, label);
  return hash;
}

async function writeWithRetry(client, functionName, args, label, attempts = 4) {
  let lastErr = null;
  for (let i = 1; i <= attempts; i++) {
    try {
      return await write(client, functionName, args, `${label} (attempt ${i})`);
    } catch (err) {
      lastErr = err;
      console.log(`${label} attempt ${i} failed: ${String(err?.message ?? err).slice(0, 300)}`);
      if (i < attempts) await new Promise((r) => setTimeout(r, 10000));
    }
  }
  throw new Error(`${label} failed after ${attempts} attempts: ${String(lastErr?.message ?? lastErr)}`);
}

async function read(client, functionName, args) {
  const raw = await client.readContract({ address, functionName, args });
  if (typeof raw === "string") {
    try { return JSON.parse(raw); } catch { return raw; }
  }
  return raw;
}

// --- 1. Hunter claims demo funds (once): 10000 simulated mGEN.
await write(clientA, "claim_demo_funds", [], "claim_demo_funds (A)");
const balanceAfterFaucet = await read(clientA, "get_balance", [hunter.address]);
console.log("A balance after faucet:", JSON.stringify(balanceAfterFaucet));

// --- 2. Hunter submits 3 cases.
await write(clientA, "submit_case", [TARGET_SYBIL, ev("case-sybil-evidence.json"), "Cluster candidate: shared funder, identical pattern, burst, fresh."], "submit_case 0 (sybil)");
await write(clientA, "submit_case", [TARGET_HUMAN, ev("case-human-evidence.json"), "Established user: long history, diverse counterparties."], "submit_case 1 (human)");
await write(clientA, "submit_case", [TARGET_THIN, ev("case-thin-evidence.json"), "Thin evidence: burst activity only, nothing else observed."], "submit_case 2 (thin)");

// --- 3. Case 0: evaluate -> pending SYBIL (expected).
await writeWithRetry(clientB, "evaluate_case", [0n], "evaluate_case 0 (first)");
const case0eval1 = await read(clientB, "get_case", [0n]);
console.log("Case 0 after first evaluation:", JSON.stringify(case0eval1));

// --- 4. Case 0: challenge, claiming HUMAN.
await write(clientB, "challenge_case", [0n, "LONG_HISTORY,DIVERSE_COUNTERPARTIES", "HUMAN"], "challenge_case 0 (claim HUMAN)");
const case0challenged = await read(clientB, "get_case", [0n]);
console.log("Case 0 after challenge:", JSON.stringify(case0challenged));

// --- 5. Case 0: second evaluation finalizes directly.
await writeWithRetry(clientB, "evaluate_case", [0n], "evaluate_case 0 (second, finalizes)");
const case0final = await read(clientB, "get_case", [0n]);
console.log("Case 0 finalized:", JSON.stringify(case0final));

// --- 6. Case 1: evaluate -> HUMAN, finalize -> weight 1000000.
await writeWithRetry(clientB, "evaluate_case", [1n], "evaluate_case 1");
const case1eval = await read(clientB, "get_case", [1n]);
console.log("Case 1 after evaluation:", JSON.stringify(case1eval));
await write(clientB, "finalize_case", [1n], "finalize_case 1");

// --- 7. Case 2: evaluate -> UNCERTAIN, finalize -> weight 500000.
await writeWithRetry(clientB, "evaluate_case", [2n], "evaluate_case 2");
const case2eval = await read(clientB, "get_case", [2n]);
console.log("Case 2 after evaluation:", JSON.stringify(case2eval));
await write(clientB, "finalize_case", [2n], "finalize_case 2");

// --- 8. Hunter reward (only if case 0 finalized SYBIL).
let rewardClaimed = false;
if (case0final.final_verdict === "SYBIL") {
  await write(clientA, "claim_hunter_reward", [0n], "claim_hunter_reward 0");
  rewardClaimed = true;
} else {
  console.log("Case 0 did not finalize SYBIL; skipping reward claim (recorded honestly).");
}

// --- 9. Read back everything.
const case0 = await read(clientA, "get_case", [0n]);
const case1 = await read(clientA, "get_case", [1n]);
const case2 = await read(clientA, "get_case", [2n]);
const weightSybil = await read(clientA, "get_weight", [TARGET_SYBIL]);
const weightHuman = await read(clientA, "get_weight", [TARGET_HUMAN]);
const weightThin = await read(clientA, "get_weight", [TARGET_THIN]);
const balanceA = await read(clientA, "get_balance", [hunter.address]);
const repB = await read(clientA, "get_reputation", [challenger.address]);
const pool = await read(clientA, "get_pool", []);
const leaderboard = await read(clientA, "get_leaderboard", [10n]);
const count = await read(clientA, "get_case_count", []);

console.log("Final read-back:");
console.log(" case0:", JSON.stringify(case0));
console.log(" case1:", JSON.stringify(case1));
console.log(" case2:", JSON.stringify(case2));
console.log(" weights:", JSON.stringify({ weightSybil, weightHuman, weightThin }));
console.log(" balanceA:", JSON.stringify(balanceA));
console.log(" repB:", JSON.stringify(repB));
console.log(" pool:", JSON.stringify(pool));
console.log(" leaderboard:", JSON.stringify(leaderboard));
console.log(" count:", JSON.stringify(count));

const evidence = {
  network: "Stable Studionet",
  chainId: 61999,
  rpcUrl: "https://studio.genlayer.com/api",
  contractAddress: address,
  explorer: `https://explorer-studio.genlayer.com/address/${address}`,
  hunter: hunter.address,
  challenger: challenger.address,
  targets: { sybil: TARGET_SYBIL, human: TARGET_HUMAN, thin: TARGET_THIN },
  transactions: txs,
  cases: { case0, case1, case2 },
  weights: { sybil: weightSybil, human: weightHuman, thin: weightThin },
  balanceHunter: balanceA,
  reputationChallenger: repB,
  rewardPool: pool,
  leaderboard,
  caseCount: count,
  rewardClaimed,
  checkedAt: new Date().toISOString(),
};
writeFileSync(path.join(root, "evidence.json"), JSON.stringify(evidence, null, 2) + "\n");
console.log("Wrote evidence.json");

const lines = [
  "# Live verification",
  "",
  "Network: Stable Studionet (chain 61999). Contract: `" + address + "`",
  "Explorer: https://explorer-studio.genlayer.com/address/" + address,
  "Checked at: " + evidence.checkedAt,
  "",
  "## Transactions (all FINALIZED)",
  "",
  ...txs.map((t) => `- ${t.label}: \`${t.txHash}\` — ${t.status}`),
  "",
  "## Read-back (via RPC, after the flow)",
  "",
  "- Case 0: status `" + case0.status + "`, verdict `" + case0.final_verdict + "`, signals `" + JSON.stringify(case0.final_signals) + "`, weight `" + case0.final_weight_scaled + "`, witnesses `" + case0.witnesses.length + "`",
  "- Case 1: status `" + case1.status + "`, verdict `" + case1.final_verdict + "`, signals `" + JSON.stringify(case1.final_signals) + "`, weight `" + case1.final_weight_scaled + "`",
  "- Case 2: status `" + case2.status + "`, verdict `" + case2.final_verdict + "`, signals `" + JSON.stringify(case2.final_signals) + "`, weight `" + case2.final_weight_scaled + "`",
  "- Weights: sybil target `" + JSON.stringify(weightSybil) + "`, human target `" + JSON.stringify(weightHuman) + "`, thin target `" + JSON.stringify(weightThin) + "`",
  "- Hunter balance: `" + JSON.stringify(balanceA) + "`; reward claimed: `" + rewardClaimed + "`",
  "- Challenger reputation: `" + JSON.stringify(repB) + "`",
  "- Reward pool: `" + JSON.stringify(pool) + "`",
  "- Leaderboard: `" + JSON.stringify(leaderboard) + "`",
  "- Case count: `" + JSON.stringify(count) + "`",
  "",
  "Full machine-readable record: `evidence.json` in this repository.",
  "",
];
writeFileSync(path.join(root, "docs", "live-verification.md"), lines.join("\n"));
console.log("Wrote docs/live-verification.md");
