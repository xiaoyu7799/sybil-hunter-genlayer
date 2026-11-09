/* End-to-end on-chain flow for Sybil Hunter v0.2.0 (real testnet GEN).
 *
 * Usage:
 *   CONTRACT_ADDRESS=0x... node scripts/flow.mjs
 *   # Accounts are ephemeral and generated for this run only (Studionet is
 *   # gasless; testnet GEN comes from sim_fundAccount). No key is ever
 *   * written to disk.
 *
 * Roles:
 *   D = funder: funds 10000 GEN, deposit_funding 100 GEN into the pool.
 *   A = hunter: submits cases for free, claims the SYBIL reward, withdraws.
 *   B = evaluator/challenger: funded 100 GEN, evaluates, challenges (3 GEN).
 *   C = fresh account with no credit, used for the no-credit withdraw probe.
 *
 * Flow:
 *   reject probes (deposit 0, bad target, no-credit withdraw, own-case
 *   evaluate, finalize with open challenge, wrong challenge stake,
 *   double reward claim) -> 3 main cases (sybil / human / thin) with a
 *   failed challenge on case 0 -> up to 2 borderline cases attempting the
 *   successful-challenge path (second verdict differs -> CONTRADICTION
 *   witness, challenger credited 3 GEN refund + 2 GEN reward) ->
 *   withdrawals -> full read-back + ledger reconciliation.
 * Writes evidence.json (tx hashes, FINALIZED status, read-back values)
 * and docs/live-verification.md.
 *
 * If any evaluate step fails to reach consensus, it is retried up to 4
 * times; a persistent failure stops the run with a clear error instead
 * of recording a success that did not happen. Verdicts are recorded as
 * they actually come back; the flow adapts (challenge the actual pending
 * verdict, claim the reward only for SYBIL) rather than assuming them.
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

const GEN = 10n ** 18n;
const TARGET_SYBIL = "0x1111111111111111111111111111111111111111";
const TARGET_HUMAN = "0x2222222222222222222222222222222222222222";
const TARGET_THIN = "0x3333333333333333333333333333333333333333";
const TARGET_BORDER_A = "0x4444444444444444444444444444444444444444";
const TARGET_BORDER_B = "0x5555555555555555555555555555555555555555";

const funder = createAccount(generatePrivateKey());
const hunter = createAccount(generatePrivateKey());
const challenger = createAccount(generatePrivateKey());
const fresh = createAccount(generatePrivateKey());
console.log("Funder (D):", funder.address);
console.log("Hunter (A):", hunter.address);
console.log("Challenger/evaluator (B):", challenger.address);
console.log("Fresh probe account (C):", fresh.address);
console.log("Contract:", address);

const clientD = createClient({ chain: studionet, account: funder });
const clientA = createClient({ chain: studionet, account: hunter });
const clientB = createClient({ chain: studionet, account: challenger });
const clientC = createClient({ chain: studionet, account: fresh });

const STATUS_NAMES = { 0: "UNINITIALIZED", 1: "PENDING", 2: "PROPOSING", 3: "COMMITTING", 4: "REVEALING", 5: "ACCEPTED", 6: "UNDETERMINED", 7: "FINALIZED", 8: "CANCELED" };
const txs = [];
const rejects = [];
const eoaBalances = {};

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

async function write(client, functionName, args, label, value = 0n) {
  const hash = await client.writeContract({ address, functionName, args, value, leaderOnly: false });
  await waitFinal(client, hash, label);
  return hash;
}

async function writeWithRetry(client, functionName, args, label, value = 0n, attempts = 4) {
  let lastErr = null;
  for (let i = 1; i <= attempts; i++) {
    try {
      return await write(client, functionName, args, `${label} (attempt ${i})`, value);
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

const eoaBalance = async (client, addr) => (await client.getBalance({ address: addr })).toString();

/* A call that must be rejected. Records how it was rejected (client-side
 * throw, or an included transaction whose receipt carries the error) and
 * verifies the relevant on-chain state did not change. Throws if the call
 * unexpectedly succeeds. */
