# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from dataclasses import dataclass
from datetime import datetime, timezone

from genlayer import *


ERROR_EXPECTED = "[EXPECTED]"
ERROR_LLM = "[LLM_ERROR]"


@allow_storage
@dataclass
class Organization:
    id: str
    owner: Address
    name: str
    kind: str
    mission: str
    jurisdiction: str
    reputation: u32
    request_count: u32
    permit_count: u32
    audit_count: u32
    created_at: u64


@allow_storage
@dataclass
class Collection:
    id: str
    steward_org_id: str
    title: str
    domain: str
    description: str
    covenant: str
    allowed_purposes: str
    prohibited_uses: str
    required_safeguards: str
    sensitivity: str
    total_budget: u32
    available_budget: u32
    max_retention_days: u32
    audit_interval_days: u32
    permit_count: u32
    status: str
    created_at: u64


@allow_storage
@dataclass
class AccessRequest:
    id: str
    applicant: Address
    organization_id: str
    collection_id: str
    title: str
    purpose: str
    methods: str
    safeguards: str
    retention_days: u32
    requested_budget: u32
    status: str
    verdict: str
    risk_score: u32
    allocated_budget: u32
    conditions: str
    analysis: str
    permit_id: str
    submitted_at: u64
    resolved_at: u64


@allow_storage
@dataclass
class Permit:
    id: str
    request_id: str
    holder: Address
    organization_id: str
    collection_id: str
    status: str
    scope: str
    conditions: str
    allocated_budget: u32
    consumed_budget: u32
    issued_at: u64
    expires_at: u64
    next_audit_due: u64
    audit_count: u32


@allow_storage
@dataclass
class UsageCheckpoint:
    id: str
    permit_id: str
    organization_id: str
    units: u32
    purpose_note: str
    artifact_url: str
    recorded_at: u64


@allow_storage
@dataclass
class ComplianceAudit:
    id: str
    permit_id: str
    organization_id: str
    submitter: Address
    report: str
    evidence_url: str
    status: str
    outcome: str
    compliance_score: u32
    findings: str
    submitted_at: u64
    resolved_at: u64


@allow_storage
@dataclass
class Remediation:
    id: str
    permit_id: str
    organization_id: str
    submitter: Address
    plan: str
    status: str
    decision: str
    analysis: str
    submitted_at: u64
    resolved_at: u64


