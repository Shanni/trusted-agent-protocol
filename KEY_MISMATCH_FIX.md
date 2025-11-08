# Key Mismatch Fix - Ed25519 Signature Verification

## Root Cause Identified ✅

The CDN proxy signature verification was **failing** because:

```
🎯 Ed25519 Verification result: INVALID ❌
❌ CDN: ed25519 signature verification failed
```

**The Problem:**
- TAP Agent signs with Ed25519 private key from `tap-agent/.env`
- Agent Registry has a **different** Ed25519 public key in its database
- CDN Proxy fetches the wrong public key and verification fails

### Evidence

**TAP Agent's Public Key** (from `.env`):
```
ED25519_PUBLIC_KEY=A0LEzedOrxk15qZJnGtI... (your actual key)
```

**Agent Registry's Public Key** (from `populate_sample_data.py` line 61):
```python
"public_key": "09Xvvs6I2LOkF0EFb3ofNai87g0mWipuEMwVdi78m6E="  # WRONG KEY!
```

These are **completely different keys**, so signature verification will always fail!

---

## Fixes Applied

### Fix 1: Add DELETE Endpoint for Keys ✅

Added ability to remove keys from the agent registry.

**File:** `agent-registry/main.py` (lines 321-355)

```python
@app.delete("/agents/{agent_id}/keys/{key_id}", response_model=Message)
async def delete_agent_key(agent_id: int, key_id: str, db: Session = Depends(get_db)):
    """
    Delete a specific key from an agent
    """
    # ... implementation ...
```

**Usage:**
```bash
curl -X DELETE http://localhost:9002/agents/1/keys/primary-ed25519
```

### Fix 2: Key Sync Script ✅

Created `sync_tap_agent_key.py` to automatically sync the TAP agent's public key to the registry.

**What it does:**
1. Reads `ED25519_PUBLIC_KEY` from `tap-agent/.env`
2. Deletes the old `primary-ed25519` key from agent registry
3. Adds the correct public key
4. Verifies the sync was successful

---

## How to Fix Your Setup

### Step 1: Restart Agent Registry (with DELETE endpoint)

```bash
cd agent-registry
python main.py
```

### Step 2: Run the Sync Script

```bash
cd trusted-agent-protocol
python sync_tap_agent_key.py
```

**Expected Output:**
```
✅ Found ED25519_PUBLIC_KEY in tap-agent/.env
   Public Key: A0LEzedOrxk15qZJnGtI...

🔄 Syncing key to Agent Registry...
   Agent ID: 1
   Key ID: primary-ed25519

✅ Deleted old key 'primary-ed25519'
✅ Successfully added new key 'primary-ed25519'

📋 Key Details:
   Key ID: primary-ed25519
   Algorithm: ed25519
   Public Key: A0LEzedOrxk15qZJnGtI...
   Status: Active

✅ Verification successful! Key matches TAP agent's public key.

🎉 Done! You can now test signature verification.
```

### Step 3: Test Signature Verification

1. **Restart CDN Proxy** (to clear cache):
   ```bash
   cd cdn-proxy
   npm start
   ```

2. **In TAP Agent** (http://localhost:8503):
   - Click **"🔄 Reset to Default JSON"** (fresh nonce!)
   - Click **"Generate Signature & Launch Browser"**

3. **Expected Success:**
   ```
   ✅ CDN: RFC 9421 signature verification successful!
   🎯 Request authenticated with keyId: primary-ed25519
   🔄 Forwarding /product request to backend: /1
   ```

---

## Why the CDN Proxy Doesn't Try Multiple Keys

**Current Behavior:**
The CDN proxy fetches **one specific key** by `keyId` from the signature:

```javascript
// From signature-input header
keyId: 'primary-ed25519'

// CDN proxy fetches this specific key
const keyInfo = await getKeyById('primary-ed25519');  // Only ONE key!
```

**Why This is Correct:**
- RFC 9421 specifies the `keyId` in the signature
- The signer (TAP agent) tells the verifier (CDN proxy) which key to use
- The verifier should **only** try that specific key
- Trying multiple keys would be a security anti-pattern

**The Real Problem:**
- The TAP agent says: "Use key `primary-ed25519`"
- The CDN proxy fetches `primary-ed25519` from registry
- But the registry has the **wrong public key** for that `keyId`
- Solution: **Fix the registry**, not the CDN proxy logic

---

## Alternative: Update populate_sample_data.py

If you want to regenerate the sample data with the correct key:

1. **Get your public key:**
   ```bash
   cd tap-agent
   grep ED25519_PUBLIC_KEY .env
   ```

2. **Update `agent-registry/populate_sample_data.py` line 61:**
   ```python
   {
       "key_id": "primary-ed25519",
       "public_key": "YOUR_ACTUAL_PUBLIC_KEY_HERE",  # Paste from .env
       "algorithm": "ed25519",
       "description": "Primary Ed25519 signing key for modern crypto",
       "is_active": "true"
   }
   ```

3. **Re-populate:**
   ```bash
   cd agent-registry
   rm agent_registry.db  # Delete old database
   python populate_sample_data.py
   ```

---

## Files Modified

1. ✅ `agent-registry/main.py` (lines 321-355)
   - Added DELETE endpoint for keys

2. ✅ `sync_tap_agent_key.py` (new file)
   - Automated key sync script

3. ✅ `cdn-proxy/server.js` (line 671-678)
   - Added `/product/*` routing to backend (from previous fix)

---

## API Endpoints Added

### Delete Agent Key
```http
DELETE /agents/{agent_id}/keys/{key_id}
```

**Example:**
```bash
curl -X DELETE http://localhost:9002/agents/1/keys/primary-ed25519
```

**Response:**
```json
{
  "message": "Key 'primary-ed25519' deleted from agent 1"
}
```

---

## Testing Checklist

- [ ] Agent Registry running with DELETE endpoint
- [ ] Run `python sync_tap_agent_key.py` successfully
- [ ] CDN Proxy restarted (to clear key cache)
- [ ] TAP Agent: Click "🔄 Reset to Default JSON"
- [ ] TAP Agent: Generate signature and launch browser
- [ ] CDN Proxy logs show: `✅ CDN: RFC 9421 signature verification successful!`
- [ ] Browser displays product with price (not error page)

---

## Summary

The signature verification was failing because the **public key in the agent registry didn't match the private key used by the TAP agent**. The fix is to sync the correct public key to the registry using the `sync_tap_agent_key.py` script.

The CDN proxy logic is **correct** - it should only try the specific key identified by `keyId` in the signature, not iterate through multiple keys.
