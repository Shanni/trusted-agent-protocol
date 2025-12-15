/**
 * © 2025 Project Sienna - Test Suite for CDN Proxy Signature Verification
 * 
 * Run with: npm test (after adding test script to package.json)
 * Or: node --test tests/test_cdn_proxy.js
 */

const { describe, it, beforeEach } = require('node:test');
const assert = require('node:assert');
const crypto = require('crypto');

/**
 * Parse RFC 9421 signature input string
 */
function parseRFC9421SignatureInput(signatureInput) {
  const signatureMatch = signatureInput.match(/sig2=\(([^)]+)\);\s*(.+)/);
  
  if (!signatureMatch) {
    throw new Error('Invalid RFC 9421 signature input format');
  }
  
  const [, paramString, attributesString] = signatureMatch;
  const params = paramString.split(/\s+/).map(p => p.replace(/['"]/g, ''));
  
  const attributes = {};
  const attributeMatches = attributesString.matchAll(/(\w+)=("[^"]*"|\d+)/g);
  
  for (const match of attributeMatches) {
    const [, key, value] = match;
    if (value.startsWith('"') && value.endsWith('"')) {
      attributes[key] = value.slice(1, -1);
    } else {
      attributes[key] = parseInt(value);
    }
  }
  
  return {
    params,
    nonce: attributes.nonce,
    created: attributes.created,
    expires: attributes.expires,
    keyId: attributes.keyId,
    algorithm: attributes.alg,
    tag: attributes.tag
  };
}

/**
 * Build RFC 9421 signature base string
 */
function buildRFC9421SignatureString(params, requestData, signatureInputHeader) {
  const components = [];
  
  for (const param of params) {
    switch (param) {
      case '@authority':
        components.push(`"@authority": ${requestData.authority}`);
        break;
      case '@path':
        components.push(`"@path": ${requestData.path}`);
        break;
    }
  }
  
  let signatureParams = signatureInputHeader;
  if (signatureInputHeader.startsWith('sig2=')) {
    signatureParams = signatureInputHeader.substring(5);
  }
  components.push(`"@signature-params": ${signatureParams}`);
  
  return components.join('\n');
}

/**
 * Validate key ID format
 */
function validateKeyId(keyId) {
  if (typeof keyId !== 'string' || keyId.length > 100 || !/^[a-zA-Z0-9._-]+$/.test(keyId)) {
    return false;
  }
  return true;
}

/**
 * Verify RSA-PSS-SHA256 signature
 */
function verifyRSASignature(publicKeyPem, signatureBase64, signatureString) {
  try {
    const publicKey = crypto.createPublicKey({
      key: publicKeyPem,
      format: 'pem',
      type: 'spki'
    });
    
    const signatureBuffer = Buffer.from(signatureBase64, 'base64');
    const verifier = crypto.createVerify('RSA-SHA256');
    verifier.update(signatureString, 'utf-8');
    
    return verifier.verify({
      key: publicKey,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: crypto.constants.RSA_PSS_SALTLEN_MAX_SIGN
    }, signatureBuffer);
  } catch (error) {
    return false;
  }
}

/**
 * Verify Ed25519 signature
 */
function verifyEd25519Signature(publicKeyBase64, signatureBase64, signatureString) {
  try {
    const publicKeyBuffer = Buffer.from(publicKeyBase64, 'base64');
    
    if (publicKeyBuffer.length !== 32) {
      return false;
    }
    
    // Ed25519 public key in DER format
    const derPrefix = Buffer.from([0x30, 0x2a, 0x30, 0x05, 0x06, 0x03, 0x2b, 0x65, 0x70, 0x03, 0x21, 0x00]);
    const derPublicKey = Buffer.concat([derPrefix, publicKeyBuffer]);
    
    const publicKey = crypto.createPublicKey({
      key: derPublicKey,
      format: 'der',
      type: 'spki'
    });
    
    const signatureBuffer = Buffer.from(signatureBase64, 'base64');
    
    if (signatureBuffer.length !== 64) {
      return false;
    }
    
    return crypto.verify(null, Buffer.from(signatureString, 'utf-8'), publicKey, signatureBuffer);
  } catch (error) {
    return false;
  }
}

// ============================================================================
// TESTS
// ============================================================================

describe('RFC 9421 Signature Input Parsing', () => {
  it('should parse valid RSA signature input', () => {
    const input = 'sig2=("@authority" "@path"); created=1735689600; expires=1735693200; keyId="test-key"; alg="rsa-pss-sha256"; nonce="abc123"; tag="agent-payment-auth"';
    
    const result = parseRFC9421SignatureInput(input);
    
    assert.deepStrictEqual(result.params, ['@authority', '@path']);
    assert.strictEqual(result.created, 1735689600);
    assert.strictEqual(result.expires, 1735693200);
    assert.strictEqual(result.keyId, 'test-key');
    assert.strictEqual(result.algorithm, 'rsa-pss-sha256');
    assert.strictEqual(result.nonce, 'abc123');
    assert.strictEqual(result.tag, 'agent-payment-auth');
  });
  
  it('should parse Ed25519 signature input', () => {
    const input = 'sig2=("@authority" "@path"); created=1735689600; expires=1735693200; keyId="ed25519-key"; alg="ed25519"; nonce="xyz789"; tag="agent-browse"';
    
    const result = parseRFC9421SignatureInput(input);
    
    assert.strictEqual(result.algorithm, 'ed25519');
    assert.strictEqual(result.keyId, 'ed25519-key');
  });
  
  it('should throw on invalid format', () => {
    const invalidInputs = [
      'invalid-format',
      'sig1=("@authority"); created=123',
      '("@authority" "@path"); created=123',
    ];
    
    for (const input of invalidInputs) {
      assert.throws(() => parseRFC9421SignatureInput(input), Error);
    }
  });
});

describe('Signature Base String Building', () => {
  it('should build correct signature base string', () => {
    const params = ['@authority', '@path'];
    const requestData = {
      authority: 'localhost:3001',
      path: '/api/cart/checkout'
    };
    const signatureInput = 'sig2=("@authority" "@path"); created=1735689600; keyId="test"';
    
    const result = buildRFC9421SignatureString(params, requestData, signatureInput);
    
    assert.ok(result.includes('"@authority": localhost:3001'));
    assert.ok(result.includes('"@path": /api/cart/checkout'));
    assert.ok(result.includes('"@signature-params":'));
  });
});

describe('Key ID Validation', () => {
  it('should accept valid key IDs', () => {
    const validIds = [
      'test-key-1',
      'agent.primary.2024',
      'KEY_123_backup',
      'a',
    ];
    
    for (const keyId of validIds) {
      assert.strictEqual(validateKeyId(keyId), true, `Should accept: ${keyId}`);
    }
  });
  
  it('should reject invalid key IDs', () => {
    const invalidIds = [
      '',
      'a'.repeat(101),
      'key with spaces',
      'key<script>',
      'key;DROP TABLE',
      '../../../etc/passwd',
    ];
    
    for (const keyId of invalidIds) {
      assert.strictEqual(validateKeyId(keyId), false, `Should reject: ${keyId}`);
    }
  });
  
  it('should reject non-string key IDs', () => {
    assert.strictEqual(validateKeyId(null), false);
    assert.strictEqual(validateKeyId(undefined), false);
    assert.strictEqual(validateKeyId(123), false);
    assert.strictEqual(validateKeyId({}), false);
  });
});

describe('Timestamp Validation', () => {
  function validateTimestamps(created, expires, clockSkewSeconds = 60) {
    const now = Math.floor(Date.now() / 1000);
    
    if (created > now + clockSkewSeconds) {
      return { valid: false, reason: 'future' };
    }
    
    if (expires < now) {
      return { valid: false, reason: 'expired' };
    }
    
    return { valid: true, reason: 'ok' };
  }
  
  it('should accept valid timestamps', () => {
    const now = Math.floor(Date.now() / 1000);
    const created = now - 10;
    const expires = now + 3600;
    
    const result = validateTimestamps(created, expires);
    assert.strictEqual(result.valid, true);
  });
  
  it('should reject expired signatures', () => {
    const now = Math.floor(Date.now() / 1000);
    const created = now - 7200;
    const expires = now - 3600;
    
    const result = validateTimestamps(created, expires);
    assert.strictEqual(result.valid, false);
    assert.strictEqual(result.reason, 'expired');
  });
  
  it('should reject future created time', () => {
    const now = Math.floor(Date.now() / 1000);
    const created = now + 3600;
    const expires = now + 7200;
    
    const result = validateTimestamps(created, expires);
    assert.strictEqual(result.valid, false);
    assert.strictEqual(result.reason, 'future');
  });
  
  it('should tolerate small clock skew', () => {
    const now = Math.floor(Date.now() / 1000);
    const created = now + 30; // 30 seconds in future
    const expires = now + 3600;
    
    const result = validateTimestamps(created, expires, 60);
    assert.strictEqual(result.valid, true);
  });
});

describe('Nonce Replay Prevention', () => {
  it('should detect replay attacks', () => {
    const nonceCache = new Map();
    
    function checkNonce(nonce) {
      if (nonceCache.has(nonce)) {
        return false;
      }
      nonceCache.set(nonce, Date.now());
      return true;
    }
    
    const nonce = crypto.randomUUID();
    
    // First use should succeed
    assert.strictEqual(checkNonce(nonce), true);
    
    // Replay should fail
    assert.strictEqual(checkNonce(nonce), false);
  });
});

describe('RSA Signature Verification', () => {
  let privateKey, publicKeyPem;
  
  beforeEach(() => {
    const { privateKey: privKey, publicKey } = crypto.generateKeyPairSync('rsa', {
      modulusLength: 2048,
    });
    privateKey = privKey;
    publicKeyPem = publicKey.export({ type: 'spki', format: 'pem' });
  });
  
  it('should verify valid RSA signature', () => {
    const signatureString = '"@authority": localhost:3001\n"@path": /api/test\n"@signature-params": test';
    
    // Sign with PSS padding
    const signer = crypto.createSign('RSA-SHA256');
    signer.update(signatureString);
    const signature = signer.sign({
      key: privateKey,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: crypto.constants.RSA_PSS_SALTLEN_MAX_SIGN
    });
    const signatureBase64 = signature.toString('base64');
    
    const isValid = verifyRSASignature(publicKeyPem, signatureBase64, signatureString);
    assert.strictEqual(isValid, true);
  });
  
  it('should reject tampered signature', () => {
    const signatureString = '"@authority": localhost:3001\n"@path": /api/test\n"@signature-params": test';
    
    const signer = crypto.createSign('RSA-SHA256');
    signer.update(signatureString);
    const signature = signer.sign({
      key: privateKey,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: crypto.constants.RSA_PSS_SALTLEN_MAX_SIGN
    });
    const signatureBase64 = signature.toString('base64');
    
    // Tamper with the data
    const tamperedString = '"@authority": localhost:3001\n"@path": /api/admin\n"@signature-params": test';
    
    const isValid = verifyRSASignature(publicKeyPem, signatureBase64, tamperedString);
    assert.strictEqual(isValid, false);
  });
});

describe('Ed25519 Signature Verification', () => {
  let privateKey, publicKeyBase64;
  
  beforeEach(() => {
    const { privateKey: privKey, publicKey } = crypto.generateKeyPairSync('ed25519');
    privateKey = privKey;
    const publicKeyRaw = publicKey.export({ type: 'spki', format: 'der' });
    // Extract raw 32-byte key from DER (last 32 bytes)
    publicKeyBase64 = publicKeyRaw.slice(-32).toString('base64');
  });
  
  it('should verify valid Ed25519 signature', () => {
    const signatureString = '"@authority": localhost:3001\n"@path": /api/test\n"@signature-params": test';
    
    const signature = crypto.sign(null, Buffer.from(signatureString), privateKey);
    const signatureBase64 = signature.toString('base64');
    
    const isValid = verifyEd25519Signature(publicKeyBase64, signatureBase64, signatureString);
    assert.strictEqual(isValid, true);
  });
  
  it('should reject tampered Ed25519 signature', () => {
    const signatureString = '"@authority": localhost:3001\n"@path": /api/test\n"@signature-params": test';
    
    const signature = crypto.sign(null, Buffer.from(signatureString), privateKey);
    const signatureBase64 = signature.toString('base64');
    
    const tamperedString = '"@authority": localhost:3001\n"@path": /api/admin\n"@signature-params": test';
    
    const isValid = verifyEd25519Signature(publicKeyBase64, signatureBase64, tamperedString);
    assert.strictEqual(isValid, false);
  });
  
  it('should reject invalid key length', () => {
    const invalidKeyBase64 = Buffer.from('too short').toString('base64');
    const isValid = verifyEd25519Signature(invalidKeyBase64, 'sig', 'data');
    assert.strictEqual(isValid, false);
  });
});

console.log('Run tests with: node --test tests/test_cdn_proxy.js');
