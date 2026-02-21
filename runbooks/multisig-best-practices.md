# Multi-Sig Wallet Operations — Best Practices

**Version:** 1.0  
**Last Updated:** 2026-02  
**Owner:** Wallet Ops  

---

## What This Is For

This document covers how to set up, manage, and operate a multi-signature
wallet safely. It is written for ops teams — not developers. You do not
need to understand smart contract code to follow this. You do need to
understand that multi-sig is only as strong as the weakest keyholder's
security practices.

If everyone on your signing team reads one document about wallet security,
make it this one.

---

## The Basics — Why Multi-Sig Exists

A standard wallet has one private key. One key means one point of failure.
If that key is stolen, phished, or lost — the funds are gone. No recovery.

Multi-sig requires M-of-N signatures to authorize a transaction. For
example, a 2-of-3 setup means you have 3 keyholders and any 2 of them
must sign before a transaction goes through. One compromised key is not
enough to drain the wallet.

This is the standard for any wallet holding meaningful funds. If your
operation is moving more than $10k regularly and you are not using
multi-sig, that needs to change before anything else in this document
matters.

---

## Choosing Your Threshold

The most common setups and when to use them:

| Setup | Use Case |
|---|---|
| 2-of-3 | Small teams, daily ops wallets, startup treasuries |
| 3-of-5 | Mid-size teams, higher-value treasuries |
| 4-of-7 | Large organizations, DAO treasuries, institutional custody |

**General rule:** Your threshold (M) should be high enough that a single
compromised or unavailable keyholder cannot block or drain the wallet, but
low enough that normal operations do not grind to a halt if one person is
unreachable.

A 2-of-3 is the right starting point for most ops teams. Do not
over-engineer it until you have a reason to.

---

## Keyholder Selection

Pick keyholders carefully. This is not a technical decision — it is an
operational and trust decision.

**Do:**
- Assign keyholders based on role and accountability, not seniority
- Ensure geographic distribution where possible — all keyholders in the
  same office is a physical security risk
- Have a documented succession plan for each keyholder (what happens if
  they leave, become incapacitated, or are terminated)
- Require each keyholder to complete a security baseline before being
  added (see the Security Baseline section below)

**Do not:**
- Give a key to anyone who does not understand what they are signing
- Assign keys to shared accounts or shared devices
- Allow a single person to hold more than one key in the same setup
- Add keyholders as a favor or for convenience

---

## Hardware Wallet Requirements

Every keyholder must use a hardware wallet. Software wallets — including
browser extensions like MetaMask — are not acceptable for multi-sig
signing keys.

Approved hardware wallets:
- Ledger (Nano X or Flex)
- Trezor (Model T or Safe 3)
- Coldcard (BTC-only, highest security)
- GridPlus Lattice1 (for high-frequency signing environments)

**Setup requirements for each device:**
1. Buy directly from the manufacturer. Never buy a hardware wallet from
   Amazon, eBay, or any third party.
2. Verify the packaging seal is intact before opening.
3. Generate the seed phrase on the device itself — never on a computer.
4. Write the seed phrase on paper. Do not photograph it. Do not type it
   anywhere. Do not store it in a password manager.
5. Store the seed phrase in a physically secure location separate from
   the device.

---

## Seed Phrase Storage

This is where most teams cut corners. Do not cut corners here.

**Minimum standard:**
- Seed phrase written on paper, stored in a fireproof safe or safety
  deposit box
- Device and seed phrase stored in separate physical locations
- At least one backup copy of the seed phrase in a second secure location

**Better standard:**
- Seed phrase stamped on metal (Cryptosteel, Bilodal, or similar)
- Stored in a bank safety deposit box or equivalent
- Backup copy held by a trusted party under a formal custody agreement

**Never acceptable:**
- Seed phrase in a cloud note (iCloud, Google Drive, Notion, etc.)
- Seed phrase in a text message or email
- Seed phrase photographed on a phone
- Seed phrase stored in the same location as the hardware wallet

---

## Signing Procedures

