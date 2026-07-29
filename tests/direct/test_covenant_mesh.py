import json


def address_hex(address):
    return "0x" + bytes(address).hex()


def deploy_as(direct_vm, direct_deploy, sender):
    direct_vm.sender = sender
    return direct_deploy("contracts/covenant_mesh.py")


def create_research_org(contract, direct_vm, sender):
    direct_vm.sender = sender
    return contract.create_organization(
        "Civic Systems Lab",
        "RESEARCH",
        "Develop reproducible public-interest research for equitable infrastructure and community accountability.",
        "European Union",
    )


def request_access(contract, org_id, collection_id="COL-001"):
    return contract.submit_access_request(
        org_id,
        collection_id,
        "Neighborhood cooling access study",
        "Measure whether public cooling access reaches neighborhoods with the highest documented heat exposure and publish only aggregated findings.",
        "Join block-level heat observations to public facility service areas, aggregate every output to neighborhoods, suppress sparse groups, and document uncertainty before publication.",
        "Use minimum variables, prohibit row-level exports, suppress cells below twenty observations, keep an access log, and delete working extracts after thirty days.",
        30,
        24,
    )


def mock_allow(direct_vm):
    direct_vm.mock_llm(
        r".*independent data-use covenant panel.*",
        json.dumps(
            {
                "verdict": "ALLOW",
                "risk_score": 22,
                "allocated_budget": 20,
                "conditions": "Publish neighborhood-level aggregates only and delete working extracts after thirty days.",
                "analysis": "The purpose is permitted, retention is bounded, and the safeguards directly address sparse cells and row-level exposure.",
            }
        ),
    )


def test_genesis_collections_are_complete(direct_vm, direct_deploy, direct_alice):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    overview = contract.get_overview()
    collections = contract.get_collections()

    assert overview["organizations"] == 1
    assert overview["collections"] == 6
    assert len(collections) == 6
    assert collections[0].id == "COL-001"
    assert collections[0].available_budget == 180
    assert collections[1].sensitivity == "CRITICAL"


