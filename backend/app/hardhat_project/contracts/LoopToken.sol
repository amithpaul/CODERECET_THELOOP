// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LoopToken
 * @dev An ERC20 token for rewarding contributors on The Loop platform.
 *      Only the contract owner (typically your backend server) can mint new tokens.
 */
contract LoopToken is ERC20, Ownable {
    /**
     * @dev Sets the name ("The Loop Token") and symbol ("LOOP") for the token.
     *      Mints an initial supply of 0 tokens. New tokens are minted as rewards by the owner.
     */
    constructor() ERC20("The Loop Token", "LOOP") {}

    /**
     * @dev Mints new tokens to a specified address.
     *      Can only be called by the contract owner.
     * @param to The address that will receive the minted tokens.
     * @param amount The number of tokens to mint (in smallest units, like wei for Ether).
     */
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}
