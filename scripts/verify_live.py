import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import patch_status
patch_status.apply()
from genlayer_py import create_account, create_client
from genlayer_py.chains import testnet_bradbury
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.contracts.utils import make_calldata_object
import eth_utils

TERMINAL={"ACCEPTED","FINALIZED","UNDETERMINED","CANCELED"}

def env_value(path,name):
    for line in open(path,encoding="utf-8"):
        if line.strip().startswith(name+"="): return line.split("=",1)[1].strip().strip('"').strip("'")
    raise RuntimeError(name+" not found")

def account(key): return create_account(account_private_key=key if key.startswith("0x") else "0x"+key)
def client(acct): return create_client(chain=testnet_bradbury,account=acct)

def wait(c,tx,label):
    for i in range(120):
        rec=c.get_transaction(transaction_hash=tx); status=str(rec.get("status_name") or rec.get("status")); print(label,i,status,flush=True)
        if status in TERMINAL:
            if status not in {"ACCEPTED","FINALIZED"}: raise RuntimeError(label+" "+status)
            return
        time.sleep(8)
    raise TimeoutError(label)

def read(c,acct,address,fn,args=None):
    data=[calldata.encode(make_calldata_object(method=fn,args=args or [],kwargs=None)),b"\x00"]
    res=c.provider.make_request(method="gen_call",params=[{"type":"read","to":address,"from":acct.address,"data":serialize(data),"transaction_hash_variant":"latest-nonfinal"}])["result"]
    raw=res["data"] if isinstance(res,dict) else res
    return calldata.decode(eth_utils.hexadecimal.decode_hex("0x"+raw))

def write(c,address,fn,args):
    tx=c.write_contract(address=address,function_name=fn,args=args,value=0); print(fn,tx,flush=True); wait(c,tx,fn); return str(tx)

def main():
    root=os.path.dirname(os.path.dirname(__file__)); desktop=os.path.dirname(os.path.dirname(root))
    primary=account(env_value(os.path.join(os.path.dirname(root),".env"),"GENLAYER_PRIVATE_KEY"))
    provider=account(env_value(os.path.join(desktop,"sansh genlayer","accounts.env"),"ACCOUNT_1_GENLAYER_PRIVATE_KEY"))
    pc,vc=client(primary),client(provider); deployment=json.load(open(os.path.join(root,"deployment.json"))); address=deployment["address"]
    txs=[]
    txs.append(write(pc,address,"create_agreement",[provider.address,"Production API SLA","Provider will operate the production API continuously for subscribed customers.","Monthly availability must be at least 99.9 percent and incidents acknowledged within 30 minutes.","Announced maintenance with at least 72 hours notice is excluded."]))
    stats=read(pc,primary,address,"get_stats"); aid="sla-"+str(stats["agreements"])
    txs.append(write(vc,address,"accept_agreement",[aid]))
    txs.append(write(pc,address,"file_claim",[aid,"incident-live-1","The production API was unavailable for nearly two hours without any maintenance notice.","Independent monitoring recorded HTTP failures from 10:00 through 11:58 UTC across three regions."]))
    stats=read(pc,primary,address,"get_stats"); cid="claim-"+str(stats["claims"])
    txs.append(write(vc,address,"respond_claim",[cid,"We confirm an unannounced database failure affected the production API during that period.","Provider incident logs record the outage, escalation, and restoration after one hour and fifty eight minutes."]))
    txs.append(write(pc,address,"settle_claim",[cid]))
    claim=read(pc,primary,address,"get_claim",[cid]); print(json.dumps(claim,indent=2,default=str));
    if claim["status"]!="SETTLED" or claim["ruling"] not in ("BREACH","PARTIAL_BREACH"): raise RuntimeError("Unexpected live verdict")
    with open(os.path.join(root,"verification.json"),"w",encoding="utf-8") as f: json.dump({"agreement":aid,"claim":cid,"transactions":txs,"ruling":claim["ruling"],"severity":claim["severity"]},f,indent=2)
if __name__=="__main__": main()