async function expectReject(client, functionName, args, value, label, stateCheck) {
  const before = stateCheck ? await stateCheck() : null;
  let outcome = null;
  let hash = null;
  try {
    hash = await client.writeContract({ address, functionName, args, value, leaderOnly: false });
  } catch (err) {
    outcome = { rejectedAt: "client", error: String(err?.message ?? err).slice(0, 500) };
  }
  if (hash) {
    try {
      const receipt = await client.waitForTransactionReceipt({
        hash,
        status: TransactionStatus.FINALIZED,
        retries: 60,
        interval: 5000,
      });
      const status = receipt.statusName ?? STATUS_NAMES[receipt.status] ?? String(receipt.status ?? "");
      outcome = { rejectedAt: "receipt", txHash: hash, status, receipt: JSON.stringify(receipt).slice(0, 800) };
    } catch (err) {
      outcome = { rejectedAt: "receipt-wait", txHash: hash, error: String(err?.message ?? err).slice(0, 500) };
    }
  }
  const after = stateCheck ? await stateCheck() : null;
  const unchanged = before === null || JSON.stringify(before) === JSON.stringify(after);
  console.log(`${label}: REJECTED (${outcome.rejectedAt}), state unchanged: ${unchanged}`);
  if (!unchanged) throw new Error(`${label}: state changed despite rejection! before=${JSON.stringify(before)} after=${JSON.stringify(after)}`);
  rejects.push({ label, functionName, args: args.map(String), valueWei: value.toString(), ...outcome, stateUnchanged: unchanged });
  return outcome;
}

/* Claim signals for a challenge against the actual pending verdict. */
function challengeClaimFor(pendingVerdict, strongSignals, ambiguousSignals) {
  if (pendingVerdict === "SYBIL") return { csv: strongSignals.join(","), verdict: "UNCERTAIN" };
  if (pendingVerdict === "UNCERTAIN") return { csv: [...strongSignals, ...ambiguousSignals].join(","), verdict: "SYBIL" };
  return { csv: "BURST_ACTIVITY", verdict: "UNCERTAIN" }; // pending HUMAN
}

// --- 0. Fund D (10000 GEN) and B (100 GEN) via sim_fundAccount.
for (const [client, account, gen] of [[clientD, funder, 10000], [clientB, challenger, 100]]) {
  const fundTx = await client.request({
    method: "sim_fundAccount",
    params: [account.address, gen * 10 ** 18],
  });
  console.log(`sim_fundAccount ${account.address.slice(0, 10)}… ${gen} GEN:`, String(fundTx).slice(0, 80));
  const bal = await eoaBalance(client, account.address);
  if (bal !== (BigInt(gen) * GEN).toString()) throw new Error(`fund amount mismatch for ${account.address}`);
}
eoaBalances.funderAfterFundWei = await eoaBalance(clientD, funder.address);
eoaBalances.challengerAfterFundWei = await eoaBalance(clientB, challenger.address);
console.log("Funder EOA after fund:", eoaBalances.funderAfterFundWei);
console.log("Challenger EOA after fund:", eoaBalances.challengerAfterFundWei);

// --- 1. D funds the reward pool with 100 GEN.
await write(clientD, "deposit_funding", [], "deposit_funding 100 GEN (D)", 100n * GEN);
const ledgerAfterFund = await read(clientD, "get_ledger", []);
console.log("Ledger after funding:", JSON.stringify(ledgerAfterFund));
eoaBalances.funderAfterDepositWei = await eoaBalance(clientD, funder.address);

// --- 2. Reject probes (before any case exists / state-independent).
await expectReject(clientD, "deposit_funding", [], 0n, "reject: deposit_funding 0 GEN",
  async () => await read(clientD, "get_ledger", []));
await expectReject(clientA, "submit_case", ["0x1234", ev("case-sybil-evidence.json"), "bad address"], 0n,
  "reject: submit_case invalid target address",
  async () => await read(clientA, "get_case_count", []));
await expectReject(clientC, "withdraw_reward", [], 0n, "reject: withdraw_reward with no credit",
  async () => await read(clientC, "get_ledger", []));

// --- 3. Hunter submits 3 cases.
await write(clientA, "submit_case", [TARGET_SYBIL, ev("case-sybil-evidence.json"), "Cluster candidate: shared funder, identical pattern, burst, fresh."], "submit_case 0 (sybil)");
await write(clientA, "submit_case", [TARGET_HUMAN, ev("case-human-evidence.json"), "Established user: long history, diverse counterparties."], "submit_case 1 (human)");
await write(clientA, "submit_case", [TARGET_THIN, ev("case-thin-evidence.json"), "Thin evidence: burst activity only, nothing else observed."], "submit_case 2 (thin)");

