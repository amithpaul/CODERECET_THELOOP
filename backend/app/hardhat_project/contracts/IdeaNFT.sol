function mintIdea(address to) public returns (uint256) {
    _tokenIds.increment();
    uint256 newTokenId = _tokenIds.current();
    _mint(to, newTokenId);
    return newTokenId;
}

function totalSupply() public view returns (uint256) {
    return _tokenIds.current();
}