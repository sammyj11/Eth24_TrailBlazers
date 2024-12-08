// client.ts
import { ethers } from 'ethers';
import http from 'http';
import dotenv from 'dotenv';

dotenv.config();

interface CoinGeckoPriceResponse {
    ethereum: {
      inr: number;
    };
  }

class GasSponsorClient {
  private provider: ethers.providers.Provider;
  private senderWallet: ethers.Wallet;

  constructor(rpcUrl: string, privateKey: string) {
    this.provider = new ethers.providers.JsonRpcProvider(rpcUrl);
    this.senderWallet = new ethers.Wallet(privateKey, this.provider);
  }

  async prepareAndSendTransaction(
    recipientAddress: string, 
    amountInEth: string
  ): Promise<void> {
    try {
      // Create the transaction
      const tx = {
        to: recipientAddress,
        value: ethers.utils.parseEther(amountInEth),
        nonce: await this.provider.getTransactionCount(this.senderWallet.address) 
        // Optional: You can include data, nonce, etc., if needed
      };

      // Estimate gas
      const gasEstimate = await this.provider.estimateGas({
        ...tx,
        from: this.senderWallet.address
      });

    //   const response = await fetch(
    //     'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=inr'
    //   );
    //   const data = await response.json() as CoinGeckoPriceResponse;
    //   console.log("this is the fetched price", data.ethereum.inr);


      // Get current gas price (for legacy transactions) or suggest max fees (for EIP-1559)
      const gasPrice = await this.provider.getGasPrice();

      // Populate transaction with gas estimates
      const populatedTx = await this.senderWallet.populateTransaction({
        ...tx,
        gasLimit: 100000000,
        gasPrice: 100000000,
        // nonce: 21
        // For EIP-1559, use maxFeePerGas and maxPriorityFeePerGas instead
      });

      // Sign the transaction
      const signedTx = await this.senderWallet.signTransaction(populatedTx);
      
      // Send signed tx to server for submission
      this.sendToServer(signedTx, gasEstimate.toString());
    } catch (error) {
      console.error('Error preparing transaction:', error);
    }
  }

  private sendToServer(signedTx: string, gasEstimate: string): void {
    const postData = JSON.stringify({
      signedTx,
      from: this.senderWallet.address,
      estimate: gasEstimate
    });

    const options = {
      hostname: 'localhost',
      port: 3001,
      path: '/submit-transaction',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = http.request(options, (res) => {
      let responseBody = '';
      
      res.on('data', (chunk) => {
        responseBody += chunk;
      });

      res.on('end', () => {
        console.log('Server response:', responseBody);
      });
    });

    req.on('error', (error) => {
      console.error('Error sending transaction to server:', error);
    });

    req.write(postData);
    req.end();
  }
}

const { pk2 } = process.env;

// Example usage
async function main() {
  if (!pk2) {
    throw new Error('Private key (pk2) not set in environment variables.');
  }

  const client = new GasSponsorClient(
    'https://yellowstone-rpc.litprotocol.com',
    pk2
  );

  await client.prepareAndSendTransaction(
    '0x8cB4C5336db41B4701A001574749A043Fa2fCB7A',
    '0.0001'
  );
}

main().catch(console.error);
