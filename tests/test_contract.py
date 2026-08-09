import json

CONTRACT = "contracts/contract.py"


def setup_agreement(contract, vm, alice, bob):
    vm.sender = alice
    agreement = contract.create_agreement(
        bob, "Production API availability", "Provider will operate the production API continuously.",
        "Monthly availability must be at least 99.9 percent and incidents acknowledged within 30 minutes.",
        "Announced maintenance with 72 hours notice is excluded.",
    )
    vm.sender = bob
    contract.accept_agreement(agreement)
    return agreement


def test_two_party_acceptance_and_authorization(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    direct_vm.sender = direct_alice
    agreement = contract.create_agreement(
        direct_bob, "API SLA", "Provider keeps the API available for production customers.",
        "Availability is at least 99.9 percent each calendar month.", "Announced maintenance is excluded.",
    )
    with direct_vm.expect_revert("Only the named provider"):
        contract.accept_agreement(agreement)
    direct_vm.sender = direct_bob
    contract.accept_agreement(agreement)
    assert contract.get_agreement(agreement)["status"] == "ACTIVE"


def test_complete_claim_lifecycle(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    agreement = setup_agreement(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    claim = contract.file_claim(agreement, "inc-202", "The production API was unavailable for two hours without maintenance notice.", "Monitoring recorded HTTP failures from 10:00 through 12:00 UTC across three regions.")
    direct_vm.sender = direct_bob
    contract.respond_claim(claim, "We confirm an unannounced database failure affected the production API.", "Incident log records the outage and restoration after one hour and fifty eight minutes.")
    direct_vm.mock_llm("SERVICE COURT", json.dumps({"ruling":"BREACH","severity":82,"rationale":"The admitted outage violates availability and was not excluded.","remedy":"Publish a corrective action report."}))
    settled = contract.settle_claim(claim)
    direct_vm.clear_mocks()
    assert settled["ruling"] == "BREACH"
    assert contract.get_agreement(agreement)["status"] == "ACTIVE"
    assert contract.get_stats()["breaches"] == 1


def test_provider_cannot_file_customer_claim(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    agreement = setup_agreement(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only the customer"):
        contract.file_claim(agreement, "bad-1", "Provider tries to create its own customer complaint record.", "This evidence is long enough but signed by the wrong party wallet.")


def test_one_material_appeal_only(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    agreement = setup_agreement(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    claim = contract.file_claim(agreement, "inc-9", "Latency exceeded the signed threshold for multiple production requests.", "Customer traces show repeated ten second responses during the incident window.")
    direct_vm.sender = direct_bob
    contract.respond_claim(claim, "Provider records show elevated latency but no complete loss of service.", "Provider telemetry confirms elevated response time for twenty minutes.")
    direct_vm.mock_llm("SERVICE COURT", json.dumps({"ruling":"PARTIAL_BREACH","severity":50,"rationale":"A metric was missed for part of the period.","remedy":"Review capacity controls."}))
    contract.settle_claim(claim)
    direct_vm.sender = direct_alice
    appealed = contract.appeal_claim(claim, "New independent regional traces confirm the latency breach lasted ninety minutes, not twenty.")
    direct_vm.clear_mocks()
    assert appealed["status"] == "FINAL" and appealed["appealed"] is True
    with direct_vm.expect_revert("cannot be appealed"):
        contract.appeal_claim(claim, "Another new evidence package that should not enable a second appeal.")


def test_invalid_transitions_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    agreement = setup_agreement(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    claim = contract.file_claim(agreement, "inc-x", "The customer reports a material service interruption in production.", "Monitoring data records failures across the documented service boundary.")
    with direct_vm.expect_revert("not ready"):
        contract.settle_claim(claim)
