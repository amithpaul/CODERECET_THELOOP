// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LoopToken
 * @dev A simple ERC20 token for rewarding contributors on The Loop platform.
 * The contract owner (our backend server) has the exclusive right to mint new tokens.
 */
contract LoopToken is ERC20, Ownable {
    /**
     * @dev Sets the name ("The Loop Token") and symbol ("LOOP") for the token.
     * Mints an initial supply of 0 tokens. The owner will mint new tokens as rewards.
     */
    constructor() ERC20("The Loop Token", "LOOP") Ownable(msg.sender) {}

    /**
     * @dev Creates new tokens and sends them to a specified address.
     * Can only be called by the contract owner.
     * @param to The address that will receive the minted tokens.
     * @param amount The amount of tokens to mint (in the smallest unit, like wei for Ether).
     */
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}