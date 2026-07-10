// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import "forge-std/Test.sol";
import "../src/IntentRegistry.sol";

contract IntentRegistryTest is Test {
    IntentRegistry public registry;
    address public user = address(0xA001);
    address public solver = address(0xB002);

    address constant USDC = 0x3600000000000000000000000000000000000000;

    function setUp() public {
        registry = new IntentRegistry();
        registry.authorizeSolver(solver);
    }

    function testSubmitIntent() public {
        vm.prank(user);
        uint256 id = registry.submitIntent(
            IntentRegistry.IntentType.MAXIMIZE_YIELD,
            100e6,
            USDC,
            '{"minAPY": "5%"}'
        );
        assertEq(id, 0);
        IntentRegistry.Intent memory intent = registry.getIntent(0);
        assertEq(intent.user, user);
        assertEq(uint8(intent.status), uint8(IntentRegistry.IntentStatus.PENDING));
        assertEq(intent.amount, 100e6);
    }

    function testStartSolving() public {
        vm.prank(user);
        registry.submitIntent(IntentRegistry.IntentType.MAXIMIZE_YIELD, 100e6, USDC, "");

        vm.prank(solver);
        registry.startSolving(0);

        IntentRegistry.Intent memory intent = registry.getIntent(0);
        assertEq(uint8(intent.status), uint8(IntentRegistry.IntentStatus.SOLVING));
        assertEq(intent.solver, solver);
    }

    function testRecordSolved() public {
        vm.prank(user);
        registry.submitIntent(IntentRegistry.IntentType.MAXIMIZE_YIELD, 100e6, USDC, "");

        vm.prank(solver);
        registry.startSolving(0);

        vm.prank(solver);
        registry.recordSolved(0, 105e6, '{"strategy":"vault","apy":"5.2%"}');

        IntentRegistry.Intent memory intent = registry.getIntent(0);
        assertEq(uint8(intent.status), uint8(IntentRegistry.IntentStatus.SOLVED));
        assertEq(intent.outputAmount, 105e6);
    }

    function testRecordFailed() public {
        vm.prank(user);
        registry.submitIntent(IntentRegistry.IntentType.SWAP_BEST_PRICE, 100e6, USDC, "");

        vm.prank(solver);
        registry.startSolving(0);

        vm.prank(solver);
        registry.recordFailed(0, "Insufficient liquidity");

        IntentRegistry.Intent memory intent = registry.getIntent(0);
        assertEq(uint8(intent.status), uint8(IntentRegistry.IntentStatus.FAILED));
    }

    function testUnauthorizedSolver() public {
        vm.prank(user);
        registry.submitIntent(IntentRegistry.IntentType.MAXIMIZE_YIELD, 100e6, USDC, "");

        vm.prank(address(0xDEAD));
        vm.expectRevert(IntentRegistry.NotAuthorized.selector);
        registry.startSolving(0);
    }

    function testGetUserIntents() public {
        vm.startPrank(user);
        registry.submitIntent(IntentRegistry.IntentType.MAXIMIZE_YIELD, 100e6, USDC, "");
        registry.submitIntent(IntentRegistry.IntentType.SWAP_BEST_PRICE, 50e6, USDC, "");
        vm.stopPrank();

        uint256[] memory ids = registry.getUserIntents(user);
        assertEq(ids.length, 2);
        assertEq(ids[0], 0);
        assertEq(ids[1], 1);
    }

    function testGetPendingCount() public {
        vm.startPrank(user);
        registry.submitIntent(IntentRegistry.IntentType.MAXIMIZE_YIELD, 100e6, USDC, "");
        registry.submitIntent(IntentRegistry.IntentType.SWAP_BEST_PRICE, 50e6, USDC, "");
        vm.stopPrank();

        assertEq(registry.getPendingCount(), 2);

        vm.prank(solver);
        registry.startSolving(0);

        assertEq(registry.getPendingCount(), 1);
    }

    function testMultipleIntentTypes() public {
        vm.startPrank(user);
        registry.submitIntent(IntentRegistry.IntentType.MAXIMIZE_YIELD, 100e6, USDC, "");
        registry.submitIntent(IntentRegistry.IntentType.SWAP_BEST_PRICE, 50e6, USDC, "");
        registry.submitIntent(IntentRegistry.IntentType.CROSS_CHAIN_BRIDGE, 200e6, USDC, "");
        registry.submitIntent(IntentRegistry.IntentType.DOLLAR_COST_AVERAGE, 10e6, USDC, "");
        vm.stopPrank();

        assertEq(registry.nextId(), 4);
        assertEq(registry.getPendingCount(), 4);
    }
}
