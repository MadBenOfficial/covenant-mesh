import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";

const root = process.cwd();
const env = readFileSync(resolve(root, "../.env"), "utf8");
const privateKey = env
  .split(/\r?\n/)
  .find((line) => line.startsWith("GENLAYER_PRIVATE_KEY_1="))
  ?.slice("GENLAYER_PRIVATE_KEY_1=".length)
  .trim();
if (!privateKey) throw new Error("GENLAYER_PRIVATE_KEY_1 is missing");

const account = createAccount(privateKey);
const client = createClient({ chain: studionet, account });
const code = new Uint8Array(
  readFileSync(resolve(root, "contracts/covenant_mesh.py")),
);

console.log(`Deploying Covenant Mesh from ${account.address}...`);
const hash = await client.deployContract({ code, args: [] });
console.log(`Submitted ${hash}`);
const receipt = await client.waitForTransactionReceipt({
  hash,
  status: TransactionStatus.FINALIZED,
  retries: 240,
  interval: 3_000,
});
const leader = receipt.consensus_data?.leader_receipt?.[0];
if (leader?.execution_result !== "SUCCESS") {
  throw new Error(`Deployment failed: ${JSON.stringify(receipt)}`);
}
const address = receipt.data?.contract_address;
if (!address) throw new Error("Deployment returned no contract address");

const deployment = {
  network: "studionet",
  chainId: 61999,
  contractAddress: address,
  transactionHash: hash,
  deployer: account.address,
  explorer: "https://explorer-studio.genlayer.com",
  deployedAt: new Date().toISOString(),
};
mkdirSync(resolve(root, "deployments"), { recursive: true });
writeFileSync(
  resolve(root, "deployments/studionet.json"),
  `${JSON.stringify(deployment, null, 2)}\n`,
);
mkdirSync(resolve(root, "app"), { recursive: true });
writeFileSync(
  resolve(root, "app/.env.production"),
  `VITE_CONTRACT_ADDRESS=${address}\nVITE_EXPLORER_URL=https://explorer-studio.genlayer.com\n`,
);
console.log(JSON.stringify(deployment, null, 2));
