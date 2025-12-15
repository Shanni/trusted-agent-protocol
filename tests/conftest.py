# © 2025 Project Sienna - Pytest Configuration
#
# Shared fixtures for TAP test suite

import pytest
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.backends import default_backend


@pytest.fixture
def rsa_keypair():
    """Generate RSA key pair for testing"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return {
        'private_key': private_key,
        'public_key': public_key,
        'private_pem': private_pem,
        'public_pem': public_pem
    }


@pytest.fixture
def ed25519_keypair():
    """Generate Ed25519 key pair for testing"""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    return {
        'private_key': private_key,
        'public_key': public_key,
        'private_b64': base64.b64encode(private_bytes).decode('utf-8'),
        'public_b64': base64.b64encode(public_bytes).decode('utf-8')
    }
