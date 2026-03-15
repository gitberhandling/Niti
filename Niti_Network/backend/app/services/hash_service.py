import hashlib


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of raw bytes and return as hex string."""
    return hashlib.sha256(data).hexdigest()


def compute_sha256_from_file(file_path: str) -> str:
    """Compute SHA-256 hash by reading file in 8KB chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
