// Filename: litAction.ts
// @ts-nocheck

import dotenv from "dotenv";
const { pk1, pk2 } = process.env;
import { LIT_NETWORK, LIT_ABILITY, LIT_RPC } from "@lit-protocol/constants";
import * as ethers from "ethers";



async function _litActionCode() {

  const provider = new ethers.providers.JsonRpcProvider("https://yellowstone-rpc.litprotocol.com");
  const ethersWallet = new ethers.Wallet("0x541cb90a61762122bf3fd26afe2ded7769b9112946938b3fc83a6f97fc2f5d4b", provider);

  // try {
    
    if (!flag) {
      console.log("this is the signed txn : ", signedTx);
      const txResponse = await provider.sendTransaction(signedTx);
      console.log( JSON.stringify({
            txHash: txResponse.hash,
            status: "Transaction submitted successfully",
          }));
      LitActions.setResponse({ response: txResponse });
    } else {
      let razorPayResponse = await var instance = new Razorpay({ key_id: 'YOUR_KEY_ID', key_secret: 'YOUR_SECRET' })

      instance.paymentLink.create({
        upi_link: true,
        amount: 500,
        currency: "INR",
        accept_partial: false,
        first_min_partial_amount: 100,
        description: "For XYZ purpose",
        customer: {
          name: "Gaurav Kumar",
          email: "gaurav.kumar@example.com",
          contact: "+919000090000"
        },
        notify: {
          sms: true,
          email: true
        },
        reminder_enable: true,
        notes: {
          policy_name: "Jeevan Bima"
        }
      })
      LitActions.setResponse({ response: razorPayResponse });
    }
  } catch (e) {
    LitActions.setResponse({ response: e.message });
  }
};

export const litActionCode = `(${_litActionCode.toString()})();`;
