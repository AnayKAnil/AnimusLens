// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract CertRegistry {
    address public owner;

    struct Cert {
        bytes32 digest;   // SHA-256 digest stored as bytes32
        uint256 timestamp;
        bool revoked;
        string txid;      // optional additional metadata
    }

    mapping(string => Cert) private certs; // certificateId -> Cert

    modifier onlyOwner() {
        require(msg.sender == owner, "only owner");
        _;
    }

    event CertSet(string indexed certificateId, bytes32 digest, uint256 timestamp, string txid);
    event CertRevoked(string indexed certificateId, uint256 timestamp);

    constructor() {
        owner = msg.sender;
    }

    // Set certificate digest (only owner)
    function setCert(string calldata certificateId, bytes32 digest, string calldata txid) external onlyOwner {
        Cert storage c = certs[certificateId];
        c.digest = digest;
        c.timestamp = block.timestamp;
        c.revoked = false;
        c.txid = txid;
        emit CertSet(certificateId, digest, c.timestamp, txid);
    }

    // Revoke a certificate (only owner)
    function revokeCert(string calldata certificateId) external onlyOwner {
        certs[certificateId].revoked = true;
        certs[certificateId].timestamp = block.timestamp;
        emit CertRevoked(certificateId, block.timestamp);
    }

    // Get certificate details
    function getCert(string calldata certificateId) external view returns (bytes32, uint256, bool, string memory) {
        Cert memory c = certs[certificateId];
        return (c.digest, c.timestamp, c.revoked, c.txid);
    }
}
