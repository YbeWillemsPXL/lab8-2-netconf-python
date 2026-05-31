# Lab 8.2 — Task 36: NETCONF + Python (GitHub-driven)

Python script dat YANG-XML configuratie uit deze GitHub repository ophaalt
en via NETCONF deployt op een Cisco IOS-XE toestel.

## Workflow

GitHub (config.xml) → fetch → NETCONF lock → discard → edit-config (candidate)
→ validate → commit → unlock

Bij elke fout: `discard-changes` om de candidate datastore schoon achter te laten.

## Configuratie-inhoud (config.xml)

- Hostname: `CSR1kv-LAB36`
- Loopback36 met IP 36.36.36.1/32
- Loopback37 met IP 37.37.37.1/32
- OSPF process 36 met beide loopbacks in area 0

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # pas waarden aan
python deploy.py
```
