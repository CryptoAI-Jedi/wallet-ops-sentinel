# Compromised Wallet — Incident Response Runbook

**Version:** 1.0  
**Last Updated:** 2026-02  
**Owner:** Wallet Ops  

---

## Before You Start

This runbook is for when you have reason to believe a wallet — hot, warm,
or custodial — has been compromised or is actively being drained. It does
not cover smart contract exploits or exchange-side breaches. Those have
their own runbooks.

Work through this top to bottom. Do not skip steps to save time. A missed
step in the first 10 minutes is how a $50k incident becomes a $500k one.

---

## Step 1 — Confirm It's Real (Don't Panic Yet)

Before you do anything else, verify the alert is not a false positive.

1. Open the blockchain explorer for the affected chain:
   - BTC → [mempool.space](https://mempool.space)
   - ETH/EVM → [etherscan.io](https://etherscan.io) or [Tenderly](https://tenderly.co)

2. Pull up the flagged address and look at the last 3–5 transactions.

3. Ask yourself:
   - Is this a scheduled sweep or a known internal transfer?
   - Does the destination address match any of our own cold/warm wallets?
   - Was there a planned withdrawal or rebalance today?

4. If you can explain the transaction — **close the alert, log it as a
   false positive, and document why.**

5. If you cannot explain it — **move to Step 2 immediately.**

---

## Step 2 — Stop the Bleeding

Your only goal right now is to prevent more funds from leaving.

**If the wallet is a hot wallet with an active signing key:**

- Revoke API access immediately if the wallet is connected to any
  exchange or trading system.
- If you have a multi-sig setup, notify the other keyholders right now.
  Do not wait. Call or message directly — do not rely on email.
- Freeze any automated sweeps or scheduled transactions tied to this
  address.

**If the wallet is connected to a DeFi protocol:**

- Go to [revoke.cash](https://revoke.cash) and revoke all token approvals
  for the compromised address.
- Do this before moving funds. Approvals can be used to drain tokens even
  after you move the native balance.

**If funds are still in the wallet and the attacker has not fully drained it:**

- Do NOT send funds to the same wallet type or a wallet on the same
  device/seed phrase.
- Move remaining funds to a clean, air-gapped wallet or a hardware wallet
  that has never touched this environment.

---

## Step 3 — Lock Down the Environment

The wallet is a symptom. The root cause is somewhere in your environment.

Work through this checklist:

- [ ] Rotate all API keys associated with this wallet immediately
- [ ] Revoke any active sessions on exchange accounts linked to this address
- [ ] Check for unauthorized SSH sessions on any server that had access to
      the private key or seed phrase
- [ ] Run a process check on the affected machine — look for anything
      unexpected running in the background
- [ ] Check browser extensions on any machine used to access this wallet —
      malicious extensions are a common attack vector
- [ ] If a hardware wallet was involved, check whether the seed phrase was
      ever entered digitally (typed into a computer, screenshot, cloud note, etc.)

If you find anything suspicious on a machine, **take it offline** and do
not use it for anything until it has been wiped and rebuilt.

---

## Step 4 — Document Everything

Start a running incident log right now. Use a plain text file, a Notion
page, a Google Doc — whatever is fastest. You will need this later.

Record:

- Time you first noticed the alert
- Transaction hashes for all suspicious activity
- Every action you took and when
- Every person you contacted and when
- Any systems you took offline

Do not rely on memory. You are going to be moving fast and talking to
multiple people. Write it down as you go.

---

## Step 5 — Notify the Right People

Who you notify depends on the severity. Use this as a guide:

| Situation | Who to Notify |
|---|---|
| Internal wallet, funds < $10k | Team lead + ops channel |
| Internal wallet, funds > $10k | Team lead + management + legal |
| Client funds involved | All of the above + affected client immediately |
| Suspected insider threat | Management + legal only — do not broadcast |

When you notify clients, be direct and factual. Tell them what happened,
what you have done so far, and what you are doing next. Do not speculate
on cause until you have confirmed it.

---

## Step 6 — Trace the Funds

Once the immediate situation is contained, start tracing where the funds went.

1. Use [Breadcrumbs](https://www.breadcrumbs.app) or
   [Arkham Intelligence](https://platform.arkhamintelligence.com) to
   follow the transaction trail.

2. Check if funds were sent to a known exchange deposit address. If so,
   file a report with that exchange's compliance team immediately — they
   can sometimes freeze the funds before withdrawal.

3. Document the full transaction path in your incident log.

4. If the amount is significant, contact a blockchain forensics firm.
   Companies like Chainalysis and TRM Labs work with law enforcement and
   can assist with recovery efforts.

---

## Step 7 — File Reports (If Applicable)

Depending on the amount and jurisdiction, you may be required to report.

- **FBI IC3:** [ic3.gov](https://www.ic3.gov) — for US-based incidents
- **Exchange compliance teams** — if funds landed on a CEX
- **Local law enforcement** — for large amounts, get a case number even
  if they cannot help directly. You will need it for insurance claims.

Keep copies of everything you submit.

---

## Step 8 — Post-Incident Review

Once the dust settles — minimum 48 hours after containment — hold a
post-mortem. The goal is not to assign blame. The goal is to make sure
this cannot happen the same way twice.

Cover:

1. How did the attacker get access? (Phishing, leaked key, malware,
   insider, etc.)
2. How long did they have access before we detected it?
3. What did the alert catch? What did it miss?
4. What would have reduced the damage if caught earlier?
5. What process or control needs to change?

Write up the findings and store them. Update this runbook if anything
here needs to change based on what you learned.

---

## Quick Reference — Useful Tools

| Tool | Use |
|---|---|
| [mempool.space](https://mempool.space) | BTC transaction explorer |
| [etherscan.io](https://etherscan.io) | ETH transaction explorer |
| [Tenderly](https://tenderly.co) | EVM transaction simulation & tracing |
| [revoke.cash](https://revoke.cash) | Revoke ERC-20 token approvals |
| [Breadcrumbs](https://www.breadcrumbs.app) | On-chain fund tracing |
| [Arkham Intelligence](https://platform.arkhamintelligence.com) | Address labeling & tracing |
| [ic3.gov](https://www.ic3.gov) | FBI cybercrime reporting |

---

*This runbook is a living document. If you use it and something does not
work as described, update it before you close the incident.*