Every transaction above a defined threshold should follow a formal signing
procedure. Define your threshold and document it. A reasonable starting
point is any transaction over $5,000.

**Standard signing flow:**

1. **Initiator** creates the transaction in the multi-sig interface
   (Gnosis Safe, Electrum, Sparrow, etc.) and shares the transaction
   details with all keyholders via a secure channel.

2. **Each keyholder** independently verifies the transaction details
   before signing:
   - Destination address (verify character by character — do not copy/paste
     from an unverified source)
   - Amount
   - Network and token type
   - That the request came through the proper channel

3. **Required signers** connect their hardware wallets and sign.

4. **Initiator** broadcasts the transaction once threshold is met.

5. **All keyholders** are notified when the transaction is confirmed
   on-chain.

**One rule that prevents most losses:** Never sign a transaction that was
sent to you unexpectedly. If you did not initiate it or were not expecting
it, verify with the initiator directly — by voice or video — before
signing. Spoofed messages and compromised communication channels are real.

---

## Keyholder Security Baseline

Before anyone is added as a keyholder, they should meet this baseline:

- [ ] Hardware wallet purchased from manufacturer and set up correctly
- [ ] Seed phrase stored securely and offline
- [ ] Device has a strong PIN set (minimum 8 digits)
- [ ] Personal computer used for signing has full-disk encryption enabled
- [ ] No browser extensions installed on the signing machine beyond what
      is strictly necessary
- [ ] Phishing awareness — knows how to verify a transaction request is
      legitimate before signing
- [ ] Has read and acknowledged this runbook

Run through this checklist with each new keyholder in person or on a
verified video call. Do not accept a self-reported checkbox.

---

## Key Rotation

Keys should be rotated in the following situations:

- A keyholder leaves the organization (rotate immediately — do not wait)
- A keyholder's device is lost, stolen, or potentially compromised
- A keyholder's personal security is suspected to be compromised
  (phishing, malware, etc.)
- Annually as a standard hygiene practice

**Rotation process:**
1. Create a new multi-sig wallet with the updated keyholder set
2. Move funds from the old wallet to the new wallet using the standard
   signing procedure
3. Verify the new wallet is functioning correctly before decommissioning
   the old one
4. Revoke any integrations or API connections pointing to the old address
5. Update all internal documentation with the new wallet address
6. Archive the old wallet — do not delete it, as you may need the
   transaction history

---

## Emergency Access

Define what happens if keyholders are unavailable and a time-sensitive
transaction is required.

Document answers to these questions before you need them:

- What is the minimum number of keyholders that need to be reachable at
  any given time?
- Who is the backup contact for each keyholder?
- Is there a break-glass procedure for genuine emergencies, and who can
  authorize it?
- How long can operations tolerate a signing delay before it becomes
  a critical incident?

If you cannot answer these questions, your multi-sig setup has an
operational gap. Fill it now.

---

## Recommended Tools

| Tool | Use |
|---|---|
| [Gnosis Safe](https://safe.global) | EVM multi-sig — industry standard |
| [Sparrow Wallet](https://sparrowwallet.com) | BTC multi-sig with hardware wallet support |
| [Electrum](https://electrum.org) | BTC multi-sig, advanced users |
| [Fireblocks](https://www.fireblocks.com) | Institutional MPC + multi-sig (paid) |
| [revoke.cash](https://revoke.cash) | Revoke token approvals on EVM chains |
| [Etherscan](https://etherscan.io) | Verify transaction details before signing |

---

## Quick Reference — Red Flags

Stop and verify before proceeding if you see any of these:

- A signing request arrives outside of normal business hours with urgency
- The destination address was sent via chat or email and you cannot
  independently verify it
- A keyholder is pressuring others to sign quickly
- The transaction amount is larger than usual with no prior discussion
- You are being asked to sign from a device you do not normally use

Social engineering is the most common attack vector against multi-sig
setups. The technical security is solid — the human layer is where it
breaks down.

---

*This runbook is a living document. Review it any time a security incident
occurs or a keyholder change is made.*
