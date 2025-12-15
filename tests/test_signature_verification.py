# © 2025 Project Sienna - Test Suite for RFC 9421 Signature Verification
#
# Run with: pytest tests/test_signature_verification.py -v

import pytest
import base64
import time
import uuid
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ed25519
from cryptography.hazmat.backends import default_backend


class TestRFC9421SignatureGeneration:
    """Test RFC 9421 HTTP Message Signature generation"""
    
    @pytest.fixture
    def rsa_keypair(self):
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
        
        return private_key, public_key, private_pem, public_pem
    
    @pytest.fixture
    def ed25519_keypair(self):
        """Generate Ed25519 key pair for testing"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Get raw bytes for Ed25519 (base64 encoded)
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        private_b64 = base64.b64encode(private_bytes).decode('utf-8')
        public_b64 = base64.b64encode(public_bytes).decode('utf-8')
        
        return private_key, public_key, private_b64, public_b64
    
    def create_rsa_signature(self, private_key, signature_base: str) -> str:
        """Create RSA-PSS-SHA256 signature"""
        signature = private_key.sign(
            signature_base.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def create_ed25519_signature(self, private_key, signature_base: str) -> str:
        """Create Ed25519 signature"""
        signature = private_key.sign(signature_base.encode('utf-8'))
        return base64.b64encode(signature).decode('utf-8')
    
    def build_signature_base(self, authority: str, path: str, signature_params: str) -> str:
        """Build RFC 9421 signature base string"""
        return '\n'.join([
            f'"@authority": {authority}',
            f'"@path": {path}',
            f'"@signature-params": {signature_params}'
        ])
    
    def test_rsa_signature_generation(self, rsa_keypair):
        """Test RSA-PSS-SHA256 signature generation"""
        private_key, public_key, _, _ = rsa_keypair
        
        authority = "localhost:3001"
        path = "/api/cart/checkout"
        created = int(time.time())
        expires = created + 3600
        nonce = str(uuid.uuid4())
        keyid = "test-key-1"
        
        signature_params = f'("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="rsa-pss-sha256"; nonce="{nonce}"; tag="agent-payment-auth"'
        signature_base = self.build_signature_base(authority, path, signature_params)
        
        signature_b64 = self.create_rsa_signature(private_key, signature_base)
        
        assert signature_b64 is not None
        assert len(signature_b64) > 100  # RSA signatures are ~342 chars in base64
        
        # Verify the signature
        signature_bytes = base64.b64decode(signature_b64)
        try:
            public_key.verify(
                signature_bytes,
                signature_base.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            verified = True
        except Exception:
            verified = False
        
        assert verified, "RSA signature verification failed"
    
    def test_ed25519_signature_generation(self, ed25519_keypair):
        """Test Ed25519 signature generation"""
        private_key, public_key, _, _ = ed25519_keypair
        
        authority = "localhost:3001"
        path = "/api/cart/checkout"
        created = int(time.time())
        expires = created + 3600
        nonce = str(uuid.uuid4())
        keyid = "test-ed25519-key"
        
        signature_params = f'("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="ed25519"; nonce="{nonce}"; tag="agent-payment-auth"'
        signature_base = self.build_signature_base(authority, path, signature_params)
        
        signature_b64 = self.create_ed25519_signature(private_key, signature_base)
        
        assert signature_b64 is not None
        assert len(signature_b64) == 88  # Ed25519 signatures are exactly 64 bytes = 88 chars in base64
        
        # Verify the signature
        signature_bytes = base64.b64decode(signature_b64)
        try:
            public_key.verify(signature_bytes, signature_base.encode('utf-8'))
            verified = True
        except Exception:
            verified = False
        
        assert verified, "Ed25519 signature verification failed"
    
    def test_signature_with_tampered_data_fails(self, rsa_keypair):
        """Test that tampered signature base fails verification"""
        private_key, public_key, _, _ = rsa_keypair
        
        authority = "localhost:3001"
        path = "/api/cart/checkout"
        created = int(time.time())
        expires = created + 3600
        nonce = str(uuid.uuid4())
        keyid = "test-key-1"
        
        signature_params = f'("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="rsa-pss-sha256"; nonce="{nonce}"; tag="agent-payment-auth"'
        signature_base = self.build_signature_base(authority, path, signature_params)
        
        # Sign original data
        signature_b64 = self.create_rsa_signature(private_key, signature_base)
        
        # Tamper with the path
        tampered_base = self.build_signature_base(authority, "/api/admin/delete", signature_params)
        
        # Verify should fail with tampered data
        signature_bytes = base64.b64decode(signature_b64)
        try:
            public_key.verify(
                signature_bytes,
                tampered_base.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            verified = True
        except Exception:
            verified = False
        
        assert not verified, "Tampered signature should not verify"


class TestRFC9421SignatureInputParsing:
    """Test RFC 9421 signature-input header parsing"""
    
    def parse_signature_input(self, signature_input: str) -> dict:
        """Parse RFC 9421 signature input header"""
        import re
        
        # Parse RFC 9421 format: sig2=("@authority" "@path"); created=...; expires=...; keyId="..."; alg="..."; nonce="..."; tag="..."
        signature_match = re.match(r'sig2=\(([^)]+)\);\s*(.+)', signature_input)
        
        if not signature_match:
            raise ValueError('Invalid RFC 9421 signature input format')
        
        param_string, attributes_string = signature_match.groups()
        
        # Parse parameters (what's being signed)
        params = [p.strip().strip('"') for p in param_string.split()]
        
        # Parse attributes
        attributes = {}
        attribute_matches = re.findall(r'(\w+)=("[^"]*"|\d+)', attributes_string)
        
        for key, value in attribute_matches:
            if value.startswith('"') and value.endswith('"'):
                attributes[key] = value[1:-1]
            else:
                attributes[key] = int(value)
        
        return {
            'params': params,
            'nonce': attributes.get('nonce'),
            'created': attributes.get('created'),
            'expires': attributes.get('expires'),
            'keyId': attributes.get('keyId'),
            'algorithm': attributes.get('alg'),
            'tag': attributes.get('tag')
        }
    
    def test_parse_valid_signature_input(self):
        """Test parsing valid RFC 9421 signature-input header"""
        signature_input = 'sig2=("@authority" "@path"); created=1735689600; expires=1735693200; keyId="test-key"; alg="rsa-pss-sha256"; nonce="abc123"; tag="agent-payment-auth"'
        
        result = self.parse_signature_input(signature_input)
        
        assert result['params'] == ['@authority', '@path']
        assert result['created'] == 1735689600
        assert result['expires'] == 1735693200
        assert result['keyId'] == 'test-key'
        assert result['algorithm'] == 'rsa-pss-sha256'
        assert result['nonce'] == 'abc123'
        assert result['tag'] == 'agent-payment-auth'
    
    def test_parse_ed25519_signature_input(self):
        """Test parsing Ed25519 signature-input header"""
        signature_input = 'sig2=("@authority" "@path"); created=1735689600; expires=1735693200; keyId="ed25519-key"; alg="ed25519"; nonce="xyz789"; tag="agent-browse"'
        
        result = self.parse_signature_input(signature_input)
        
        assert result['algorithm'] == 'ed25519'
        assert result['keyId'] == 'ed25519-key'
    
    def test_parse_invalid_format_raises(self):
        """Test that invalid format raises ValueError"""
        invalid_inputs = [
            'invalid-format',
            'sig1=("@authority"); created=123',  # Wrong sig prefix
            '("@authority" "@path"); created=123',  # Missing sig2=
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                self.parse_signature_input(invalid_input)


class TestTimestampValidation:
    """Test signature timestamp validation"""
    
    def validate_timestamps(self, created: int, expires: int, clock_skew_seconds: int = 60) -> tuple[bool, str]:
        """Validate signature timestamps"""
        now = int(time.time())
        
        # Check if created is in the future (with clock skew allowance)
        if created > now + clock_skew_seconds:
            return False, "Signature created time is in the future"
        
        # Check if signature has expired
        if expires < now:
            return False, f"Signature expired {now - expires} seconds ago"
        
        return True, "Valid"
    
    def test_valid_timestamps(self):
        """Test valid timestamp validation"""
        now = int(time.time())
        created = now - 10  # Created 10 seconds ago
        expires = now + 3600  # Expires in 1 hour
        
        valid, message = self.validate_timestamps(created, expires)
        
        assert valid, f"Should be valid: {message}"
    
    def test_expired_signature_fails(self):
        """Test that expired signatures fail validation"""
        now = int(time.time())
        created = now - 7200  # Created 2 hours ago
        expires = now - 3600  # Expired 1 hour ago
        
        valid, message = self.validate_timestamps(created, expires)
        
        assert not valid
        assert "expired" in message.lower()
    
    def test_future_created_time_fails(self):
        """Test that future created time fails validation"""
        now = int(time.time())
        created = now + 3600  # Created 1 hour in the future
        expires = now + 7200
        
        valid, message = self.validate_timestamps(created, expires)
        
        assert not valid
        assert "future" in message.lower()
    
    def test_clock_skew_tolerance(self):
        """Test that small clock skew is tolerated"""
        now = int(time.time())
        created = now + 30  # 30 seconds in future (within 60s tolerance)
        expires = now + 3600
        
        valid, message = self.validate_timestamps(created, expires, clock_skew_seconds=60)
        
        assert valid, f"Should tolerate 30s clock skew: {message}"


class TestNonceValidation:
    """Test nonce replay attack prevention"""
    
    def test_nonce_uniqueness(self):
        """Test that nonces are unique"""
        nonces = set()
        for _ in range(1000):
            nonce = str(uuid.uuid4())
            assert nonce not in nonces, "Duplicate nonce generated"
            nonces.add(nonce)
    
    def test_nonce_replay_detection(self):
        """Test nonce replay attack detection"""
        nonce_cache = {}
        
        def check_nonce(nonce: str) -> bool:
            """Return True if nonce is valid (not seen before)"""
            if nonce in nonce_cache:
                return False
            nonce_cache[nonce] = time.time()
            return True
        
        nonce = str(uuid.uuid4())
        
        # First use should succeed
        assert check_nonce(nonce), "First use of nonce should succeed"
        
        # Replay should fail
        assert not check_nonce(nonce), "Replay of nonce should fail"


class TestKeyIdValidation:
    """Test key ID format validation"""
    
    def validate_key_id(self, key_id: str) -> bool:
        """Validate key ID format"""
        import re
        if not isinstance(key_id, str):
            return False
        if len(key_id) > 100:
            return False
        if not re.match(r'^[a-zA-Z0-9._-]+$', key_id):
            return False
        return True
    
    def test_valid_key_ids(self):
        """Test valid key ID formats"""
        valid_ids = [
            'test-key-1',
            'agent.primary.2024',
            'KEY_123_backup',
            'a',
            'a' * 100,
        ]
        
        for key_id in valid_ids:
            assert self.validate_key_id(key_id), f"Should be valid: {key_id}"
    
    def test_invalid_key_ids(self):
        """Test invalid key ID formats"""
        invalid_ids = [
            '',  # Empty
            'a' * 101,  # Too long
            'key with spaces',
            'key<script>',  # XSS attempt
            'key;DROP TABLE',  # SQL injection attempt
            '../../../etc/passwd',  # Path traversal
            None,
        ]
        
        for key_id in invalid_ids:
            assert not self.validate_key_id(key_id), f"Should be invalid: {key_id}"


class TestPublicKeyValidation:
    """Test public key format validation"""
    
    def validate_rsa_public_key(self, key: str) -> bool:
        """Validate RSA public key PEM format"""
        key = key.strip()
        if not key.startswith('-----BEGIN PUBLIC KEY-----'):
            return False
        if not key.endswith('-----END PUBLIC KEY-----'):
            return False
        
        # Try to load the key
        try:
            serialization.load_pem_public_key(key.encode('utf-8'), backend=default_backend())
            return True
        except Exception:
            return False
    
    def validate_ed25519_public_key(self, key_b64: str) -> bool:
        """Validate Ed25519 public key (base64 encoded)"""
        try:
            decoded = base64.b64decode(key_b64.strip())
            if len(decoded) != 32:
                return False
            return True
        except Exception:
            return False
    
    def test_valid_rsa_key(self):
        """Test valid RSA public key validation"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        assert self.validate_rsa_public_key(public_pem)
    
    def test_invalid_rsa_key(self):
        """Test invalid RSA public key validation"""
        invalid_keys = [
            'not a key',
            '-----BEGIN PUBLIC KEY-----\ninvalid\n-----END PUBLIC KEY-----',
            '',
        ]
        
        for key in invalid_keys:
            assert not self.validate_rsa_public_key(key), f"Should be invalid: {key[:50]}"
    
    def test_valid_ed25519_key(self):
        """Test valid Ed25519 public key validation"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        public_b64 = base64.b64encode(public_bytes).decode('utf-8')
        
        assert self.validate_ed25519_public_key(public_b64)
    
    def test_invalid_ed25519_key(self):
        """Test invalid Ed25519 public key validation"""
        invalid_keys = [
            'not base64!',
            base64.b64encode(b'too short').decode('utf-8'),
            base64.b64encode(b'x' * 64).decode('utf-8'),  # Wrong length
        ]
        
        for key in invalid_keys:
            assert not self.validate_ed25519_public_key(key), f"Should be invalid: {key}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
