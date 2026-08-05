# Covenant Mesh

## A Live Charter for Governed Data Access

> Data permission is not a checkbox. It is a durable relationship between a
> steward, a declared purpose, a bounded method, and an accountable user.

[Open the live mesh](https://madbenofficial.github.io/covenant-mesh/) |
[Inspect the contract](https://explorer-studio.genlayer.com/address/0x18B57ffAc641623783bE40C066cAff3c369505e7) |
[Review the source](https://github.com/MadBenOfficial/covenant-mesh)

![Covenant Mesh live permission graph](screenshot.png)

## Charter Summary

Covenant Mesh is a GenLayer-native coordination protocol for communities and
research organizations that need enforceable rules around collective data.
Stewards publish covenants containing purpose, prohibition, retention,
safeguard, audit, and privacy-budget terms. Researchers submit a bounded method
against a specific collection. GenLayer validators interpret whether that method
fits the covenant and persist a consequential decision on-chain.

The result is not disposable AI commentary. Consensus can create a permit,
allocate a privacy budget, set expiry and audit deadlines, suspend use, revoke
rights, or restore access after remediation.

## Live StudioNet Registry

| Instrument | Public reference |
| --- | --- |
| Network | GenLayer StudioNet, chain `61999` |
| Intelligent Contract | [`0x18B57ffAc641623783bE40C066cAff3c369505e7`](https://explorer-studio.genlayer.com/address/0x18B57ffAc641623783bE40C066cAff3c369505e7) |
| Deployment transaction | [`0x62f517...737501`](https://explorer-studio.genlayer.com/tx/0x62f51723e5cf24b2c9dac840225a5a914adf7daa13a132789f099c9e08737501) |
| Deployer | `0x659718Bc33FB7CD9f7D111F5270EEbca58e18c3D` |
| GitHub account | [`MadBenOfficial`](https://github.com/MadBenOfficial) |
| Live application | [madbenofficial.github.io/covenant-mesh](https://madbenofficial.github.io/covenant-mesh/) |

The current contract contains real StudioNet state:

| State | Count |
| --- | ---: |
| Covenanted collections | 6 |
| Organizations | 4 |
| Access requests | 6 |
| Active permits | 2 |
| Allocated privacy units | 60 |
| Consumed privacy units | 6 |
| Usage checkpoints | 1 |
| Compliance audits | 1 |
| Remediation decisions | 1 |
| Suspended permits | 1 |

Sixteen successful post-deployment transactions created this state. Their
function names, hashes, signer, contract address, and execution result are
preserved in [`deployments/seed-studionet.json`](deployments/seed-studionet.json).

## Protocol Articles

### I. Stewardship

A steward organization publishes the rules attached to a collection. The
contract keeps those rules beside the collection instead of separating policy
from access.

### II. Purpose-bound requests

A research organization declares the intended purpose, analytical method,
safeguards, retention window, and requested privacy budget. Ownership checks
prevent one wallet from submitting on behalf of another organization.

### III. Intelligent adjudication

Validators independently compare the request with the covenant. Access
consensus normalizes outcomes to `ALLOW`, `CONDITIONAL`, or `DENY`; evidence
review normalizes outcomes to `COMPLIANT`, `WARNING`, `SUSPEND`, or `REVOKE`.
Malformed validator output rotates consensus instead of mutating state.

### IV. Accountable use

Issued permits expose budget, expiry, holder, conditions, and audit schedule.
Each usage checkpoint consumes budget and attaches a public artifact. Exhausted
or suspended permits cannot silently continue. Every permit-sensitive write
materializes its time schedule first: expiry is terminal, while an overdue audit
changes the effective state to `AUDIT_OVERDUE` and blocks further usage.

### V. Audit and remediation

Permit holders submit evidence against the covenant. A warning can preserve the
permit with findings; suspension or revocation changes durable rights.
Remediation creates a new reviewable protocol event rather than editing history.
An approved remediation resets the audit clock and restores only unexpired
rights; a rejected plan leaves the permit suspended. Duplicate pending audits
and remediation plans are rejected on-chain.

## Reviewer Remediation Matrix

| Requested behavior | Contract enforcement | Application path |
| --- | --- | --- |
| Wallet must not invoke `wallet_getSnaps` | Browser client binds the injected EIP-1193 provider directly and never calls `client.connect()` | Landing and persistent header wallet controls |
| Usable organization onboarding | `create_organization` records wallet ownership; request submission enforces that owner | First-connect onboarding band, create form, and active-organization selector |
| Submitted remediation methods | Holder-only `submit_remediation`; permissionless `resolve_remediation` through validator consensus | Suspended-permit action plus remediation ledger and consensus button |
| Permit expiry | Every sensitive write computes and enforces `EXPIRED`; `sync_permit_status` persists it | Effective status, deadline warning, and Enforce action |
| Overdue audits | Usage is rejected as `AUDIT_OVERDUE`; audit submission remains available as the recovery path | Overdue badge and enabled Submit audit action |

## Application Route

1. Connect a wallet through the landing membrane.
2. Inspect collections, stewards, safeguards, and remaining budgets.
3. Create or select an organization owned by the connected wallet.
4. Submit a bounded access request.
5. Follow the animated wallet and validator lifecycle.
6. Record permitted use, submit an overdue audit, or remediate a suspension.
7. Read the persisted verdict and its `/tx/` StudioNet receipt.

Wallet connection persists across refreshes. Every transaction surface blocks
duplicate submission, displays a waiting animation while pending, preserves a
readable terminal result, and links to the current StudioNet explorer.

## Repository Map

| Path | Responsibility |
| --- | --- |
| `contracts/covenant_mesh.py` | Intelligent contract, storage, authorization, consensus, budgets, audits |
| `tests/direct/` | Access-control, lifecycle, accounting, and validator-output tests |
| `scripts/deploy-studionet.mjs` | Account-1 deployment and public metadata generation |
| `scripts/seed-studionet.mjs` | Idempotent live-state creation with receipt verification and throttling |
| `deployments/` | Public deployment and transaction manifests |
| `app/` | Wallet-gated Vue application reading and writing StudioNet |

The contract pins:
`py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.

## Verification

```bash
genvm-lint check contracts/covenant_mesh.py
pytest tests/direct -q
cd app
corepack pnpm install
corepack pnpm run build
```

Current verification baseline: GenVM lint passed, contract schema validation
passed, all `11` direct tests passed, and the production Vue build completed.

`corepack pnpm run seed` is an operator command for a fresh deployment. It
writes real StudioNet state and is intentionally excluded from routine checks.

## Key Custody

The browser contains only public network configuration. Deployment and seeding
scripts read `GENLAYER_PRIVATE_KEY_1` from the ignored workspace `.env`; the key
is never written to deployment manifests, frontend code, screenshots, or Git.
The tracked environment example contains only the public contract address and
explorer URL.

The live fixture state was created entirely by account 1,
`0x659718Bc33FB7CD9f7D111F5270EEbca58e18c3D`. This seeded identity is useful for
reviewing its holder-only actions, but it is not a hidden operator requirement:
any wallet can onboard an organization, owners submit their own requests and
evidence, and consensus resolution methods are permissionless.

MIT licensed.
