// server.ts
import http from "http";
import dotenv from "dotenv";
import { LitNodeClient } from "@lit-protocol/lit-node-client";
import { LIT_NETWORK, LIT_ABILITY, LIT_RPC } from "@lit-protocol/constants";
import { LitActionResource, LitPKPResource } from "@lit-protocol/auth-helpers";
import { LitContracts } from "@lit-protocol/contracts-sdk";
import { EthWalletProvider } from "@lit-protocol/lit-auth-client";
import * as ethers from "ethers";
import { litActionCode } from "./litAction.js";

dotenv.config();

class GasSponsorServer {
  private provider: ethers.providers.Provider;
  private sponsorWallet: ethers.Wallet;

  constructor(rpcUrl: string, sponsorPrivateKey: string) {
    this.provider = new ethers.providers.JsonRpcProvider(rpcUrl);
    this.sponsorWallet = new ethers.Wallet(sponsorPrivateKey, this.provider);
  }

  async createServer() {
    const { pk1, pk2 } = process.env;
    const NETWORK = LIT_NETWORK.DatilDev;

    const litNodeClient = new LitNodeClient({
      litNetwork: NETWORK,
      debug: false,
    });

    const provider = new ethers.providers.JsonRpcProvider(LIT_RPC.CHRONICLE_YELLOWSTONE);
    const ethersWallet = new ethers.Wallet(pk1!, provider);
    await litNodeClient.connect();

    const litContracts = new LitContracts({
      signer: ethersWallet,
      network: NETWORK,
      debug: false,
    });
    await litContracts.connect();

    const mintResult = await litContracts.pkpNftContractUtils.write.mint();
    const pkp = mintResult.pkp;

    const authMethod = await EthWalletProvider.authenticate({
      signer: ethersWallet,
      litNodeClient,
    });

    const tx = await ethersWallet.sendTransaction({
      to: pkp.ethAddress,
      value: ethers.utils.parseEther("0.0001"),
    });
    console.log("Transaction hash:", tx.hash);

    const balance = await provider.getBalance(pkp.ethAddress);
    console.log(`Balance of ${pkp.ethAddress}:`, ethers.utils.formatEther(balance));

    const pkpSessionSigs = await litNodeClient.getPkpSessionSigs({
      pkpPublicKey: pkp.publicKey!,
      chain: "ethereum",
      authMethods: [authMethod],
      resourceAbilityRequests: [
        {
          resource: new LitActionResource("*"),
          ability: LIT_ABILITY.LitActionExecution,
        },
        {
          resource: new LitPKPResource("*"),
          ability: LIT_ABILITY.PKPSigning,
        },
      ],
    });

    const server = http.createServer(async (req, res) => {
      if (req.method === "POST" && req.url === "/submit-transaction") {
        let body = "";

        req.on("data", (chunk) => {
          body += chunk.toString();
        });

        req.on("end", async () => {
          try {
            const { signedTx, from, estimate } = JSON.parse(body);

            // Optionally, perform additional checks here, such as verifying the sender
            console.log("Estimate:", estimate);

            // Submit the signed transaction directly to the network
            const txResponse = await this.provider.sendTransaction(signedTx);

            // await litNodeClient.executeJs({
            //     sessionSigs: pkpSessionSigs,
            //     code: litActionCode,
            //     jsParams: { publicKey: pkp.publicKey!, signedTx : signedTx, nonce : await provider.getTransactionCount(from)},
            //   });

            // Wait for the transaction to be mined (optional)
            // const receipt = await txResponse.wait();

            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(
              JSON.stringify({
                txHash: txResponse.hash,
                status: "Transaction submitted successfully",
              })
            );
          } catch (error: any) {
            console.error("Server transaction error:", error);
            res.writeHead(500, { "Content-Type": "application/json" });
            res.end(
              JSON.stringify({
                error: "Failed to submit transaction",
                details: error.message || error.toString(),
              })
            );
          }
        });
      } else {
        res.writeHead(404, { "Content-Type": "text/plain" });
        res.end("Not Found");
      }
    });

    return server;
  }

  async start(port: number = 3001) {
    try {
      const server = await this.createServer();
      server.listen(port, () => {
        console.log(`Gas sponsorship server running on port ${port}`);
      });
    } catch (error: any) {
      console.error("Failed to start server:", error);
    }
  }
}

const { pk1 } = process.env;

// Example usage
function main() {
  if (!pk1) {
    throw new Error("Sponsor private key (pk1) not set in environment variables.");
  }

  const server = new GasSponsorServer(
    "https://yellowstone-rpc.litprotocol.com",
    pk1
  );
  server.start();
}

main();