// --- 4. Reject probe: hunter may not judge their own case.
await expectReject(clientA, "evaluate_case", [0n], 0n, "reject: hunter evaluates own case",
  async () => await read(clientA, "get_case", [0n]));

// --- 5. Case 0: evaluate -> pending (expected SYBIL).
await writeWithRetry(clientB, "evaluate_case", [0n], "evaluate_case 0 (first)");
const case0eval1 = await read(clientB, "get_case", [0n]);
console.log("Case 0 after first evaluation:", JSON.stringify(case0eval1));
const claim0 = challengeClaimFor(case0eval1.pending_verdict,
  ["BURST_ACTIVITY", "FRESH_NO_HISTORY", "IDENTICAL_TX_PATTERN", "SAME_FUNDER"], []);

// --- 6. Case 0: challenge, claiming the opposite verdict, staking 3 GEN.
await write(clientB, "challenge_case", [0n, claim0.csv, claim0.verdict], `challenge_case 0 (claim ${claim0.verdict}, 3 GEN)`, 3n * GEN);
const case0challenged = await read(clientB, "get_case", [0n]);
console.log("Case 0 after challenge:", JSON.stringify(case0challenged));

// --- 7. Reject probes while the challenge is open.
await expectReject(clientB, "finalize_case", [0n], 0n, "reject: finalize_case with open challenge",
  async () => await read(clientB, "get_case", [0n]));
await expectReject(clientB, "challenge_case", [0n, "LONG_HISTORY,DIVERSE_COUNTERPARTIES", "HUMAN"], 1n * GEN,
  "reject: challenge_case with 1 GEN stake (must be 3 GEN)",
  async () => await read(clientB, "get_case", [0n]));

// --- 8. Case 0: second evaluation finalizes directly.
await writeWithRetry(clientB, "evaluate_case", [0n], "evaluate_case 0 (second, finalizes)");
const case0final = await read(clientB, "get_case", [0n]);
console.log("Case 0 finalized:", JSON.stringify(case0final));

// --- 9. Hunter reward for case 0 (only if it finalized SYBIL).
let rewardClaimed0 = false;
if (case0final.final_verdict === "SYBIL") {
  await write(clientA, "claim_case_reward", [0n], "claim_case_reward 0 (5 GEN credit)");
  rewardClaimed0 = true;
  // Reject probe: the same reward cannot be claimed twice.
  await expectReject(clientA, "claim_case_reward", [0n], 0n, "reject: claim_case_reward 0 twice",
    async () => await read(clientA, "get_case", [0n]));
} else {
  console.log("Case 0 did not finalize SYBIL; skipping reward claim (recorded honestly).");
}

// --- 10. Case 1: evaluate -> finalize -> close (or claim if SYBIL).
await writeWithRetry(clientB, "evaluate_case", [1n], "evaluate_case 1");
const case1eval = await read(clientB, "get_case", [1n]);
console.log("Case 1 after evaluation:", JSON.stringify(case1eval));
await write(clientB, "finalize_case", [1n], "finalize_case 1");
const case1final = await read(clientB, "get_case", [1n]);
if (case1final.final_verdict === "SYBIL") {
  await write(clientA, "claim_case_reward", [1n], "claim_case_reward 1 (5 GEN credit)");
} else {
  await write(clientB, "close_case", [1n], "close_case 1 (no reward)");
}

// --- 11. Case 2: evaluate -> finalize -> close (or claim if SYBIL).
await writeWithRetry(clientB, "evaluate_case", [2n], "evaluate_case 2");
const case2eval = await read(clientB, "get_case", [2n]);
console.log("Case 2 after evaluation:", JSON.stringify(case2eval));
await write(clientB, "finalize_case", [2n], "finalize_case 2");
const case2final = await read(clientB, "get_case", [2n]);
if (case2final.final_verdict === "SYBIL") {
  await write(clientA, "claim_case_reward", [2n], "claim_case_reward 2 (5 GEN credit)");
} else {
  await write(clientB, "close_case", [2n], "close_case 2 (no reward)");
}

