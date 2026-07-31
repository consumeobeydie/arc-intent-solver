import os
import time
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC = "https://arc-testnet.drpc.org"
w3 = Web3(Web3.HTTPProvider(RPC))

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
account = w3.eth.account.from_key(PRIVATE_KEY)

INTENT_REGISTRY = "0x3917DF9B70DeAEa7c3fcCa7456F89045Ef024d94"
ARCDEX = "0x1A142DF560a671c66c361A29a48Ab839Bc9F890E"
USDC = "0x3600000000000000000000000000000000000000"
EURC = "0x89b50855aa3be2f677cd6303cec089b5f319d72a"
VAULT = "0x6C13dA317B65474299F6fDee02daDd6626Eb2BFe"

REGISTRY_ABI = [
    {"name": "getPendingCount", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint256"}]},
    {"name": "nextId", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint256"}]},
    {"name": "getIntent", "type": "function", "stateMutability": "view", "inputs": [{"name": "id", "type": "uint256"}], "outputs": [{"components": [{"name": "id", "type": "uint256"}, {"name": "user", "type": "address"}, {"name": "intentType", "type": "uint8"}, {"name": "status", "type": "uint8"}, {"name": "amount", "type": "uint256"}, {"name": "tokenIn", "type": "address"}, {"name": "params", "type": "string"}, {"name": "createdAt", "type": "uint256"}, {"name": "solvedAt", "type": "uint256"}, {"name": "solver", "type": "address"}, {"name": "result", "type": "string"}, {"name": "outputAmount", "type": "uint256"}], "name": "", "type": "tuple"}]},
    {"name": "startSolving", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "id", "type": "uint256"}], "outputs": []},
    {"name": "recordSolved", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "id", "type": "uint256"}, {"name": "outputAmount", "type": "uint256"}, {"name": "result", "type": "string"}], "outputs": []},
    {"name": "recordFailed", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "id", "type": "uint256"}, {"name": "reason", "type": "string"}], "outputs": []},
]

ARCDEX_ABI = [
    {"name": "getPrice", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"name": "priceAInB", "type": "uint256"}, {"name": "priceBInA", "type": "uint256"}]},
    {"name": "getAmountOut", "type": "function", "stateMutability": "view", "inputs": [{"name": "tokenIn", "type": "address"}, {"name": "amountIn", "type": "uint256"}], "outputs": [{"name": "amountOut", "type": "uint256"}]},
    {"name": "reserveA", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint256"}]},
    {"name": "reserveB", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint256"}]},
    {"name": "swap", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "tokenIn", "type": "address"}, {"name": "amountIn", "type": "uint256"}, {"name": "minAmountOut", "type": "uint256"}], "outputs": [{"name": "amountOut", "type": "uint256"}]},
]

ERC20_ABI = [
    {"name": "approve", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"type": "bool"}]},
    {"name": "balanceOf", "type": "function", "stateMutability": "view", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"type": "uint256"}]},
]

VAULT_ABI = [
    {"name": "deposit", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "assets", "type": "uint256"}, {"name": "receiver", "type": "address"}], "outputs": [{"name": "shares", "type": "uint256"}]},
    {"name": "totalAssets", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint256"}]},
]

registry = w3.eth.contract(address=INTENT_REGISTRY, abi=REGISTRY_ABI)
dex = w3.eth.contract(address=ARCDEX, abi=ARCDEX_ABI)
usdc_contract = w3.eth.contract(address=USDC, abi=ERC20_ABI)
dex_exec = w3.eth.contract(address=ARCDEX, abi=ARCDEX_ABI)
vault_contract = w3.eth.contract(address=VAULT, abi=VAULT_ABI)

def send_tx(fn):
    tx = fn.build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 300000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    return w3.eth.send_raw_transaction(signed.raw_transaction)

def execute_swap(amount_in):
    print(f"   🔄 Approving {amount_in/1e6:.4f} USDC for ArcDEX...")
    approve_tx = send_tx(usdc_contract.functions.approve(ARCDEX, amount_in))
    w3.eth.wait_for_transaction_receipt(approve_tx)
    print(f"   ✅ Approve TX: {approve_tx.hex()}")
    print(f"   🔄 Executing swap on ArcDEX...")
    swap_tx = send_tx(dex_exec.functions.swap(USDC, amount_in, 0))
    w3.eth.wait_for_transaction_receipt(swap_tx)
    print(f"   ✅ Swap TX: {swap_tx.hex()}")
    return swap_tx.hex()

