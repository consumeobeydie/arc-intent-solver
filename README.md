# Arc Intent Solver

Autonomous on-chain intent solver on Arc Testnet. Users submit intents, the Python agent analyzes and executes the optimal strategy.

## Live

- **Dashboard:** https://arc-intent-dashboard.vercel.app
- **Contract:** https://testnet.arcscan.app/address/0x3917DF9B70DeAEa7c3fcCa7456F89045Ef024d94

## Intent Types

| Type | Strategy |
|---|---|
| MAXIMIZE_YIELD | ArcDEX vs Vault analysis |
| SWAP_BEST_PRICE | ArcDEX best price |
| CROSS_CHAIN_BRIDGE | CCTP to Base |
| DOLLAR_COST_AVERAGE | Daily automated buy |

## Contracts (Arc Testnet)

| Contract | Address |
|---|---|
| IntentRegistry | 0x3917DF9B70DeAEa7c3fcCa7456F89045Ef024d94 |
| ArcDEX | 0x1A142DF560a671c66c361A29a48Ab839Bc9F890E |
| AgentIdentity | 0x5275783cD74eC21739Af8f3be9c42C024F671cFb |

## Run Agent

```bash
cd agent && pip install web3 python-dotenv
python3 solver.py
```

## Stack

- Solidity + Foundry (IntentRegistry.sol)
- Python (autonomous solver agent)
- Next.js (dashboard)
- viem (on-chain reads)
- Arc Testnet (Chain ID: 5042002)

## Author

consumeobeydie — https://github.com/consumeobeydie/arc-testnet-journey
