# ServiceCourt

> The uptime chart is red. The invoice says the SLA was met. ServiceCourt gives both parties one shared record and lets GenLayer settle what the promise actually means.

[Bradbury contract](https://explorer-bradbury.genlayer.com/address/0xED2E95b237829b4107B5da741Ab1dA061773D067) | [deployment](https://explorer-bradbury.genlayer.com/tx/0xb273dc9955ba61519ba1e5d8a935aa187b45dca27ba2e6d41adc883c38c5e50e) | MIT

## Case 002: the two-hour outage

The customer and provider signed a 99.9% availability promise. Later, independent monitors recorded regional HTTP failures from 10:00 to 11:58 UTC. The provider answered from its bound wallet and confirmed an unannounced database failure.

Five accepted Bradbury transactions moved that case through the entire docket:

```text
AGREEMENT FILED
      | provider signs
AGREEMENT ACTIVE
      | customer files incident + evidence
CLAIM OPEN
      | provider answers + evidence
READY FOR COURT
      | GenLayer validators rule
BREACH | severity 75 | SETTLED
```

[File agreement](https://explorer-bradbury.genlayer.com/tx/0xe91f08b84d9a03397b3871403bc370213a14aade7d0b8bd2f1b35340f97cc6a2) -> [provider signature](https://explorer-bradbury.genlayer.com/tx/0x4d430afa7f87de6eb53491210b1ff4b6da6698e6867f8ef118245d7645372ca8) -> [customer claim](https://explorer-bradbury.genlayer.com/tx/0xff998c1a5d81479deae4ac953f6cec0f46fa158e6f67659cc843b91dc0798cb6) -> [provider response](https://explorer-bradbury.genlayer.com/tx/0x9ee2d456fd27ab140277ee110ffbfc5b179a23d60eef6f5c2c718671b5ced649) -> [consensus settlement](https://explorer-bradbury.genlayer.com/tx/0x066f24b89475b5b067f18940ddc75e6e5d347000c917aac3fc12a55173bcd073)

The machine-readable receipt is committed in [`verification.json`](verification.json).

## What the court decides

A conventional contract can check an integer. It cannot reliably decide whether an incident violates a natural-language promise once exclusions, partial impact, competing accounts, and incomplete evidence enter the record.

ServiceCourt asks every validator the same bounded question:

```text
Given this immutable promise, measurable terms, exclusions,
customer claim, customer evidence, provider response, and provider evidence:
what breach ruling and severity does the complete signed record support?
```

The only permitted rulings are:

| Ruling | Severity band | Meaning |
|---|---:|---|
| `BREACH` | 67-100 | Clear failure of the signed promise |
| `PARTIAL_BREACH` | 34-66 | Material but incomplete failure |
| `NO_BREACH` | 0-33 | Compliance or a stated exclusion |
| `INSUFFICIENT_EVIDENCE` | 0-33 | The record cannot support a reliable conclusion |

Validators must reproduce the ruling exactly and severity within 15 points. Deterministic code clamps the score into its ruling band, so a model cannot store a low-severity `BREACH` or a high-severity `NO_BREACH`.

## Chain of custody

ServiceCourt deliberately does not judge a floating URL. The evidence text is sealed inside the claim by the wallet that submits it:

- only the named customer can file;
- only the named provider can accept and answer;
- neither party can overwrite the other's statement;
- settlement is permissionless only after both records exist;
- one material appeal may add evidence, never erase the original case;
- the appeal replays the complete original record plus the new evidence.

The contract holds no funds. Its remedy is an auditable protocol record, not an automatic payment and not legal advice.

## Clerk's window

```python
create_agreement(provider, title, promise, metrics, exclusions)
accept_agreement(agreement_id)
file_claim(agreement_id, incident_id, statement, evidence)
respond_claim(claim_id, response, evidence)
settle_claim(claim_id)
appeal_claim(claim_id, new_evidence)
```

Read the docket with `get_agreement`, `get_claim`, `list_claims`, and `get_stats`.

## Reproduce the record

```bash
python -m pytest -q            # 5 contract tests
python scripts/deploy.py       # deploy to Bradbury
python scripts/verify_live.py  # two-wallet end-to-end case
```

The shared `.env` uses `GENLAYER_PRIVATE_KEY` for the customer and a separately funded `GENLAYER_SECONDARY_PRIVATE_KEY` for the provider. The suite covers party binding, complete settlement, wrong-wallet calls, a single material appeal, and invalid transitions that fail closed.

## Repository evidence

```text
contracts/contract.py    court, consensus, and state machine
tests/test_contract.py   adversarial lifecycle tests
scripts/deploy.py        Bradbury deployment with terminal-status checks
scripts/verify_live.py   reproducible two-wallet case
deployment.json          accepted contract receipt
verification.json        accepted lifecycle receipts
```

ServiceCourt is released under the MIT License.