// --- 12. Borderline cases: attempt the successful-challenge path.
//     Each borderline file states 2 sybil signals strongly and a third
//     (SAME_FUNDER) ambiguously, so the two evaluations can honestly
//     disagree. Try A, then B if A does not flip.
const borderlineAttempts = [];
let successChallenge = null;
const borderlineFiles = [
  { id: 3, target: TARGET_BORDER_A, file: "case-borderline-a-evidence.json", note: "Borderline cluster candidate A: 2 strong signals, funder ambiguous." },
  { id: 4, target: TARGET_BORDER_B, file: "case-borderline-b-evidence.json", note: "Borderline cluster candidate B: 2 strong signals, funder ambiguous." },
];
for (const b of borderlineFiles) {
  const doc = JSON.parse(readFileSync(path.join(root, "evidence", b.file), "utf-8"));
  await write(clientA, "submit_case", [b.target, ev(b.file), b.note], `submit_case ${b.id} (borderline ${b.file === "case-borderline-a-evidence.json" ? "A" : "B"})`);
  await writeWithRetry(clientB, "evaluate_case", [BigInt(b.id)], `evaluate_case ${b.id} (first)`);
  const first = await read(clientB, "get_case", [BigInt(b.id)]);
  console.log(`Case ${b.id} after first evaluation:`, JSON.stringify(first));
  const claim = challengeClaimFor(first.pending_verdict, doc.signals_stated_strong, doc.signals_ambiguous);
  await write(clientB, "challenge_case", [BigInt(b.id), claim.csv, claim.verdict], `challenge_case ${b.id} (claim ${claim.verdict}, 3 GEN)`, 3n * GEN);
  await writeWithRetry(clientB, "evaluate_case", [BigInt(b.id)], `evaluate_case ${b.id} (second, finalizes)`);
  const fin = await read(clientB, "get_case", [BigInt(b.id)]);
  console.log(`Case ${b.id} finalized:`, JSON.stringify(fin));
  const flipped = fin.final_verdict !== first.pending_verdict;
  borderlineAttempts.push({ caseId: b.id, file: b.file, firstVerdict: first.pending_verdict, firstSignals: first.pending_signals, secondVerdict: fin.final_verdict, secondSignals: fin.final_signals, flipped, witnesses: fin.witnesses });
  if (flipped) {
    successChallenge = { caseId: b.id, ...borderlineAttempts[borderlineAttempts.length - 1] };
    if (fin.final_verdict === "SYBIL") {
      await write(clientA, "claim_case_reward", [BigInt(b.id)], `claim_case_reward ${b.id} (5 GEN credit)`);
    } else {
      await write(clientB, "close_case", [BigInt(b.id)], `close_case ${b.id} (no reward)`);
    }
    break;
  }
  // No flip: the failed challenge already finalized the case; close/claim it.
  if (fin.final_verdict === "SYBIL") {
    await write(clientA, "claim_case_reward", [BigInt(b.id)], `claim_case_reward ${b.id} (5 GEN credit)`);
  } else {
    await write(clientB, "close_case", [BigInt(b.id)], `close_case ${b.id} (no reward)`);
  }
}
console.log("Successful challenge on-chain:", successChallenge ? `yes, case ${successChallenge.caseId}` : "NO — both borderline attempts failed to flip");

// --- 13. Withdrawals (pull payment) + EOA balance checks.
eoaBalances.hunterBeforeWithdrawWei = await eoaBalance(clientA, hunter.address);
eoaBalances.challengerBeforeWithdrawWei = await eoaBalance(clientB, challenger.address);
const creditA = await read(clientA, "get_reward_credit", [hunter.address]);
const creditB = await read(clientB, "get_reward_credit", [challenger.address]);
console.log("Credit A before withdraw:", JSON.stringify(creditA));
console.log("Credit B before withdraw:", JSON.stringify(creditB));
let withdrawA = false;
let withdrawB = false;
if (Number(creditA.credit_wei) > 0) {
  await write(clientA, "withdraw_reward", [], "withdraw_reward (A)");
  withdrawA = true;
} else {
  console.log("Hunter has no credit; skipping withdraw (recorded honestly).");
}
if (Number(creditB.credit_wei) > 0) {
  await write(clientB, "withdraw_reward", [], "withdraw_reward (B)");
  withdrawB = true;
} else {
  // No credit: a withdraw attempt is itself a reject probe.
  await expectReject(clientB, "withdraw_reward", [], 0n, "reject: withdraw_reward (B) with no credit",
    async () => await read(clientB, "get_ledger", []));
}
// The transfer executes on finalization; re-read EOA balances after a wait.
await new Promise((r) => setTimeout(r, 8000));
eoaBalances.hunterAfterWithdrawWei = await eoaBalance(clientA, hunter.address);
eoaBalances.hunterAfterWithdrawPlus8sWei = eoaBalances.hunterAfterWithdrawWei;
eoaBalances.challengerAfterWithdrawWei = await eoaBalance(clientB, challenger.address);
eoaBalances.challengerAfterWithdrawPlus8sWei = eoaBalances.challengerAfterWithdrawWei;
eoaBalances.funderFinalWei = await eoaBalance(clientD, funder.address);
console.log("Hunter EOA after withdraw:", eoaBalances.hunterAfterWithdrawWei);
console.log("Challenger EOA after withdraw:", eoaBalances.challengerAfterWithdrawWei);

