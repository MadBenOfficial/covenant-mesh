import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { ExecutionResult, TransactionStatus } from "genlayer-js/types";

const root = process.cwd();
const deployment = JSON.parse(
  readFileSync(resolve(root, "deployments/studionet.json"), "utf8"),
);
const env = readFileSync(resolve(root, "../.env"), "utf8");
const privateKey = env
  .split(/\r?\n/)
  .find((line) => line.startsWith("GENLAYER_PRIVATE_KEY_1="))
  ?.slice("GENLAYER_PRIVATE_KEY_1=".length)
  .trim();
if (!privateKey) throw new Error("GENLAYER_PRIVATE_KEY_1 is missing");

const account = createAccount(privateKey);
const expectedSeeder = "0x659718Bc33FB7CD9f7D111F5270EEbca58e18c3D";
if (account.address.toLowerCase() !== expectedSeeder.toLowerCase()) {
  throw new Error(`Account 1 mismatch: expected ${expectedSeeder}`);
}
const client = createClient({ chain: studionet, account });
const address = deployment.contractAddress;
const transactions = [];
const wait = (ms) => new Promise((done) => setTimeout(done, ms));
const details = (error) =>
  String(error?.details || error?.shortMessage || error?.message || error);

async function retry(operation, attempts = 24) {
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await operation();
    } catch (error) {
      const message = details(error);
      if (
        attempt === attempts ||
        (!message.includes("Server busy") &&
          !message.includes("-32028") &&
          !message.includes("429"))
      ) {
        throw error;
      }
      await wait(attempt * 2_000);
    }
  }
}

const read = (functionName, args = []) =>
  retry(() =>
    client.readContract({
      address,
      functionName,
      args,
      jsonSafeReturn: true,
    }),
  );

async function write(functionName, args = []) {
  const hash = await retry(() =>
    client.writeContract({ address, functionName, args }),
  );
  console.log(`${functionName}: ${hash}`);
  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.ACCEPTED,
    retries: 120,
    interval: 3_000,
  });
  const succeeded =
    receipt.txExecutionResultName === ExecutionResult.FINISHED_WITH_RETURN ||
    receipt.consensus_data?.leader_receipt?.[0]?.execution_result === "SUCCESS";
  transactions.push({ functionName, hash, succeeded });
  if (!succeeded) {
    throw new Error(`${functionName} failed: ${JSON.stringify(receipt)}`);
  }
  await wait(2_500);
  return receipt;
}

const organizationBlueprints = [
  [
    "Reciprocal Systems Lab",
    "Produce reproducible public-interest analysis while returning methods, limitations, and community-readable findings to every contributing data cooperative.",
    "Morocco and European Union",
  ],
  [
    "Civic Access Observatory",
    "Audit whether essential public systems remain accessible across neighborhoods while publishing reproducible methods and community-readable limitations.",
    "North Africa",
  ],
  [
    "Commons Evidence Unit",
    "Translate cooperative environmental records into independently reviewable public evidence without exposing members or enabling commercial scoring.",
    "Mediterranean cooperatives",
  ],
];

let organizations = await read("get_organizations");
for (const [name, mission, jurisdiction] of organizationBlueprints) {
  if (organizations.some((item) => item.name === name)) continue;
  await write("create_organization", [
    name,
    "RESEARCH",
    mission,
    jurisdiction,
  ]);
  organizations = await read("get_organizations");
}

