#!/usr/bin/env python3
"""
Task 36 — NETCONF (Python)
Haalt config-XML uit GitHub en deployt via NETCONF op een IOS-XE toestel.
Workflow: lock → discard → edit-config (candidate) → validate → commit → unlock.
Foutafhandeling: bij elke fout wordt discard-changes uitgevoerd.
"""
import os
import sys
import requests
from dotenv import load_dotenv
from ncclient import manager
from ncclient.operations.rpc import RPCError

# --- Config -----------------------------------------------------------------
load_dotenv()

ROUTER = {
    "host": os.getenv("ROUTER_HOST"),
    "port": int(os.getenv("ROUTER_PORT", 830)),
    "username": os.getenv("ROUTER_USER"),
    "password": os.getenv("ROUTER_PASS"),
    "hostkey_verify": False,
    "device_params": {"name": "iosxe"},
    "allow_agent": False,
    "look_for_keys": False,
}

GITHUB_RAW = (
    "https://raw.githubusercontent.com/"
    "YbeWillemsPXL/lab8-2-netconf-python/main/config.xml"
)

# --- Logging helpers --------------------------------------------------------
def info(msg):  print(f"[ INFO ] {msg}")
def ok(msg):    print(f"[  OK  ] {msg}")
def err(msg):   print(f"[ FAIL ] {msg}", file=sys.stderr)

# --- Pipeline ---------------------------------------------------------------
def fetch_config_from_github(url):
    info(f"Fetching config from GitHub: {url}")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    ok(f"Got {len(r.text)} bytes from GitHub")
    return r.text

def deploy(config_xml):
    info(f"Connecting to NETCONF on {ROUTER['host']}:{ROUTER['port']}")
    with manager.connect(**ROUTER) as m:
        ok("NETCONF session established")

        # 1. Lock candidate
        info("Locking candidate datastore")
        m.lock(target="candidate")
        ok("candidate locked")

        try:
            # 2. Discard any leftover candidate changes
            info("Discarding leftover candidate changes")
            m.discard_changes()
            ok("candidate cleared")

            # 3. Edit-config to candidate
            info("Sending edit-config to candidate")
            m.edit_config(target="candidate", config=config_xml)
            ok("edit-config accepted")

            # 4. Validate candidate
            info("Validating candidate")
            m.validate(source="candidate")
            ok("candidate is valid")

            # 5. Commit
            info("Committing candidate to running")
            m.commit()
            ok("commit successful — config is live")

        except RPCError as e:
            err(f"NETCONF error: {e}")
            info("Rolling back: discard-changes on candidate")
            m.discard_changes()
            err("Deployment aborted, candidate discarded")
            return 1

        finally:
            info("Unlocking candidate")
            m.unlock(target="candidate")
            ok("candidate unlocked")

    return 0

def main():
    try:
        config_xml = fetch_config_from_github(GITHUB_RAW)
    except Exception as e:
        err(f"Could not fetch config from GitHub: {e}")
        return 1

    return deploy(config_xml)

if __name__ == "__main__":
    sys.exit(main())