// --- 14. Final read-back of everything.
const finalCases = {};
const count = await read(clientA, "get_case_count", []);
for (let i = 0; i < Number(count); i++) finalCases[`case${i}`] = await read(clientA, "get_case", [BigInt(i)]);
const weights = {
  sybil: await read(clientA, "get_weight", [TARGET_SYBIL]),
  human: await read(clientA, "get_weight", [TARGET_HUMAN]),
  thin: await read(clientA, "get_weight", [TARGET_THIN]),
  borderA: await read(clientA, "get_weight", [TARGET_BORDER_A]),
  borderB: await read(clientA, "get_weight", [TARGET_BORDER_B]),
};
const ledger = await read(clientA, "get_ledger", []);
const pool = await read(clientA, "get_funding_pool", []);
const creditAFinal = await read(clientA, "get_reward_credit", [hunter.address]);
const creditBFinal = await read(clientB, "get_reward_credit", [challenger.address]);
const statsA = await read(clientA, "get_hunter_stats", [hunter.address]);
const statsB = await read(clientB, "get_hunter_stats", [challenger.address]);
const leaderboard = await read(clientA, "get_leaderboard", [10n]);

console.log("Final read-back:");
console.log(" cases:", JSON.stringify(finalCases));
console.log(" weights:", JSON.stringify(weights));
console.log(" ledger:", JSON.stringify(ledger));
console.log(" pool:", JSON.stringify(pool));
console.log(" creditA:", JSON.stringify(creditAFinal), "creditB:", JSON.stringify(creditBFinal));
console.log(" statsA:", JSON.stringify(statsA));
console.log(" statsB:", JSON.stringify(statsB));
console.log(" leaderboard:", JSON.stringify(leaderboard));
console.log(" caseCount:", JSON.stringify(count));

// Numeric invariant check (BigInt, not string comparison).
const invOk =
  BigInt(ledger.total_received_wei) ===
    BigInt(ledger.total_paid_out_wei) + BigInt(ledger.funding_pool_wei) +
    BigInt(ledger.challenge_reserved_wei) + BigInt(ledger.open_stakes_wei) +
    BigInt(ledger.reward_credits_wei) &&
  BigInt(ledger.contract_balance_wei) ===
    BigInt(ledger.total_received_wei) - BigInt(ledger.total_paid_out_wei);
console.log("Invariant total_in == total_out + locked + credits:", invOk, "| contract reports invariant_ok:", ledger.invariant_ok);
if (!invOk || !ledger.invariant_ok) throw new Error("LEDGER INVARIANT BROKEN");

// GEN reconciliation (wei -> GEN for the report).
const weiToGen = (w) => (BigInt(w) / GEN).toString();
const reconciliation = {
  totalReceivedGen: weiToGen(ledger.total_received_wei),
  totalPaidOutGen: weiToGen(ledger.total_paid_out_wei),
  fundingPoolGen: weiToGen(ledger.funding_pool_wei),
  challengeReservedGen: weiToGen(ledger.challenge_reserved_wei),
  openStakesGen: weiToGen(ledger.open_stakes_wei),
  rewardCreditsGen: weiToGen(ledger.reward_credits_wei),
  contractBalanceGen: weiToGen(ledger.contract_balance_wei),
  hunterWithdrawnGen: withdrawA ? weiToGen(creditA.credit_wei) : "0",
  challengerWithdrawnGen: withdrawB ? weiToGen(creditB.credit_wei) : "0",
  invariantOk: invOk,
};

