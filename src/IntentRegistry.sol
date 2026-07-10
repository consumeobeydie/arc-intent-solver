// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

/// @title IntentRegistry
/// @notice On-chain intent registry for Arc Intent Solver
/// @dev Users submit intents, agents solve them and record results
contract IntentRegistry {

    enum IntentType { MAXIMIZE_YIELD, SWAP_BEST_PRICE, CROSS_CHAIN_BRIDGE, DOLLAR_COST_AVERAGE }
    enum IntentStatus { PENDING, SOLVING, SOLVED, FAILED }

    struct Intent {
        uint256 id;
        address user;
        IntentType intentType;
        IntentStatus status;
        uint256 amount;
        address tokenIn;
        string params;
        uint256 createdAt;
        uint256 solvedAt;
        address solver;
        string result;
        uint256 outputAmount;
    }

    uint256 public nextId;
    mapping(uint256 => Intent) public intents;
    mapping(address => uint256[]) public userIntents;
    mapping(address => bool) public authorizedSolvers;
    address public owner;

    event IntentSubmitted(uint256 indexed id, address indexed user, IntentType intentType, uint256 amount);
    event IntentSolving(uint256 indexed id, address indexed solver);
    event IntentSolved(uint256 indexed id, address indexed solver, uint256 outputAmount, string result);
    event IntentFailed(uint256 indexed id, string reason);
    event SolverAuthorized(address indexed solver);

    error NotAuthorized();
    error IntentNotFound();
    error InvalidStatus();

    constructor() {
        owner = msg.sender;
        authorizedSolvers[msg.sender] = true;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotAuthorized();
        _;
    }

    modifier onlySolver() {
        if (!authorizedSolvers[msg.sender]) revert NotAuthorized();
        _;
    }

    function authorizeSolver(address solver) external onlyOwner {
        authorizedSolvers[solver] = true;
        emit SolverAuthorized(solver);
    }

    function submitIntent(
        IntentType intentType,
        uint256 amount,
        address tokenIn,
        string calldata params
    ) external returns (uint256 id) {
        id = nextId++;
        intents[id] = Intent({
            id: id,
            user: msg.sender,
            intentType: intentType,
            status: IntentStatus.PENDING,
            amount: amount,
            tokenIn: tokenIn,
            params: params,
            createdAt: block.timestamp,
            solvedAt: 0,
            solver: address(0),
            result: "",
            outputAmount: 0
        });
        userIntents[msg.sender].push(id);
        emit IntentSubmitted(id, msg.sender, intentType, amount);
    }

    function startSolving(uint256 id) external onlySolver {
        Intent storage intent = intents[id];
        if (intent.createdAt == 0) revert IntentNotFound();
        if (intent.status != IntentStatus.PENDING) revert InvalidStatus();
        intent.status = IntentStatus.SOLVING;
        intent.solver = msg.sender;
        emit IntentSolving(id, msg.sender);
    }

    function recordSolved(
        uint256 id,
        uint256 outputAmount,
        string calldata result
    ) external onlySolver {
        Intent storage intent = intents[id];
        if (intent.status != IntentStatus.SOLVING) revert InvalidStatus();
        intent.status = IntentStatus.SOLVED;
        intent.solvedAt = block.timestamp;
        intent.outputAmount = outputAmount;
        intent.result = result;
        emit IntentSolved(id, msg.sender, outputAmount, result);
    }

    function recordFailed(uint256 id, string calldata reason) external onlySolver {
        Intent storage intent = intents[id];
        if (intent.status != IntentStatus.SOLVING) revert InvalidStatus();
        intent.status = IntentStatus.FAILED;
        intent.solvedAt = block.timestamp;
        intent.result = reason;
        emit IntentFailed(id, reason);
    }

    function getIntent(uint256 id) external view returns (Intent memory) {
        return intents[id];
    }

    function getUserIntents(address user) external view returns (uint256[] memory) {
        return userIntents[user];
    }

    function getPendingCount() external view returns (uint256 count) {
        for (uint256 i = 0; i < nextId; i++) {
            if (intents[i].status == IntentStatus.PENDING) count++;
        }
    }
}
