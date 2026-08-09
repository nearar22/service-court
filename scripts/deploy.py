import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import patch_status
patch_status.apply()
from genlayer_py import create_account, create_client
from genlayer_py.chains import testnet_bradbury

def key():
    value = os.environ.get("GENLAYER_PRIVATE_KEY", "").strip()
    if not value:
        path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        for line in open(path, encoding="utf-8"):
            if line.strip().startswith("GENLAYER_PRIVATE_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'"); break
    if not value: raise SystemExit("GENLAYER_PRIVATE_KEY not found")
    return value if value.startswith("0x") else "0x" + value

def main():
    urllib.request.install_opener(urllib.request.build_opener())
    account = create_account(account_private_key=key())
    client = create_client(chain=testnet_bradbury, account=account)
    root = os.path.dirname(os.path.dirname(__file__))
    code = open(os.path.join(root, "contracts", "contract.py"), encoding="utf-8").read()
    tx = None
    attempts = max(1, int(os.environ.get("DEPLOY_ATTEMPTS", "16")))
    for attempt in range(attempts):
        try:
            tx = client.deploy_contract(code=code, args=[])
            break
        except Exception as exc:
            transient = any(word in str(exc).lower() for word in ("rate limit", "backpressure", "429", "timeout", "503"))
            if not transient or attempt == attempts - 1: raise
            delay = min(300, 60 + attempt * 20)
            print("submit busy; retrying in", delay, "seconds:", exc, flush=True)
            time.sleep(delay)
    print("deployer:", account.address, "tx:", tx, flush=True)
    record = None
    for i in range(180):
        try: record = client.get_transaction(transaction_hash=tx)
        except Exception as exc: print("poll:", exc, flush=True); time.sleep(8); continue
        status = record.get("status_name") or record.get("status")
        print(i, status, record.get("recipient"), flush=True)
        if str(status) in {"ACCEPTED", "FINALIZED", "UNDETERMINED", "CANCELED"}: break
        time.sleep(8)
    if str(status) not in {"ACCEPTED", "FINALIZED"}: raise RuntimeError("Deployment failed: " + str(status))
    out = {"network":"bradbury","chainId":4221,"tx":str(tx),"address":str(record.get("recipient")),"explorer":"https://explorer-bradbury.genlayer.com"}
    with open(os.path.join(root,"deployment.json"),"w",encoding="utf-8") as f: json.dump(out,f,indent=2)
    print(json.dumps(out, indent=2))
if __name__ == "__main__": main()
