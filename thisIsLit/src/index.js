// Filename: index.ts
import { LitNodeClient } from "@lit-protocol/lit-node-client";
import { LIT_NETWORK, LIT_ABILITY, LIT_RPC } from "@lit-protocol/constants";
import { LitActionResource, LitPKPResource } from "@lit-protocol/auth-helpers";
import { LitContracts } from "@lit-protocol/contracts-sdk";
import { EthWalletProvider } from "@lit-protocol/lit-auth-client";
import * as ethers from "ethers";
import { litActionCode } from "./litAction.js";
import http from 'http';
import dotenv from 'dotenv';
// Load environment variables at the very beginning
dotenv.config();
const { pk1, pk2 } = process.env;
const NETWORK = LIT_NETWORK.DatilDev;
// Ensure that pk1 is provided
if (!pk1) {
    throw new Error('Sponsor private key (pk1) not set in environment variables.');
}
class GasSponsorServer {
    constructor(rpcUrl, sponsorPrivateKey) {
        this.provider = new ethers.providers.JsonRpcProvider(rpcUrl);
        this.sponsorWallet = new ethers.Wallet(sponsorPrivateKey, this.provider);
        this.litNodeClient = new LitNodeClient({
            litNetwork: NETWORK,
            debug: false,
        });
    }
    // Asynchronous initialization method
    async init() {
        const provider = new ethers.providers.JsonRpcProvider(LIT_RPC.CHRONICLE_YELLOWSTONE);
        const ethersWallet = new ethers.Wallet(this.sponsorWallet.privateKey, provider);
        try {
            // Connect to Lit Node
            await this.litNodeClient.connect();
            console.log("Connected to Lit Node.");
            // Initialize Lit Contracts
            this.litContracts = new LitContracts({
                signer: ethersWallet,
                network: NETWORK,
                debug: false,
            });
            await this.litContracts.connect();
            console.log("Connected to Lit Contracts.");
            // Mint PKP NFT
            const mintResult = await this.litContracts.pkpNftContractUtils.write.mint();
            this.pkp = mintResult.pkp;
            console.log("PKP NFT minted:", this.pkp);
            // Authenticate with EthWalletProvider
            const authMethod = await EthWalletProvider.authenticate({
                signer: ethersWallet,
                litNodeClient: this.litNodeClient,
            });
            console.log("Authenticated with EthWalletProvider.");
            // Send a transaction to PKP's address
            const tx = await ethersWallet.sendTransaction({
                to: this.pkp.ethAddress,
                value: ethers.utils.parseEther("0.0001"),
            });
            console.log("Transaction hash:", tx.hash);
            // Log PKP's balance
            const balance = await provider.getBalance(this.pkp.ethAddress);
            console.log(`Balance of ${this.pkp.ethAddress}:`, ethers.utils.formatEther(balance));
            // Get PKP Session Signatures
            this.pkpSessionSigs = await this.litNodeClient.getPkpSessionSigs({
                pkpPublicKey: this.pkp.publicKey,
                chain: "ethereum",
                authMethods: [authMethod],
                resourceAbilityRequests: [
                    {
                        resource: new LitActionResource("*"),
                        ability: LIT_ABILITY.LitActionExecution,
                    },
                    { resource: new LitPKPResource("*"), ability: LIT_ABILITY.PKPSigning },
                ],
            });
            console.log("Obtained PKP session signatures.");
            // Optionally, execute litActionCode during initialization
            // const result = await this.executeLitAction();
            // console.log("LitAction execution result:", result);
        }
        catch (error) {
            console.error("Initialization error:", error);
            throw error; // Rethrow to prevent server from starting if initialization fails
        }
    }
    // Method to execute Lit Action
    async executeLitAction() {
        try {
            const result = await this.litNodeClient.executeJs({
                sessionSigs: this.pkpSessionSigs,
                code: litActionCode,
                jsParams: { publicKey: this.pkp.publicKey },
            });
            return result;
        }
        catch (error) {
            console.error("Error executing Lit Action:", error);
            throw error;
        }
    }
    // Create HTTP server
    createServer() {
        const server = http.createServer(async (req, res) => {
            if (req.method === 'POST' && req.url === '/submit-transaction') {
                let body = '';
                req.on('data', chunk => {
                    body += chunk.toString();
                });
                req.on('end', async () => {
                    try {
                        const {} = JSON.parse(body);
                        // Note: Since we're not using signedTx anymore, you can remove these fields or repurpose them
                        // Optionally, perform additional validation or processing based on the request body
                        console.log("Received /submit-transaction request. Executing Lit Action...");
                        // Execute Lit Action instead of sending a transaction
                        const result = await this.executeLitAction();
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({
                            status: 'Lit Action executed successfully',
                            result: result
                        }));
                    }
                    catch (error) {
                        console.error('Server transaction error:', error);
                        res.writeHead(500, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({
                            error: 'Failed to execute Lit Action',
                            details: error.message || error.toString()
                        }));
                    }
                });
            }
            else {
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                res.end('Not Found');
            }
        });
        return server;
    }
    // Start the server
    start(port = 3000) {
        const server = this.createServer();
        server.listen(port, () => {
            console.log(`Gas sponsorship server running on port ${port}`);
        });
    }
}
// Example usage
async function main() {
    const server = new GasSponsorServer('https://yellowstone-rpc.litprotocol.com', pk1);
    try {
        await server.init();
        server.start();
    }
    catch (error) {
        console.error('Failed to initialize the GasSponsorServer:', error);
        process.exit(1); // Exit the process with a failure code
    }
}
// Execute the main function
main();