def test_organization_creation(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    org_id = create_research_org(contract, direct_vm, direct_bob)
    organization = contract.get_organizations()[-1]

    assert org_id == "ORG-002"
    assert organization.kind == "RESEARCH"
    assert organization.owner.as_hex.lower() == address_hex(direct_bob).lower()
    assert organization.reputation == 50


def test_only_stewards_publish_collections(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    org_id = create_research_org(contract, direct_vm, direct_bob)

    with direct_vm.expect_revert("Only stewards"):
        contract.publish_collection(
            org_id,
            "Unauthorized Collection",
            "Research",
            "A sufficiently detailed collection description for the direct test.",
            "This covenant is deliberately long enough to satisfy validation while remaining unauthorized for a research organization.",
            "Public-interest research and reproducible analysis with community benefit.",
            "Profiling, surveillance, exclusion, and targeted commercial decisions.",
            "Aggregation, deletion, access logs, and transparent publication methods.",
            "HIGH",
            100,
            30,
            14,
        )


def test_request_requires_owner(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    org_id = create_research_org(contract, direct_vm, direct_bob)
    direct_vm.sender = direct_charlie

    with direct_vm.expect_revert("Only the organization owner"):
        request_access(contract, org_id)


def test_consensus_issues_permit_and_allocates_budget(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    org_id = create_research_org(contract, direct_vm, direct_bob)
    request_id = request_access(contract, org_id)
    mock_allow(direct_vm)

    contract.resolve_access_request(request_id)

    request = contract.get_requests()[0]
    permit = contract.get_permits()[0]
    collection = contract.get_collections()[0]
    organization = contract.get_organizations()[-1]
    overview = contract.get_overview()

    assert request.status == "APPROVED"
    assert request.verdict == "ALLOW"
    assert request.permit_id == "PER-0001"
    assert permit.status == "ACTIVE"
    assert permit.allocated_budget == 20
    assert collection.available_budget == 160
    assert organization.reputation == 55
    assert overview["budget_allocated"] == 20

    with direct_vm.expect_revert("not pending"):
        contract.resolve_access_request(request_id)


def test_denial_persists_without_consuming_capacity(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    org_id = create_research_org(contract, direct_vm, direct_bob)
    request_id = request_access(contract, org_id, "COL-002")
    direct_vm.mock_llm(
        r".*independent data-use covenant panel.*",
        json.dumps(
            {
                "verdict": "DENY",
                "risk_score": 91,
                "allocated_budget": 18,
                "conditions": "",
                "analysis": "The proposed processing conflicts with protected cultural authority.",
            }
        ),
    )

    contract.resolve_access_request(request_id)

    assert contract.get_requests()[0].status == "DENIED"
    assert contract.get_requests()[0].allocated_budget == 0
    assert len(contract.get_permits()) == 0
    assert contract.get_collections()[1].available_budget == 120


def test_usage_consumes_only_authorized_budget(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    org_id = create_research_org(contract, direct_vm, direct_bob)
    request_id = request_access(contract, org_id)
    mock_allow(direct_vm)
    contract.resolve_access_request(request_id)

    checkpoint_id = contract.record_usage(
        "PER-0001",
        7,
        "Generated neighborhood-level cooling access aggregates after suppressing every sparse output cell.",
        "https://example.org/public-method-note",
    )

    permit = contract.get_permits()[0]
    assert checkpoint_id == "USE-0001"
    assert permit.consumed_budget == 7
    assert contract.get_overview()["budget_consumed"] == 7

    with direct_vm.expect_revert("exceeds remaining budget"):
        contract.record_usage(
            "PER-0001",
            14,
            "Attempt to consume more units than remain under the issued privacy budget.",
            "",
        )


def test_audit_can_suspend_and_reduce_reputation(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    org_id = create_research_org(contract, direct_vm, direct_bob)
    request_id = request_access(contract, org_id)
    mock_allow(direct_vm)
    contract.resolve_access_request(request_id)
    audit_id = contract.submit_audit(
        "PER-0001",
        "The team completed the planned aggregation but cannot yet demonstrate deletion of two temporary extracts or provide the required access-log reconciliation. Publication remains paused pending containment and verified deletion.",
        "https://example.org/audit-record",
    )
    direct_vm.mock_llm(
        r".*independent compliance panel.*",
        json.dumps(
            {
                "outcome": "SUSPEND",
                "compliance_score": 38,
                "findings": "Missing deletion proof and unreconciled access logs create material uncertainty requiring remediation.",
            }
        ),
    )

    contract.resolve_audit(audit_id)

    assert contract.get_permits()[0].status == "SUSPENDED"
    assert contract.get_audits()[0].outcome == "SUSPEND"
    assert contract.get_organizations()[-1].reputation == 43


def test_remediation_restores_suspended_permit(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = deploy_as(direct_vm, direct_deploy, direct_alice)
    org_id = create_research_org(contract, direct_vm, direct_bob)
    request_id = request_access(contract, org_id)
    mock_allow(direct_vm)
    contract.resolve_access_request(request_id)
    audit_id = contract.submit_audit(
        "PER-0001",
        "The team cannot currently reconcile the access log with all temporary extracts and requests a suspension while containment work is completed.",
        "https://example.org/audit",
    )
    direct_vm.mock_llm(
        r".*independent compliance panel.*",
        json.dumps(
            {
                "outcome": "SUSPEND",
                "compliance_score": 35,
                "findings": "Containment and deletion evidence are incomplete.",
            }
        ),
    )
    contract.resolve_audit(audit_id)
    remediation_id = contract.submit_remediation(
        "PER-0001",
        "The security lead will delete both temporary extracts within twenty-four hours, publish signed deletion hashes, reconcile every access-log entry, assign an independent reviewer, and run weekly checks for the remainder of the permit.",
    )
    direct_vm.mock_llm(
        r".*Evaluate whether this remediation plan.*",
        json.dumps(
            {
                "decision": "RESTORE",
                "analysis": "The plan assigns ownership, deadlines, deletion proof, independent review, and continuing monitoring.",
            }
        ),
    )

    contract.resolve_remediation(remediation_id)

    assert contract.get_permits()[0].status == "ACTIVE"
    assert contract.get_remediations()[0].decision == "RESTORE"
    assert contract.get_organizations()[-1].reputation == 47