class CovenantMesh(gl.Contract):
    owner: Address
    organization_ids: DynArray[str]
    organizations: TreeMap[str, Organization]
    collection_ids: DynArray[str]
    collections: TreeMap[str, Collection]
    request_ids: DynArray[str]
    requests: TreeMap[str, AccessRequest]
    permit_ids: DynArray[str]
    permits: TreeMap[str, Permit]
    usage_ids: DynArray[str]
    usage: TreeMap[str, UsageCheckpoint]
    audit_ids: DynArray[str]
    audits: TreeMap[str, ComplianceAudit]
    remediation_ids: DynArray[str]
    remediations: TreeMap[str, Remediation]
    total_budget_allocated: u256
    total_budget_consumed: u256

    def __init__(self):
        self.owner = gl.message.sender_address
        self.total_budget_allocated = u256(0)
        self.total_budget_consumed = u256(0)
        steward_id = self._create_organization(
            self.owner,
            "Public Interest Data Assembly",
            "STEWARD",
            "Maintain community-governed datasets under explicit consent and public accountability.",
            "Transnational",
        )
        self._create_collection(
            steward_id,
            "Urban Heat Commons",
            "Climate resilience",
            "Block-level temperature, shade, surface, and cooling-access observations from participating neighborhoods.",
            "Use must produce public-interest climate adaptation knowledge and must not expose household or individual-level vulnerability.",
            "Heat mitigation, urban planning, public health research, and non-commercial resilience tools.",
            "Insurance pricing, property speculation, individual profiling, policing, and targeted advertising.",
            "Aggregate outputs to neighborhood scale, suppress sparse cells, publish methods, and delete row-level extracts after analysis.",
            "HIGH",
            180,
            120,
            30,
        )
        self._create_collection(
            steward_id,
            "Coastal Memory Archive",
            "Cultural heritage",
            "Oral histories, place descriptions, and environmental observations contributed by coastal communities.",
            "Interpretation must preserve contributor context, attribution preferences, and community authority over sensitive locations.",
            "Non-commercial heritage research, language preservation, education, and climate-memory studies.",
            "Synthetic voice cloning, commercial tourism targeting, sacred-site mapping, and decontextualized model training.",
            "Quote minimally, honor attribution flags, obscure protected locations, and return derived annotations to the archive.",
            "CRITICAL",
            120,
            90,
            21,
        )
        self._create_collection(
            steward_id,
            "Open Mobility Pulse",
            "Public transport",
            "Privacy-preserving transit reliability and accessibility signals aggregated across city routes.",
            "Results must improve equitable mobility and may not be used to rank, price, or exclude individual riders.",
            "Accessibility analysis, schedule reliability, route planning, and public infrastructure evaluation.",
            "Individual tracking, fare enforcement, commercial scoring, immigration enforcement, and biometric inference.",
            "Use aggregate windows, document bias, prohibit re-identification, and publish accessibility limitations.",
            "MEDIUM",
            260,
            180,
            45,
        )
        self._create_collection(
            steward_id,
            "Community Health Signals",
            "Public health",
            "De-identified symptom, service-access, and environmental context signals governed by participating clinics.",
            "Every use must deliver a direct community health benefit and remain proportionate to the stated research question.",
            "Epidemiology, service capacity planning, environmental health, and publicly funded prevention research.",
            "Employment screening, credit scoring, targeted sales, law enforcement, and individual diagnosis.",
            "Minimum necessary variables, documented ethics review, cell suppression, no linkage attacks, and 30-day deletion.",
            "CRITICAL",
            100,
            60,
            14,
        )
        self._create_collection(
            steward_id,
            "Regenerative Soil Ledger",
            "Agriculture",
            "Farm-contributed soil practices, biodiversity indicators, and seasonal outcomes organized by ecological region.",
            "Use must strengthen farmer knowledge and cannot transfer bargaining power to extractive buyers or input monopolies.",
            "Agroecology research, farmer cooperatives, soil restoration, and open climate adaptation.",
            "Supplier lock-in, land acquisition targeting, punitive underwriting, and proprietary yield prediction.",
            "Regional aggregation, cooperative review before publication, transparent uncertainty, and reciprocal findings.",
            "HIGH",
            150,
            100,
            30,
        )
        self._create_collection(
            steward_id,
            "Learning Access Observatory",
            "Education",
            "Institution-level signals about learning access, assistive technology, and public resource availability.",
            "Analysis must focus on structural access and may not score, rank, or predict outcomes for identifiable learners.",
            "Accessibility policy, resource allocation, assistive technology research, and public program evaluation.",
            "Student profiling, admissions scoring, discipline prediction, surveillance, and commercial lead generation.",
            "Institution-level reporting, protected subgroup thresholds, accessible publication, and no individual inference.",
            "HIGH",
            200,
            140,
            30,
        )

    def _now(self) -> u64:
        return u64(int(datetime.now(timezone.utc).timestamp()))

    def _validate_text(self, value: str, field: str, minimum: int, maximum: int) -> None:
        length = len(value.strip())
        if length < minimum or length > maximum:
            raise gl.vm.UserError(
                f"{ERROR_EXPECTED} {field} must contain {minimum}-{maximum} characters"
            )

    def _create_organization(
        self,
        creator: Address,
        name: str,
        kind: str,
        mission: str,
        jurisdiction: str,
    ) -> str:
        organization_id = f"ORG-{len(self.organization_ids) + 1:03d}"
        self.organization_ids.append(organization_id)
        self.organizations[organization_id] = Organization(
            id=organization_id,
            owner=creator,
            name=name,
            kind=kind,
            mission=mission,
            jurisdiction=jurisdiction,
            reputation=u32(70 if kind == "STEWARD" else 50),
            request_count=u32(0),
            permit_count=u32(0),
            audit_count=u32(0),
            created_at=self._now(),
        )
        return organization_id

    def _create_collection(
        self,
        steward_org_id: str,
        title: str,
        domain: str,
        description: str,
        covenant: str,
        allowed_purposes: str,
        prohibited_uses: str,
        required_safeguards: str,
        sensitivity: str,
        total_budget: int,
        max_retention_days: int,
        audit_interval_days: int,
    ) -> str:
        collection_id = f"COL-{len(self.collection_ids) + 1:03d}"
        self.collection_ids.append(collection_id)
        self.collections[collection_id] = Collection(
            id=collection_id,
            steward_org_id=steward_org_id,
            title=title,
            domain=domain,
            description=description,
            covenant=covenant,
            allowed_purposes=allowed_purposes,
            prohibited_uses=prohibited_uses,
            required_safeguards=required_safeguards,
            sensitivity=sensitivity,
            total_budget=u32(total_budget),
            available_budget=u32(total_budget),
            max_retention_days=u32(max_retention_days),
            audit_interval_days=u32(audit_interval_days),
            permit_count=u32(0),
            status="OPEN",
            created_at=self._now(),
        )
        return collection_id

    def _require_organization(self, organization_id: str) -> Organization:
        if organization_id not in self.organizations:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Organization not found")
        return self.organizations[organization_id]

    def _require_collection(self, collection_id: str) -> Collection:
        if collection_id not in self.collections:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collection not found")
        return self.collections[collection_id]

    def _require_request(self, request_id: str) -> AccessRequest:
        if request_id not in self.requests:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Access request not found")
        return self.requests[request_id]

    def _require_permit(self, permit_id: str) -> Permit:
        if permit_id not in self.permits:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Permit not found")
        return self.permits[permit_id]

    def _bounded(self, value, minimum: int, maximum: int) -> int:
        try:
            return max(minimum, min(maximum, int(value)))
        except Exception:
            raise gl.vm.UserError(f"{ERROR_LLM} Invalid numeric decision")

    def _assess_access(
        self,
        request: AccessRequest,
        organization: Organization,
        collection: Collection,
    ) -> dict:
        def assess() -> dict:
            result = gl.nondet.exec_prompt(
                f"""
You are an independent data-use covenant panel. Decide whether the proposed use
is compatible with the collection's consent conditions. Interpret substance,
not keyword overlap. A plan must have a permitted purpose, concrete safeguards,
proportionate retention, and no prohibited use.

COLLECTION: {collection.title}
DOMAIN: {collection.domain}
SENSITIVITY: {collection.sensitivity}
COVENANT: <covenant>{collection.covenant}</covenant>
ALLOWED PURPOSES: <allowed>{collection.allowed_purposes}</allowed>
PROHIBITED USES: <prohibited>{collection.prohibited_uses}</prohibited>
REQUIRED SAFEGUARDS: <required>{collection.required_safeguards}</required>
MAX RETENTION: {int(collection.max_retention_days)} days
AVAILABLE PRIVACY BUDGET: {int(collection.available_budget)}

TEAM: {organization.name}
TEAM MISSION: {organization.mission}
TEAM REPUTATION: {int(organization.reputation)}/100
REQUEST: {request.title}
PURPOSE: <purpose>{request.purpose}</purpose>
METHODS: <methods>{request.methods}</methods>
PROPOSED SAFEGUARDS: <safeguards>{request.safeguards}</safeguards>
RETENTION: {int(request.retention_days)} days
REQUESTED PRIVACY BUDGET: {int(request.requested_budget)}

Return JSON:
{{
  "verdict": "ALLOW" | "CONDITIONAL" | "DENY",
  "risk_score": integer 0-100 where higher means greater consent risk,
  "allocated_budget": integer 0-{int(request.requested_budget)},
  "conditions": concise enforceable conditions under 500 characters,
  "analysis": concrete policy reasoning under 650 characters
}}

ALLOW requires clear alignment and complete safeguards. CONDITIONAL is allowed
only when explicit enforceable conditions can close limited gaps. DENY when the
purpose is prohibited, safeguards are materially insufficient, retention is
disproportionate, or the plan conflicts with community authority. DENY must
allocate zero. ALLOW or CONDITIONAL must allocate at least one unit and no more
than the available budget.
""",
                response_format="json",
            )
            if not isinstance(result, dict):
                raise gl.vm.UserError(f"{ERROR_LLM} Invalid access assessment")
            verdict = str(result.get("verdict", "")).strip().upper()
            if verdict not in ("ALLOW", "CONDITIONAL", "DENY"):
                raise gl.vm.UserError(f"{ERROR_LLM} Invalid access verdict")
            risk = self._bounded(result.get("risk_score", 100), 0, 100)
            allocation = self._bounded(
                result.get("allocated_budget", 0),
                0,
                min(int(request.requested_budget), int(collection.available_budget)),
            )
            if verdict == "DENY":
                allocation = 0
            elif allocation == 0:
                allocation = min(
                    int(request.requested_budget),
                    int(collection.available_budget),
                )
            return {
                "verdict": verdict,
                "risk_score": risk,
                "allocated_budget": allocation,
                "conditions": str(result.get("conditions", ""))[:500],
                "analysis": str(result.get("analysis", ""))[:650],
            }

        def validate(leader_result: gl.vm.Result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            validator = assess()
            leader = leader_result.calldata
            if leader["verdict"] != validator["verdict"]:
                return False
            if abs(int(leader["risk_score"]) - int(validator["risk_score"])) > 15:
                return False
            if leader["verdict"] != "DENY":
                return abs(
                    int(leader["allocated_budget"])
                    - int(validator["allocated_budget"])
                ) <= max(5, int(request.requested_budget) // 3)
            return True

        return gl.vm.run_nondet_unsafe(assess, validate)

    def _assess_audit(
        self,
        audit: ComplianceAudit,
        permit: Permit,
        collection: Collection,
        organization: Organization,
    ) -> dict:
        remaining = int(permit.allocated_budget) - int(permit.consumed_budget)

        def assess() -> dict:
            result = gl.nondet.exec_prompt(
                f"""
Act as an independent compliance panel for a consent-bound data permit.
Determine whether the report demonstrates compliance with scope, conditions,
budget, and the underlying covenant.

COLLECTION COVENANT: {collection.covenant}
PERMIT SCOPE: {permit.scope}
PERMIT CONDITIONS: {permit.conditions}
ALLOCATED BUDGET: {int(permit.allocated_budget)}
CONSUMED BUDGET: {int(permit.consumed_budget)}
REMAINING BUDGET: {remaining}
TEAM REPUTATION: {int(organization.reputation)}/100
AUDIT REPORT: <report>{audit.report}</report>
PUBLIC EVIDENCE REFERENCE: {audit.evidence_url}

Return JSON:
{{
  "outcome": "COMPLIANT" | "WARNING" | "SUSPEND" | "REVOKE",
  "compliance_score": integer 0-100,
  "findings": specific conclusion under 650 characters
}}

COMPLIANT requires direct reporting against all permit conditions. WARNING means
a limited correctable gap. SUSPEND means material uncertainty or breach requiring
remediation. REVOKE requires clear prohibited use, deliberate concealment,
re-identification, or exhausted budget used beyond authorization.
""",
                response_format="json",
            )
            if not isinstance(result, dict):
                raise gl.vm.UserError(f"{ERROR_LLM} Invalid audit assessment")
            outcome = str(result.get("outcome", "")).strip().upper()
            if outcome not in ("COMPLIANT", "WARNING", "SUSPEND", "REVOKE"):
                raise gl.vm.UserError(f"{ERROR_LLM} Invalid audit outcome")
            return {
                "outcome": outcome,
                "compliance_score": self._bounded(
                    result.get("compliance_score", 0), 0, 100
                ),
                "findings": str(result.get("findings", ""))[:650],
            }

        def validate(leader_result: gl.vm.Result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            validator = assess()
            leader = leader_result.calldata
            if leader["outcome"] != validator["outcome"]:
                return False
            return abs(
                int(leader["compliance_score"])
                - int(validator["compliance_score"])
            ) <= 15

        return gl.vm.run_nondet_unsafe(assess, validate)

    @gl.public.write
    def create_organization(
        self,
        name: str,
        kind: str,
        mission: str,
        jurisdiction: str,
    ) -> str:
        normalized_kind = kind.strip().upper()
        if normalized_kind not in ("STEWARD", "RESEARCH", "AUDITOR"):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Invalid organization kind")
        self._validate_text(name, "Name", 3, 80)
        self._validate_text(mission, "Mission", 30, 600)
        self._validate_text(jurisdiction, "Jurisdiction", 2, 80)
        return self._create_organization(
            gl.message.sender_address,
            name.strip(),
            normalized_kind,
            mission.strip(),
            jurisdiction.strip(),
        )

    @gl.public.write
    def publish_collection(
        self,
        organization_id: str,
        title: str,
        domain: str,
        description: str,
        covenant: str,
        allowed_purposes: str,
        prohibited_uses: str,
        required_safeguards: str,
        sensitivity: str,
        total_budget: u32,
        max_retention_days: u32,
        audit_interval_days: u32,
    ) -> str:
        organization = self._require_organization(organization_id)
        if organization.owner != gl.message.sender_address:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only the organization owner")
        if organization.kind != "STEWARD":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only stewards publish collections")
        self._validate_text(title, "Title", 4, 90)
        self._validate_text(domain, "Domain", 3, 60)
        self._validate_text(description, "Description", 40, 1000)
        self._validate_text(covenant, "Covenant", 80, 1800)
        self._validate_text(allowed_purposes, "Allowed purposes", 30, 1000)
        self._validate_text(prohibited_uses, "Prohibited uses", 30, 1000)
        self._validate_text(required_safeguards, "Required safeguards", 30, 1000)
        normalized_sensitivity = sensitivity.strip().upper()
        if normalized_sensitivity not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Invalid sensitivity")
        if total_budget < u32(10) or total_budget > u32(10000):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Privacy budget must be 10-10000")
        if max_retention_days < u32(1) or max_retention_days > u32(365):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Retention must be 1-365 days")
        if audit_interval_days < u32(7) or audit_interval_days > u32(180):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Audit interval must be 7-180 days")
        return self._create_collection(
            organization_id,
            title.strip(),
            domain.strip(),
            description.strip(),
            covenant.strip(),
            allowed_purposes.strip(),
            prohibited_uses.strip(),
            required_safeguards.strip(),
            normalized_sensitivity,
            int(total_budget),
            int(max_retention_days),
            int(audit_interval_days),
        )

    @gl.public.write
    def submit_access_request(
        self,
        organization_id: str,
        collection_id: str,
        title: str,
        purpose: str,
        methods: str,
        safeguards: str,
        retention_days: u32,
        requested_budget: u32,
    ) -> str:
        organization = self._require_organization(organization_id)
        collection = self._require_collection(collection_id)
        sender = gl.message.sender_address
        if organization.owner != sender:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only the organization owner")
        if organization.kind != "RESEARCH":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Research organization required")
        if collection.status != "OPEN":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collection is not accepting requests")
        self._validate_text(title, "Title", 5, 100)
        self._validate_text(purpose, "Purpose", 60, 1200)
        self._validate_text(methods, "Methods", 80, 1600)
        self._validate_text(safeguards, "Safeguards", 60, 1400)
        if retention_days == u32(0) or retention_days > u32(365):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Invalid retention period")
        if requested_budget == u32(0) or requested_budget > collection.available_budget:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Invalid privacy budget request")
        request_id = f"REQ-{len(self.request_ids) + 1:04d}"
        self.request_ids.append(request_id)
        self.requests[request_id] = AccessRequest(
            id=request_id,
            applicant=sender,
            organization_id=organization_id,
            collection_id=collection_id,
            title=title.strip(),
            purpose=purpose.strip(),
            methods=methods.strip(),
            safeguards=safeguards.strip(),
            retention_days=retention_days,
            requested_budget=requested_budget,
            status="PENDING",
            verdict="",
            risk_score=u32(0),
            allocated_budget=u32(0),
            conditions="",
            analysis="",
            permit_id="",
            submitted_at=self._now(),
            resolved_at=u64(0),
        )
        organization.request_count += u32(1)
        self.organizations[organization_id] = organization
        return request_id

    @gl.public.write
    def resolve_access_request(self, request_id: str) -> None:
        request = self._require_request(request_id)
        if request.status != "PENDING":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Request is not pending")
        organization = self._require_organization(request.organization_id)
        collection = self._require_collection(request.collection_id)
        result = self._assess_access(request, organization, collection)
        request.verdict = result["verdict"]
        request.risk_score = u32(result["risk_score"])
        request.allocated_budget = u32(result["allocated_budget"])
        request.conditions = result["conditions"]
        request.analysis = result["analysis"]
        request.resolved_at = self._now()

        if request.verdict == "DENY":
            request.status = "DENIED"
        else:
            if request.allocated_budget > collection.available_budget:
                raise gl.vm.UserError(f"{ERROR_EXPECTED} Collection budget changed")
            permit_id = f"PER-{len(self.permit_ids) + 1:04d}"
            now = self._now()
            expiry = u64(int(now) + int(request.retention_days) * 86_400)
            self.permit_ids.append(permit_id)
            self.permits[permit_id] = Permit(
                id=permit_id,
                request_id=request.id,
                holder=request.applicant,
                organization_id=request.organization_id,
                collection_id=request.collection_id,
                status="ACTIVE",
                scope=request.purpose,
                conditions=request.conditions,
                allocated_budget=request.allocated_budget,
                consumed_budget=u32(0),
                issued_at=now,
                expires_at=expiry,
                next_audit_due=u64(
                    int(now) + int(collection.audit_interval_days) * 86_400
                ),
                audit_count=u32(0),
            )
            request.permit_id = permit_id
            request.status = (
                "APPROVED" if request.verdict == "ALLOW" else "CONDITIONAL"
            )
            collection.available_budget -= request.allocated_budget
            collection.permit_count += u32(1)
            organization.permit_count += u32(1)
            organization.reputation = u32(
                min(100, int(organization.reputation) + (5 if request.verdict == "ALLOW" else 2))
            )
            self.total_budget_allocated += u256(int(request.allocated_budget))

        self.requests[request.id] = request
        self.collections[collection.id] = collection
        self.organizations[organization.id] = organization

    @gl.public.write
    def record_usage(
        self,
        permit_id: str,
        units: u32,
        purpose_note: str,
        artifact_url: str,
    ) -> str:
        permit = self._require_permit(permit_id)
        if permit.holder != gl.message.sender_address:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only the permit holder")
        if permit.status != "ACTIVE":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Permit is not active")
        self._validate_text(purpose_note, "Purpose note", 30, 700)
        if artifact_url != "" and not artifact_url.startswith("https://"):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Artifact URL must use HTTPS")
        remaining = int(permit.allocated_budget) - int(permit.consumed_budget)
        if units == u32(0) or int(units) > remaining:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Usage exceeds remaining budget")
        checkpoint_id = f"USE-{len(self.usage_ids) + 1:04d}"
        self.usage_ids.append(checkpoint_id)
        self.usage[checkpoint_id] = UsageCheckpoint(
            id=checkpoint_id,
            permit_id=permit_id,
            organization_id=permit.organization_id,
            units=units,
            purpose_note=purpose_note.strip(),
            artifact_url=artifact_url.strip(),
            recorded_at=self._now(),
        )
        permit.consumed_budget += units
        if permit.consumed_budget == permit.allocated_budget:
            permit.status = "EXHAUSTED"
        self.total_budget_consumed += u256(int(units))
        self.permits[permit_id] = permit
        return checkpoint_id

    @gl.public.write
    def submit_audit(
        self,
        permit_id: str,
        report: str,
        evidence_url: str,
    ) -> str:
        permit = self._require_permit(permit_id)
        if permit.holder != gl.message.sender_address:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only the permit holder")
        if permit.status not in ("ACTIVE", "EXHAUSTED"):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Permit cannot be audited")
        self._validate_text(report, "Audit report", 100, 2200)
        if not evidence_url.startswith("https://"):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Evidence URL must use HTTPS")
        audit_id = f"AUD-{len(self.audit_ids) + 1:04d}"
        self.audit_ids.append(audit_id)
        self.audits[audit_id] = ComplianceAudit(
            id=audit_id,
            permit_id=permit_id,
            organization_id=permit.organization_id,
            submitter=gl.message.sender_address,
            report=report.strip(),
            evidence_url=evidence_url.strip(),
            status="PENDING",
            outcome="",
            compliance_score=u32(0),
            findings="",
            submitted_at=self._now(),
            resolved_at=u64(0),
        )
        return audit_id

    @gl.public.write
    def resolve_audit(self, audit_id: str) -> None:
        if audit_id not in self.audits:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Audit not found")
        audit = self.audits[audit_id]
        if audit.status != "PENDING":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Audit is not pending")
        permit = self._require_permit(audit.permit_id)
        collection = self._require_collection(permit.collection_id)
        organization = self._require_organization(permit.organization_id)
        result = self._assess_audit(audit, permit, collection, organization)
        audit.outcome = result["outcome"]
        audit.compliance_score = u32(result["compliance_score"])
        audit.findings = result["findings"]
        audit.status = "RESOLVED"
        audit.resolved_at = self._now()
        permit.audit_count += u32(1)
        organization.audit_count += u32(1)

        if audit.outcome == "COMPLIANT":
            organization.reputation = u32(min(100, int(organization.reputation) + 6))
            permit.next_audit_due = u64(
                int(self._now()) + int(collection.audit_interval_days) * 86_400
            )
        elif audit.outcome == "WARNING":
            organization.reputation = u32(max(0, int(organization.reputation) - 3))
        elif audit.outcome == "SUSPEND":
            permit.status = "SUSPENDED"
            organization.reputation = u32(max(0, int(organization.reputation) - 12))
        else:
            permit.status = "REVOKED"
            organization.reputation = u32(max(0, int(organization.reputation) - 25))

        self.audits[audit_id] = audit
        self.permits[permit.id] = permit
        self.organizations[organization.id] = organization

    @gl.public.write
    def submit_remediation(self, permit_id: str, plan: str) -> str:
        permit = self._require_permit(permit_id)
        if permit.holder != gl.message.sender_address:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only the permit holder")
        if permit.status != "SUSPENDED":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Permit is not suspended")
        self._validate_text(plan, "Remediation plan", 100, 1800)
        remediation_id = f"REM-{len(self.remediation_ids) + 1:04d}"
        self.remediation_ids.append(remediation_id)
        self.remediations[remediation_id] = Remediation(
            id=remediation_id,
            permit_id=permit_id,
            organization_id=permit.organization_id,
            submitter=gl.message.sender_address,
            plan=plan.strip(),
            status="PENDING",
            decision="",
            analysis="",
            submitted_at=self._now(),
            resolved_at=u64(0),
        )
        return remediation_id

    @gl.public.write
    def resolve_remediation(self, remediation_id: str) -> None:
        if remediation_id not in self.remediations:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Remediation not found")
        remediation = self.remediations[remediation_id]
        if remediation.status != "PENDING":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Remediation is not pending")
        permit = self._require_permit(remediation.permit_id)
        if permit.status != "SUSPENDED":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Permit is no longer suspended")
        plan = remediation.plan
        conditions = permit.conditions

        def assess() -> dict:
            result = gl.nondet.exec_prompt(
                f"""
Evaluate whether this remediation plan concretely resolves the suspended data
permit's compliance conditions.
PERMIT CONDITIONS: {conditions}
REMEDIATION PLAN: <plan>{plan}</plan>
Return JSON: {{"decision":"RESTORE"|"REJECT","analysis":"reason under 500 characters"}}
RESTORE only for specific, verifiable corrective actions, responsible owners,
deadlines, deletion or containment where relevant, and future monitoring.
""",
                response_format="json",
            )
            if not isinstance(result, dict):
                raise gl.vm.UserError(f"{ERROR_LLM} Invalid remediation assessment")
            decision = str(result.get("decision", "")).strip().upper()
            if decision not in ("RESTORE", "REJECT"):
                raise gl.vm.UserError(f"{ERROR_LLM} Invalid remediation decision")
            return {
                "decision": decision,
                "analysis": str(result.get("analysis", ""))[:500],
            }

        def validate(leader_result: gl.vm.Result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            validator = assess()
            return leader_result.calldata["decision"] == validator["decision"]

        result = gl.vm.run_nondet_unsafe(assess, validate)
        remediation.decision = result["decision"]
        remediation.analysis = result["analysis"]
        remediation.status = "RESOLVED"
        remediation.resolved_at = self._now()
        if remediation.decision == "RESTORE":
            permit.status = "ACTIVE"
            organization = self._require_organization(permit.organization_id)
            organization.reputation = u32(min(100, int(organization.reputation) + 4))
            self.organizations[organization.id] = organization
        self.remediations[remediation_id] = remediation
        self.permits[permit.id] = permit

    @gl.public.view
    def get_overview(self) -> dict:
        active_permits = 0
        pending_requests = 0
        pending_audits = 0
        suspended_permits = 0
        for permit_id in self.permit_ids:
            status = self.permits[permit_id].status
            if status == "ACTIVE":
                active_permits += 1
            elif status == "SUSPENDED":
                suspended_permits += 1
        for request_id in self.request_ids:
            if self.requests[request_id].status == "PENDING":
                pending_requests += 1
        for audit_id in self.audit_ids:
            if self.audits[audit_id].status == "PENDING":
                pending_audits += 1
        return {
            "organizations": len(self.organization_ids),
            "collections": len(self.collection_ids),
            "requests": len(self.request_ids),
            "pending_requests": pending_requests,
            "permits": len(self.permit_ids),
            "active_permits": active_permits,
            "suspended_permits": suspended_permits,
            "usage_checkpoints": len(self.usage_ids),
            "audits": len(self.audit_ids),
            "pending_audits": pending_audits,
            "remediations": len(self.remediation_ids),
            "budget_allocated": self.total_budget_allocated,
            "budget_consumed": self.total_budget_consumed,
        }

    @gl.public.view
    def get_organizations(self) -> list:
        return [self.organizations[item_id] for item_id in self.organization_ids]

    @gl.public.view
    def get_collections(self) -> list:
        return [self.collections[item_id] for item_id in self.collection_ids]

    @gl.public.view
    def get_requests(self) -> list:
        return [self.requests[item_id] for item_id in self.request_ids]

    @gl.public.view
    def get_permits(self) -> list:
        return [self.permits[item_id] for item_id in self.permit_ids]

    @gl.public.view
    def get_usage(self) -> list:
        return [self.usage[item_id] for item_id in self.usage_ids]

    @gl.public.view
    def get_audits(self) -> list:
        return [self.audits[item_id] for item_id in self.audit_ids]

    @gl.public.view
    def get_remediations(self) -> list:
        return [self.remediations[item_id] for item_id in self.remediation_ids]