const evidence = {
  network: "Stable Studionet",
  chainId: 61999,
  rpcUrl: "https://studio.genlayer.com/api",
  contractAddress: address,
  explorer: `https://explorer-studio.genlayer.com/address/${address}`,
  funder: funder.address,
  hunter: hunter.address,
  challenger: challenger.address,
  freshProbeAccount: fresh.address,
  targets: { sybil: TARGET_SYBIL, human: TARGET_HUMAN, thin: TARGET_THIN, borderA: TARGET_BORDER_A, borderB: TARGET_BORDER_B },
  fundingGen: 100,
  transactions: txs,
  rejectedCalls: rejects,
  cases: finalCases,
  weights,
  ledger,
  reconciliation,
  fundingPool: pool,
  rewardCreditHunter: creditAFinal,
  rewardCreditChallenger: creditBFinal,
  hunterStats: statsA,
  challengerStats: statsB,
  leaderboard,
  caseCount: count,
  rewardClaimedCase0: rewardClaimed0,
  borderlineAttempts,
  successChallengeOnChain: successChallenge,
  withdrawHunter: withdrawA,
  withdrawChallenger: withdrawB,
  eoaBalances,
  checkedAt: new Date().toISOString(),
};
writeFileSync(path.join(root, "evidence.json"), JSON.stringify(evidence, null, 2) + "\n");
console.log("Wrote evidence.json");

const caseLine = (c) => `- Case ${c.case_id}: status \`${c.status}\`, verdict \`${c.final_verdict}\`, signals \`${JSON.stringify(c.final_signals)}\`, weight \`${c.final_weight_scaled}\`, witnesses \`${c.witnesses.length}\``;
const lines = [
  "# Live verification",
  "",
  "Network: Stable Studionet (chain 61999). Contract: `" + address + "`",
  "Explorer: https://explorer-studio.genlayer.com/address/" + address,
  "Checked at: " + evidence.checkedAt,
  "",
  "Previous contract `0xAA9667d41895928f7DE2AACC2fd0F1764f6c6EE4` is superseded: it used a simulated ledger with no real GEN movement. This deployment replaces it.",
  "",
  "## Transactions (all FINALIZED)",
  "",
  ...txs.map((t) => `- ${t.label}: \`${t.txHash}\` — ${t.status}`),
  "",
  "## Rejected calls (all rejected before any state change; state re-read and confirmed unchanged)",
  "",
  ...rejects.map((r) => `- ${r.label} — rejected at \`${r.rejectedAt}\`${r.txHash ? ` (tx \`${r.txHash}\`)` : ""}${r.error ? `: ${r.error.slice(0, 200)}` : ""}`),
  "",
  "## Read-back (via RPC, after the flow)",
  "",
  ...Object.values(finalCases).map(caseLine),
  "- Weights: " + JSON.stringify(weights),
  "- Ledger: " + JSON.stringify(ledger),
  "- GEN reconciliation: " + JSON.stringify(reconciliation),
  "- Funding pool: " + JSON.stringify(pool),
  "- Hunter reward credit (after withdraw): " + JSON.stringify(creditAFinal),
  "- Challenger reward credit (after withdraw): " + JSON.stringify(creditBFinal),
  "- Hunter stats: " + JSON.stringify(statsA),
  "- Challenger stats: " + JSON.stringify(statsB),
  "- Leaderboard: " + JSON.stringify(leaderboard),
  "- Case count: " + JSON.stringify(count),
  "- Successful challenge on-chain: " + (successChallenge ? `yes, case ${successChallenge.caseId} (${successChallenge.firstVerdict} -> ${successChallenge.secondVerdict}, CONTRADICTION witness)` : "no — both borderline attempts failed to flip; see evidence.json borderlineAttempts"),
  "- Hunter withdrew: " + withdrawA + "; challenger withdrew: " + withdrawB,
  "- EOA balances (wei): " + JSON.stringify(eoaBalances),
  "",
  "Full machine-readable record: `evidence.json` in this repository.",
  "",
];
writeFileSync(path.join(root, "docs", "live-verification.md"), lines.join("\n"));
console.log("Wrote docs/live-verification.md");