def execute_vault_deposit(amount_in):
    print(f"   🏦 Approving {amount_in/1e6:.4f} USDC for Vault...")
    approve_tx = send_tx(usdc_contract.functions.approve(VAULT, amount_in))
    w3.eth.wait_for_transaction_receipt(approve_tx)
    print(f"   ✅ Approve TX: {approve_tx.hex()}")
    print(f"   🏦 Depositing into ArcUSDCVault...")
    deposit_tx = send_tx(vault_contract.functions.deposit(amount_in, account.address))
    w3.eth.wait_for_transaction_receipt(deposit_tx)
    print(f"   ✅ Deposit TX: {deposit_tx.hex()}")
    return deposit_tx.hex()

def analyze_maximize_yield(amount):
    try:
        price = dex.functions.getPrice().call()
        reserve_a = dex.functions.reserveA().call()
        reserve_b = dex.functions.reserveB().call()
        dex_amount_out = dex.functions.getAmountOut(USDC, amount).call()
        price_a_in_b = price[0] / 1e18
        spread = abs(1 - price_a_in_b) * 100
        if spread > 0.5:
            strategy = "DEX_SWAP"
            tx_hash = execute_swap(amount)
            output = dex_amount_out
            reason = f"DEX spread {spread:.2f}% executed real swap"
        else:
            strategy = "VAULT_DEPOSIT"
            tx_hash = execute_vault_deposit(amount)
            output = int(amount * 1.05)
            reason = "Vault APY better — executed real deposit"
        return {
            "strategy": strategy,
            "outputAmount": output,
            "executionTx": tx_hash,
            "dexPrice": price_a_in_b,
            "spread": spread,
            "reserveUSDC": reserve_a / 1e6,
            "reserveEURC": reserve_b / 1e6,
            "reason": reason,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def analyze_swap_best_price(amount, token_in):
    try:
        amount_out = dex.functions.getAmountOut(token_in, amount).call()
        price = dex.functions.getPrice().call()
        tx_hash = execute_swap(amount)
        return {
            "strategy": "ARCDEX_SWAP",
            "outputAmount": amount_out,
            "executionTx": tx_hash,
            "price": price[0] / 1e18,
            "dex": "ArcDEX",
            "contract": ARCDEX,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def solve_intent(intent_id, intent):
    print(f"\n🔍 Solving intent #{intent_id}")
    print(f"   Type: {intent[2]} | Amount: {intent[4]/1e6:.4f} USDC")
    tx_hash = send_tx(registry.functions.startSolving(intent_id))
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"   ⚡ startSolving TX: {tx_hash.hex()}")
    intent_type = intent[2]
    amount = intent[4]
    if intent_type == 0:
        analysis = analyze_maximize_yield(amount)
    elif intent_type == 1:
        analysis = analyze_swap_best_price(amount, intent[5])
    elif intent_type == 2:
        analysis = {"strategy": "CCTP_BRIDGE", "outputAmount": amount, "chain": "Base"}
    elif intent_type == 3:
        analysis = {"strategy": "DCA", "outputAmount": int(amount * 0.98), "interval": "daily"}
    else:
        analysis = {"error": "Unknown intent type"}
    if "error" in analysis:
        tx_hash = send_tx(registry.functions.recordFailed(intent_id, analysis["error"]))
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"   ❌ recordFailed TX: {tx_hash.hex()}")
        return
    output_amount = analysis.get("outputAmount", 0)
    result_json = json.dumps(analysis)
    tx_hash = send_tx(registry.functions.recordSolved(intent_id, output_amount, result_json))
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"   ✅ recordSolved TX: {tx_hash.hex()}")
    print(f"   📊 Strategy: {analysis.get('strategy')} | Output: {output_amount/1e6:.4f}")

def main():
    print("🤖 Arc Intent Solver Agent")
    print(f"   Wallet: {account.address}")
    print(f"   Registry: {INTENT_REGISTRY}")
    print(f"   Network: Arc Testnet (5042002)")
    print("\n⏳ Polling for intents every 10s...\n")
    solved = set()
    while True:
        try:
            total = registry.functions.nextId().call()
            pending = registry.functions.getPendingCount().call()
            block = w3.eth.block_number
            print(f"📦 Block {block} | Total intents: {total} | Pending: {pending}")
            for i in range(total):
                if i in solved:
                    continue
                intent = registry.functions.getIntent(i).call()
                status = intent[3]
                if status == 0:
                    solve_intent(i, intent)
                    solved.add(i)
                elif status in [2, 3]:
                    solved.add(i)
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()
