# ServiceCourt

ServiceCourt is a reusable two-party SLA adjudication primitive for GenLayer. It turns a natural-language service promise into a wallet-bound agreement, then gives customer and provider a shared process for filing, answering, settling, and appealing an incident claim.

**Bradbury deployment:** [`0xED2E...D067`](https://explorer-bradbury.genlayer.com/address/0xED2E95b237829b4107B5da741Ab1dA061773D067) · [deployment transaction](https://explorer-bradbury.genlayer.com/tx/0xb273dc9955ba61519ba1e5d8a935aa187b45dca27ba2e6d41adc883c38c5e50e)

## Why this needs an Intelligent Contract

An SLA dispute is not solved by finding a keyword. The same outage can be a breach, an excluded maintenance window, a partial failure, or an unsupported allegation depending on the signed promise, measurable terms, exclusions, and both parties' evidence. GenLayer validators independently read the complete record and must agree on the ruling and severity that mutate state.

## State machine

```text
PENDING_PROVIDER -> ACTIVE -> CLAIM_OPEN
                              |
             AWAITING_RESPONSE -> READY -> SETTLED -> FINAL (optional appeal)
```

- The customer creates the immutable agreement and binds a provider wallet.
- Only that provider can accept or answer a claim.
- Only the customer can file a claim.
- Settlement is permissionless once both signed statements are present.
- Either bound party may file one appeal, but only with material new evidence.
- The appeal re-evaluates the original promise, both original statements, all original evidence, and the new evidence together.

## Consensus and deterministic controls

The jury returns `BREACH`, `PARTIAL_BREACH`, `NO_BREACH`, or `INSUFFICIENT_EVIDENCE` with severity, rationale, and a non-binding corrective action. Validators independently reproduce the exact ruling and a severity within 15 points. Deterministic code clamps severity into the ruling's legal band, enforces wallet roles and state transitions, prevents repeat appeals, and updates aggregate breach counters only after consensus succeeds.

Evidence is stored inside the claim and authenticated by the wallet that submitted it. ServiceCourt never trusts a mutable URL, never fetches a different record during an appeal, and never allows appeal evidence to replace or hide the original record.

## Interface

```text
create_agreement(provider, title, promise, metrics, exclusions)
accept_agreement(agreement_id)
file_claim(agreement_id, incident_id, statement, evidence)
respond_claim(claim_id, response, evidence)
settle_claim(claim_id)
appeal_claim(claim_id, new_evidence)
get_agreement(id) | get_claim(id) | list_claims(start) | get_stats()
```

## Test

```bash
python -m pytest -q
```

The suite covers party binding, the full settlement lifecycle, wrong-wallet rejection, one material appeal, and fail-closed invalid transitions.

## Deploy

Set `GENLAYER_PRIVATE_KEY` in the shared `.env`, then run `python scripts/deploy.py`. For the two-party live verification, also set a separately funded `GENLAYER_SECONDARY_PRIVATE_KEY`, then run `python scripts/verify_live.py`. The scripts target Bradbury.

No funds are held or transferred. Verdicts and suggested remedies are protocol records, not legal advice.

## License

MIT
