// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BadgeRegistry {
    struct BadgeRecord {
        string badgeId;
        bytes32 badgeHash;
        address issuer;
        uint256 timestamp;
    }

    // Mapping from badge ID to its on-chain record
    mapping(string => BadgeRecord) private badges;

    // Event emitted when a badge is registered on-chain
    event BadgeIssued(string indexed badgeId, bytes32 indexed badgeHash, address indexed issuer, uint256 timestamp);

    // Register a badge hash on-chain
    function issueBadge(string memory badgeId, bytes32 badgeHash) public {
        require(bytes(badges[badgeId].badgeId).length == 0, "Badge already registered");

        badges[badgeId] = BadgeRecord({
            badgeId: badgeId,
            badgeHash: badgeHash,
            issuer: msg.sender,
            timestamp: block.timestamp
        });

        emit BadgeIssued(badgeId, badgeHash, msg.sender, block.timestamp);
    }

    // Verify and retrieve a badge hash record
    function verifyBadge(string memory badgeId) public view returns (bytes32 badgeHash, address issuer, uint256 timestamp) {
        require(bytes(badges[badgeId].badgeId).length > 0, "Badge does not exist");
        BadgeRecord memory record = badges[badgeId];
        return (record.badgeHash, record.issuer, record.timestamp);
    }
}