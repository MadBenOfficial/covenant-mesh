import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const root = process.cwd();
const deployment = JSON.parse(
  readFileSync(resolve(root, "deployments/studionet.json"), "utf8"),
);
const seed = JSON.parse(
  readFileSync(resolve(root, "deployments/seed-studionet.json"), "utf8"),
);
const client = createClient({ chain: studionet });
const address = deployment.contractAddress;
const wait = (ms) => new Promise((done) => setTimeout(done, ms));
async function read(functionName, args = []) {
  for (let attempt = 1; attempt <= 12; attempt += 1) {
    try {
      return await client.readContract({
        address,
        functionName,
        args,
        jsonSafeReturn: true,
      });
    } catch (error) {
      const message = String(error?.details || error?.message || error);
      const retryable =
        message.includes("Server busy") ||
        message.includes("-32028") ||
        message.includes("429");
      if (!retryable || attempt === 12) throw error;
      await wait(attempt * 1_500);
    }
  }
}

const overview = await read("get_overview");
const organizations = await read("get_organizations");
const collections = await read("get_collections");
const requests = await read("get_requests");
const permits = await read("get_permits");
const audits = await read("get_audits");
const remediations = await read("get_remediations");

const failures = [];
const expect = (condition, message) => {
  if (!condition) failures.push(message);
};
expect(address === seed.contractAddress, "Deployment and seed addresses differ");
expect(collections.length === 6, "Expected six governed collections");
expect(organizations.length >= 4, "Expected four onboarded organizations");
expect(requests.length >= 6, "Expected six access requests");
expect(permits.length >= 2, "Expected two consensus-issued permits");
expect(audits.length >= 1, "Expected a submitted compliance audit");
expect(remediations.length >= 1, "Expected a submitted remediation plan");
expect(seed.transactions.every((item) => item.succeeded), "Seed receipt failure found");

const permitSchedules = [];
for (const permit of permits) {
  permitSchedules.push(await read("get_permit_status", [permit.id]));
}

if (failures.length) {
  throw new Error(`Live verification failed:\n- ${failures.join("\n- ")}`);
}

console.log(
  JSON.stringify(
    {
      verifiedAt: new Date().toISOString(),
      network: deployment.network,
      contractAddress: address,
      overview,
      acceptedSeedTransactions: seed.transactions.length,
      permitSchedules,
    },
    null,
    2,
  ),
);
