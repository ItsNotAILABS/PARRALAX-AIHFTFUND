"""
Digital Fingerprinting Service — SHA-256 + Merkle Tree Document Hashing
PARALLAX Sovereign Organism — Cryptographic Document Identity System

PURPOSE: Every document/artifact in PARALLAX gets a verifiable, immutable digital
fingerprint. Combined with Merkle trees, this creates a tamper-proof registry that
proves document authenticity and detects any changes.

DOCTRINE:
- Each document = SHA-256 hash + timestamp + version
- Collections = Merkle root for batch verification
- Public fingerprint registry = immutable proof chain
- PARALLAX stores fingerprints on ANIMA chain (permanent, tamper-proof)
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class DocumentFingerprint:
    """Single document fingerprint record."""
    doc_id: str
    doc_path: str
    doc_name: str
    content_hash: str  # SHA-256 of document content
    metadata_hash: str  # SHA-256 of metadata
    composite_hash: str  # SHA-256(content_hash + metadata_hash)
    timestamp: str  # ISO 8601
    version: int
    release_class: str  # SOVEREIGN_PRIVATE, TRUNK, PUBLIC
    tags: List[str]  # Tags for indexing (Law03, architecture, doctrine, etc.)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MerkleNode:
    """Node in Merkle tree."""
    hash: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    is_leaf: bool = False
    fingerprint: Optional[DocumentFingerprint] = None


class DigitalFingerprintService:
    """Service for generating and verifying digital fingerprints."""
    
    def __init__(self):
        self.fingerprints: Dict[str, DocumentFingerprint] = {}
        self.merkle_trees: Dict[str, MerkleNode] = {}  # keyed by collection_id
        self.version_history: Dict[str, List[DocumentFingerprint]] = {}  # Track versions
    
    @staticmethod
    def sha256(data: str) -> str:
        """Generate SHA-256 hash of string data."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def sha256_bytes(data: bytes) -> str:
        """Generate SHA-256 hash of bytes."""
        return hashlib.sha256(data).hexdigest()
    
    def create_fingerprint(
        self,
        doc_id: str,
        doc_path: str,
        doc_name: str,
        content: str,
        metadata: Dict = None,
        release_class: str = "TRUNK",
        tags: List[str] = None,
    ) -> DocumentFingerprint:
        """
        Create a digital fingerprint for a document.
        
        Args:
            doc_id: Unique document identifier
            doc_path: Path in repository
            doc_name: Human-readable name
            content: Document content (string or serialized)
            metadata: Optional metadata dict
            release_class: SOVEREIGN_PRIVATE, TRUNK, or PUBLIC
            tags: List of tags for indexing
            
        Returns:
            DocumentFingerprint object
        """
        if metadata is None:
            metadata = {}
        
        # Hash the content
        content_hash = self.sha256(content)
        
        # Hash the metadata
        metadata_str = json.dumps(metadata, sort_keys=True, default=str)
        metadata_hash = self.sha256(metadata_str)
        
        # Composite hash: hash of both hashes
        composite_input = f"{content_hash}{metadata_hash}"
        composite_hash = self.sha256(composite_input)
        
        # Create fingerprint
        fp = DocumentFingerprint(
            doc_id=doc_id,
            doc_path=doc_path,
            doc_name=doc_name,
            content_hash=content_hash,
            metadata_hash=metadata_hash,
            composite_hash=composite_hash,
            timestamp=datetime.utcnow().isoformat() + "Z",
            version=1,
            release_class=release_class,
            tags=tags or [],
        )
        
        # Store
        self.fingerprints[doc_id] = fp
        
        # Track version history
        if doc_id not in self.version_history:
            self.version_history[doc_id] = []
        self.version_history[doc_id].append(fp)
        
        return fp
    
    def verify_fingerprint(self, doc_id: str, content: str, metadata: Dict = None) -> Tuple[bool, str]:
        """
        Verify that content matches a stored fingerprint.
        
        Returns:
            (is_valid, message)
        """
        if doc_id not in self.fingerprints:
            return False, f"Document {doc_id} not found in fingerprint registry"
        
        fp = self.fingerprints[doc_id]
        
        if metadata is None:
            metadata = {}
        
        # Recompute hashes
        new_content_hash = self.sha256(content)
        metadata_str = json.dumps(metadata, sort_keys=True, default=str)
        new_metadata_hash = self.sha256(metadata_str)
        
        # Check if content matches
        if new_content_hash != fp.content_hash:
            return False, "Content has been modified"
        
        if new_metadata_hash != fp.metadata_hash:
            return False, "Metadata has been modified"
        
        return True, "Fingerprint verified — no modifications detected"
    
    def get_version_history(self, doc_id: str) -> List[DocumentFingerprint]:
        """Get all versions of a document."""
        return self.version_history.get(doc_id, [])
    
    def detect_changes(self, doc_id: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Check if document has changed since fingerprint was created.
        
        Returns:
            (has_changed, previous_version_composite_hash_if_changed)
        """
        if doc_id not in self.fingerprints:
            return False, None
        
        fp = self.fingerprints[doc_id]
        new_composite = self.sha256(self.sha256(content) + self.sha256("{}"))
        
        if new_composite != fp.composite_hash:
            return True, fp.composite_hash
        
        return False, None
    
    def build_merkle_tree(self, collection_id: str, doc_ids: List[str]) -> MerkleNode:
        """
        Build a Merkle tree from a collection of document fingerprints.
        Merkle root = verifiable proof of entire collection state.
        """
        if not doc_ids:
            return MerkleNode(hash="", is_leaf=True)
        
        # Build leaf nodes from fingerprints
        leaves = []
        for doc_id in doc_ids:
            if doc_id in self.fingerprints:
                fp = self.fingerprints[doc_id]
                leaf = MerkleNode(
                    hash=fp.composite_hash,
                    is_leaf=True,
                    fingerprint=fp,
                )
                leaves.append(leaf)
        
        # Build tree bottom-up
        if len(leaves) == 0:
            return MerkleNode(hash="", is_leaf=True)
        
        current_level = leaves
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Parent hash = sha256(left_hash + right_hash)
                parent_input = f"{left.hash}{right.hash}"
                parent_hash = self.sha256(parent_input)
                
                parent = MerkleNode(
                    hash=parent_hash,
                    left=left,
                    right=right,
                    is_leaf=False,
                )
                next_level.append(parent)
            
            current_level = next_level
        
        root = current_level[0]
        self.merkle_trees[collection_id] = root
        return root
    
    def get_merkle_root(self, collection_id: str) -> str:
        """Get Merkle root hash for a collection."""
        if collection_id not in self.merkle_trees:
            return ""
        return self.merkle_trees[collection_id].hash
    
    def verify_merkle_proof(self, collection_id: str, doc_id: str) -> bool:
        """Verify that a document is part of a Merkle tree collection."""
        if collection_id not in self.merkle_trees:
            return False
        
        if doc_id not in self.fingerprints:
            return False
        
        fp = self.fingerprints[doc_id]
        target_hash = fp.composite_hash
        
        # Traverse tree to find target
        def find_in_tree(node: MerkleNode) -> bool:
            if node.is_leaf:
                return node.hash == target_hash
            
            if node.left and find_in_tree(node.left):
                return True
            if node.right and find_in_tree(node.right):
                return True
            
            return False
        
        root = self.merkle_trees[collection_id]
        return find_in_tree(root)
    
    def export_fingerprints(self, release_class: Optional[str] = None) -> List[Dict]:
        """
        Export fingerprints (optionally filtered by release class).
        Used for public APIs — filters by SOVEREIGN_PRIVATE/TRUNK/PUBLIC.
        """
        fps = []
        for doc_id, fp in self.fingerprints.items():
            if release_class is None or fp.release_class == release_class:
                fps.append(fp.to_dict())
        
        return sorted(fps, key=lambda x: x['timestamp'])
    
    def get_fingerprint(self, doc_id: str) -> Optional[DocumentFingerprint]:
        """Retrieve a single fingerprint by ID."""
        return self.fingerprints.get(doc_id)


# Singleton instance
_fingerprint_service: Optional[DigitalFingerprintService] = None


def get_fingerprint_service() -> DigitalFingerprintService:
    """Get or create the fingerprint service singleton."""
    global _fingerprint_service
    if _fingerprint_service is None:
        _fingerprint_service = DigitalFingerprintService()
    return _fingerprint_service
