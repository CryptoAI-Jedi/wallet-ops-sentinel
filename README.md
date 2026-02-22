# Wallet Ops Sentinel

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Bitcoin](https://img.shields.io/badge/Bitcoin-Blockstream_API-F7931A?style=flat-square&logo=bitcoin&logoColor=white)
![Ethereum](https://img.shields.io/badge/Ethereum-Etherscan_API-3C3C3D?style=flat-square&logo=ethereum&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A Python-based wallet monitoring tool built around exchange-grade ops
principles to detect anomalies early, log everything, and escalate fast.

Monitors BTC and EVM wallet addresses using free public APIs. Flags large
outflows, interactions with sanctioned or mixer contracts, and writes
structured alerts to a JSON log for ops review.

Paired with a professional incident response runbook and multi-sig
operations guide because tooling without process is just noise.

---

## Features

- **Multi-chain monitoring:** BTC via Blockstream API, ETH/EVM via Etherscan API
- **Large outflow detection:** configurable thresholds per chain
- **Flagged contract alerts:** detects interactions with known mixers and
  OFAC-sanctioned addresses (Tornado Cash and others)
- **Structured JSON alert log:** every alert timestamped and labeled by
  severity (HIGH / CRITICAL)
- **Human-readable config:** all watchlists and thresholds managed in
  `config.yaml`, no code changes needed
- **Ops runbooks included:** incident response SOP and multi-sig best
  practices written for ops teams, not developers

---

## Project Structure

```text
wallet-ops-sentinel/
├── wallet_sentinel.py          # Main monitoring script
├── config.yaml                 # Watchlist, thresholds, API keys (not committed)
├── alerts.json                 # Auto-generated alert log (not committed)
├── requirements.txt            # Python dependencies
├── .gitignore
├── runbooks/
│   ├── compromised-wallet-ir.md    # Incident response runbook
│   └── multisig-best-practices.md  # Multi-sig ops guide
└── README.md
```

---

## Quickstart

### 1. **Clone the repo**

```bash
git clone https://github.com/CryptoAI-Jedi/wallet-ops-sentinel.git
cd wallet-ops-sentinel
```

### 2. **Install dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Configure your watchlist**

Copy the example config and edit it:

```bash
cp config.yaml.example config.yaml
```

Open `config.yaml` and add:

- Your Etherscan API key
- Wallet addresses to monitor (BTC and/or ETH)
- Alert thresholds
- Any additional flagged contracts

### 4. **Run the sentinel**

```bash
python wallet_sentinel.py
```

The script polls on the interval defined in `config.yaml` (default: 5
minutes) and writes alerts to `alerts.json`.

---

## Alert Log Format

Each alert entry in `alerts.json` follows this structure:

```json
{
  "timestamp": "2026-02-21T10:45:00Z",
  "chain": "ETH",
  "address": "0xYourAddressHere",
  "tx_hash": "0xabc123...",
  "severity": "CRITICAL",
  "message": "Interaction with flagged contract: 0xd90e2f925...",
  "flagged_contract": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b"
}
```

Severity levels:

| Level | Trigger |
|---|---|
| HIGH | Outflow exceeds configured threshold |
| CRITICAL | Interaction with OFAC-sanctioned or mixer contract |

---

## Runbooks

| Runbook | Description |
|---|---|
| Compromised Wallet IR | Step-by-step response for a suspected or confirmed wallet compromise |
| Multi-Sig Best Practices | Keyholder selection, seed storage, signing procedures, key rotation |

---

## API Keys

| API | Free Tier | Link |
|---|---|---|
| Etherscan | 5 calls/sec, 100k calls/day | [etherscan.io/myapikey](https://etherscan.io/myapikey) |
| Blockstream | No key required | [blockstream.info/api](https://blockstream.info/api) |

---

## Requirements

```text
requests>=2.31.0
pyyaml>=6.0
```

---

## Roadmap

- [ ] Slack / Telegram alert webhook integration
- [ ] Solana wallet monitoring (Solscan API)
- [ ] Monero wallet activity tracking
- [ ] Grafana dashboard for alert visualization
- [ ] Docker container for always-on deployment

---

## Disclaimer

This tool is for operational monitoring and educational purposes. It does
not provide financial or legal advice. Always verify alerts manually before
taking action. See the incident response runbook for guidance.

---

*Built by an ops engineer who has run ASIC mining fleets, managed blockchain nodes, and learned the hard way that monitoring without a runbook is a plan for eventual panic.*
