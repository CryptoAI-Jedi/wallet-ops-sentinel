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
    cp config.yaml.example config.yaml   # fill in your values
    python wallet_sentinel.py
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[FATAL] PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


# ─────────────────────────────────────────────
# CONFIG LOADER
# ─────────────────────────────────────────────

CONFIG_FILE = "config.yaml"


def load_config() -> dict:
    config_path = Path(CONFIG_FILE)
    if not config_path.exists():
        print(f"[FATAL] {CONFIG_FILE} not found.")
        print(f"        Run: cp config.yaml.example config.yaml")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Validate required fields
    required = ["api_keys", "watchlist", "thresholds", "flagged_contracts", "polling", "logging"]
    missing = [key for key in required if key not in config]
    if missing:
        print(f"[FATAL] config.yaml missing required keys: {', '.join(missing)}")
        sys.exit(1)

    return config


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_alert(alert: dict, alert_log: str):
    try:
        with open(alert_log, "r") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = []

    log.append(alert)

    with open(alert_log, "w") as f:
        json.dump(log, f, indent=2)

    print(f"[ALERT] {alert['severity']} | {alert['message']}")


# ─────────────────────────────────────────────
# BTC MONITORING (Blockstream API)
# ─────────────────────────────────────────────

def check_btc_address(address: str, label: str, threshold: int, alert_log: str):
    url = f"https://blockstream.info/api/address/{address}/txs"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        txs = resp.json()
    except requests.RequestException as e:
        print(f"[WARN] BTC fetch failed for {label} ({address}): {e}")
        return

    if not txs:
        return

    latest_tx = txs[0]
    tx_id = latest_tx.get("txid", "unknown")

    total_out = sum(
        vin.get("prevout", {}).get("value", 0)
        for vin in latest_tx.get("vin", [])
        if vin.get("prevout", {}).get("scriptpubkey_address") == address
    )

    if total_out >= threshold:
        write_alert({
            "timestamp": now_utc(),
            "chain": "BTC",
            "address": address,
            "label": label,
            "tx_id": tx_id,
            "severity": "HIGH",
            "message": f"Large BTC outflow from {label}: {total_out / 1e8:.8f} BTC",
            "value_sats": total_out,
        }, alert_log)


# ─────────────────────────────────────────────
# ETH MONITORING (Etherscan API)
# ─────────────────────────────────────────────

def check_eth_address(address: str, label: str, threshold: int,
                      flagged: set, api_key: str, alert_log: str):
    url = (
        f"https://api.etherscan.io/api"
        f"?module=account&action=txlist"
        f"&address={address}"
        f"&startblock=0&endblock=99999999"
        f"&sort=desc&apikey={api_key}"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[WARN] ETH fetch failed for {label} ({address}): {e}")
        return

    if data.get("status") != "1" or not data.get("result"):
        return

    latest_tx = data["result"][0]
    tx_hash = latest_tx.get("hash", "unknown")
    value_wei = int(latest_tx.get("value", 0))
    to_addr = latest_tx.get("to", "").lower()
    from_addr = latest_tx.get("from", "").lower()

    # Large outflow check
    if from_addr == address.lower() and value_wei >= threshold:
        write_alert({
            "timestamp": now_utc(),
            "chain": "ETH",
            "address": address,
            "label": label,
            "tx_hash": tx_hash,
            "severity": "HIGH",
            "message": f"Large ETH outflow from {label}: {value_wei / 1e18:.6f} ETH to {to_addr}",
            "value_wei": value_wei,
        }, alert_log)

    # Mixer / flagged contract interaction check
    if to_addr in flagged:
        write_alert({
            "timestamp": now_utc(),
            "chain": "ETH",
            "address": address,
            "label": label,
            "tx_hash": tx_hash,
            "severity": "CRITICAL",
            "message": f"Interaction with flagged contract: {to_addr}",
            "flagged_contract": to_addr,
        }, alert_log)


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

def run():
    config = load_config()

    api_key = config["api_keys"].get("etherscan", "")
    btc_wallets = config["watchlist"].get("btc", [])
    eth_wallets = config["watchlist"].get("eth", [])
    btc_threshold = config["thresholds"].get("btc_outflow_sats", 50000000)
    eth_threshold = config["thresholds"].get("eth_outflow_wei", 500000000000000000)
    flagged = {entry["address"].lower() for entry in config.get("flagged_contracts", [])}
    interval = config["polling"].get("interval_seconds", 300)
    alert_log = config["logging"].get("alert_log_file", "alerts.json")

    print(f"[INFO] Wallet Sentinel started at {now_utc()}")
    print(f"[INFO] Config loaded from {CONFIG_FILE}")
    print(f"[INFO] Monitoring {len(btc_wallets)} BTC | {len(eth_wallets)} ETH addresses")
    print(f"[INFO] Flagged contracts: {len(flagged)}")
    print(f"[INFO] Poll interval: {interval}s | Alert log: {alert_log}\n")

    if not api_key or api_key == "YOUR_ETHERSCAN_API_KEY":
        print("[WARN] Etherscan API key not set — ETH monitoring will fail.")
        print("[WARN] Add your key to config.yaml → api_keys → etherscan\n")

    while True:
        print(f"[{now_utc()}] Running checks...")

        for wallet in btc_wallets:
            check_btc_address(wallet["address"], wallet.get("label", "unlabeled"),
                              btc_threshold, alert_log)

        for wallet in eth_wallets:
            check_eth_address(wallet["address"], wallet.get("label", "unlabeled"),
                              eth_threshold, flagged, api_key, alert_log)

        print(f"[{now_utc()}] Checks complete. Sleeping {interval}s...\n")
        time.sleep(interval)


if __name__ == "__main__":
    run()