const proposals = [
  [
    "Reciprocal Systems Lab",
    "COL-001",
    "Cooling access inequality atlas",
    "Measure whether public cooling resources reach neighborhoods with the highest documented heat exposure and return an accessible planning atlas to participating communities.",
    "Join heat observations to public facility service areas, aggregate every output to neighborhood scale, suppress sparse cells, compare daytime and nighttime access, and publish uncertainty with the method.",
    "Use only necessary fields, prohibit row-level exports, suppress cells below twenty observations, maintain an immutable access log, and delete working extracts within thirty days.",
    30,
    26,
  ],
  [
    "Civic Access Observatory",
    "COL-003",
    "Step-free transit reliability study",
    "Evaluate whether step-free routes remain reliable during service disruptions and produce public recommendations for accessible scheduling and infrastructure investment.",
    "Analyze route-level reliability windows, compare published accessibility status with aggregate service signals, avoid rider-level linkage, and publish only corridor-level results.",
    "Use aggregate windows, prohibit re-identification, document missingness and route bias, retain extracts for forty-five days, and publish an accessible limitations statement.",
    45,
    34,
  ],
  [
    "Commons Evidence Unit",
    "COL-005",
    "Reciprocal soil restoration benchmark",
    "Compare regional soil-restoration practices without ranking individual farms and return cooperative-reviewed findings for open farmer education.",
    "Group observations by ecological region and practice family, publish uncertainty bands, exclude commercial yield forecasts, and route every draft through cooperative review.",
    "Aggregate all farm records, remove direct identifiers, prohibit buyer-facing scoring, maintain review logs, and delete analytical extracts after sixty days.",
    60,
    28,
  ],
  [
    "Reciprocal Systems Lab",
    "COL-002",
    "Heat refuge operating-hours audit",
    "Test whether published refuge hours match periods of documented heat risk and return a public gap register to municipal stewards.",
    "Compare aggregate risk windows with facility schedules, suppress sparse observations, publish uncertainty, and retain no resident-level timeline.",
    "Use aggregate time windows, prohibit identity linkage, log every query, publish limitations, and delete working extracts within thirty days.",
    30,
    22,
  ],
  [
    "Civic Access Observatory",
    "COL-004",
    "Accessible interchange continuity review",
    "Identify where step-free journeys break across interchange boundaries and publish independently reproducible service recommendations.",
    "Join only corridor-level accessibility and disruption windows, avoid passenger identifiers, and report uncertainty for every interchange.",
    "Prohibit rider-level linkage, aggregate all outputs, document missingness, retain extracts for forty-five days, and publish an accessible report.",
    45,
    30,
  ],
  [
    "Commons Evidence Unit",
    "COL-006",
    "Cooperative water resilience brief",
    "Compare water-retention practices across ecological zones while protecting individual farms and returning an open educational brief.",
    "Group records by ecological zone and practice family, publish uncertainty bands, exclude commercial ranking, and require cooperative review.",
    "Remove direct identifiers, prohibit farm scoring, aggregate sparse groups, log analysis, and delete working extracts after sixty days.",
    60,
    24,
  ],
];

let requests = await read("get_requests");
for (let index = requests.length; index < proposals.length; index += 1) {
  const [organizationName, ...request] = proposals[index];
  const organization = organizations.find(
    (item) => item.name === organizationName,
  );
  if (!organization) throw new Error(`Missing organization ${organizationName}`);
  await write("submit_access_request", [organization.id, ...request]);
}

requests = await read("get_requests");
for (const request of requests.slice(0, 2)) {
  if (request.status !== "PENDING") continue;
  try {
    await write("resolve_access_request", [request.id]);
  } catch (error) {
    console.warn(`${request.id} remains pending: ${details(error)}`);
  }
}

let permits = await read("get_permits");
if (permits.length) {
  const first = permits[0];
  const usage = await read("get_usage");
  if (!usage.some((item) => item.permit_id === first.id)) {
    const remaining =
      Number(first.allocated_budget) - Number(first.consumed_budget);
    if (remaining > 1) {
      await write("record_usage", [
        first.id,
        Math.min(6, remaining),
        "Produced the first neighborhood-level aggregate, suppressed sparse cells, and logged every query against the permit conditions.",
        "https://github.com/MadBenOfficial/covenant-mesh",
      ]);
    }
  }

  const audits = await read("get_audits");
  if (!audits.some((item) => item.permit_id === first.id)) {
    await write("submit_audit", [
      first.id,
      "The internal review found that two temporary row-level extracts lack verified deletion receipts and that several access-log entries remain unreconciled. Publication and further processing are paused while the team contains the workspace, verifies deletion, and completes independent log review. This material uncertainty requires formal remediation before use resumes.",
      "https://github.com/MadBenOfficial/covenant-mesh",
    ]);
  }

  let currentAudits = await read("get_audits");
  const firstAudit = currentAudits.find((item) => item.permit_id === first.id);
  if (firstAudit?.status === "PENDING") {
    await write("resolve_audit", [firstAudit.id]);
  }

  permits = await read("get_permits");
  const auditedPermit = permits.find((item) => item.id === first.id);
  if (auditedPermit?.status === "SUSPENDED") {
    let remediations = await read("get_remediations");
    let remediation = remediations.find((item) => item.permit_id === first.id);
    if (!remediation) {
      await write("submit_remediation", [
        first.id,
        "Within twenty-four hours the security lead will delete both temporary extracts, publish signed deletion receipts, and reconcile every access-log entry. An independent reviewer will attest to containment within forty-eight hours. Export controls will be revalidated before access resumes, with weekly log review and public exception reporting for the remainder of the permit.",
      ]);
      remediations = await read("get_remediations");
      remediation = remediations.find((item) => item.permit_id === first.id);
    }
    if (remediation?.status === "PENDING") {
      await write("resolve_remediation", [remediation.id]);
    }
  }
}

const snapshot = {
  seededAt: new Date().toISOString(),
  account: account.address,
  contractAddress: address,
  overview: await read("get_overview"),
  transactions,
};
writeFileSync(
  resolve(root, "deployments/seed-studionet.json"),
  `${JSON.stringify(snapshot, null, 2)}\n`,
);
console.log(JSON.stringify(snapshot, null, 2));
