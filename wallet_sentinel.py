#!/usr/bin/env python3
"""
wallet_sentinel.py
------------------
Monitors wallet addresses across BTC and EVM chains.
Flags large outflows, mixer interactions, and unusual activity.
Logs alerts to JSON for ops review.

APIs used (free tier):
  - Etherscan: https://etherscan.io/apis
  - Blockstream: https://blockstream.info/api/

Usage:
  python wallet_sentinel.py
"""

import requests
import json
import time
from datetime import datetime, timezone

# ─────────────────────────────────────────────
# CONFIG — edit this section
# ─────────────────────────────────────────────

ETHERSCAN_API_KEY = "YOUR_ETHERSCAN_API_KEY"

WATCHLIST = {
    "btc": [
        "bc1qexampleaddress1",
        "bc1qexampleaddress2",
    ],
    "eth": [
        "0xYourEthAddressHere",
    ],
}

# Alert thresholds
BTC_ALERT_THRESHOLD_SATS = 50_000_000   # 0.5 BTC
ETH_ALERT_THRESHOLD_WEI  = 500_000_000_000_000_000  # 0.5 ETH

# Known mixer / high-risk contract addresses (add more as needed)
FLAGGED_CONTRACTS = {
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",  # Tornado Cash Router
    "0x722122df12d4e14e13ac3b6895a86e84145b6967",  # Tornado Cash Proxy
}

ALERT_LOG = "alerts.json"
POLL_INTERVAL_SECONDS = 300  # 5 minutes


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_alert(alert: dict):
    try:
        with open(ALERT_LOG, "r") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = []

    log.append(alert)

    with open(ALERT_LOG, "w") as f:
        json.dump(log, f, indent=2)

    print(f"[ALERT] {alert['severity']} | {alert['message']}")


# ─────────────────────────────────────────────
# BTC MONITORING (Blockstream API)
# ─────────────────────────────────────────────

def check_btc_address(address: str):
    url = f"https://blockstream.info/api/address/{address}/txs"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        txs = resp.json()
    except requests.RequestException as e:
        print(f"[WARN] BTC fetch failed for {address}: {e}")
        return

    if not txs:
        return

    latest_tx = txs[0]
    tx_id = latest_tx.get("txid", "unknown")

    # Sum outflows from this address
    total_out = sum(
        vin.get("prevout", {}).get("value", 0)
        for vin in latest_tx.get("vin", [])
        if vin.get("prevout", {}).get("scriptpubkey_address") == address
    )

    if total_out >= BTC_ALERT_THRESHOLD_SATS:
        write_alert({
            "timestamp": now_utc(),
            "chain": "BTC",
            "address": address,
            "tx_id": tx_id,
            "severity": "HIGH",
            "message": f"Large BTC outflow detected: {total_out / 1e8:.8f} BTC",
            "value_sats": total_out,
        })


# ─────────────────────────────────────────────
# ETH MONITORING (Etherscan API)
# ─────────────────────────────────────────────

def check_eth_address(address: str):
    url = (
        f"https://api.etherscan.io/api"
        f"?module=account&action=txlist"
        f"&address={address}"
        f"&startblock=0&endblock=99999999"
        f"&sort=desc&apikey={ETHERSCAN_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[WARN] ETH fetch failed for {address}: {e}")
        return

    if data.get("status") != "1" or not data.get("result"):
        return

    latest_tx = data["result"][0]
    tx_hash   = latest_tx.get("hash", "unknown")
    value_wei = int(latest_tx.get("value", 0))
    to_addr   = latest_tx.get("to", "").lower()
    from_addr = latest_tx.get("from", "").lower()

    # Large outflow check
    if from_addr == address.lower() and value_wei >= ETH_ALERT_THRESHOLD_WEI:
        write_alert({
            "timestamp": now_utc(),
            "chain": "ETH",
            "address": address,
            "tx_hash": tx_hash,
            "severity": "HIGH",
            "message": f"Large ETH outflow: {value_wei / 1e18:.6f} ETH to {to_addr}",
            "value_wei": value_wei,
        })

    # Mixer / flagged contract interaction check
    if to_addr in FLAGGED_CONTRACTS:
        write_alert({
            "timestamp": now_utc(),
            "chain": "ETH",
            "address": address,
            "tx_hash": tx_hash,
            "severity": "CRITICAL",
            "message": f"Interaction with flagged contract: {to_addr}",
            "flagged_contract": to_addr,
        })


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

def run():
    print(f"[INFO] Wallet Sentinel started at {now_utc()}")
    print(f"[INFO] Monitoring {len(WATCHLIST['btc'])} BTC | {len(WATCHLIST['eth'])} ETH addresses")
    print(f"[INFO] Poll interval: {POLL_INTERVAL_SECONDS}s | Alert log: {ALERT_LOG}\n")

    while True:
        print(f"[{now_utc()}] Running checks...")

        for addr in WATCHLIST["btc"]:
            check_btc_address(addr)

        for addr in WATCHLIST["eth"]:
            check_eth_address(addr)

        print(f"[{now_utc()}] Checks complete. Sleeping {POLL_INTERVAL_SECONDS}s...\n")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
