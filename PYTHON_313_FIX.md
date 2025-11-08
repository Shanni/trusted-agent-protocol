# Python 3.13 Compatibility Fix

## Problem Summary

The Trusted Agent Protocol repository was using `pydantic==2.5.0` which is incompatible with Python 3.13. The error occurred because:

- Python 3.13 changed the `ForwardRef._evaluate()` API to require a `recursive_guard` parameter
- Pydantic 2.5.0 (released late 2023) predates Python 3.13 and doesn't support this change
- This caused build failures when installing `pydantic-core`

## Solution Applied

Updated the following files to use Python 3.13-compatible versions:

### `/requirements.txt`
- `pydantic`: 2.5.0 → **2.10.3**
- `fastapi`: 0.104.1 → **0.115.6**
- `uvicorn[standard]`: 0.24.0 → **0.34.0**
- `sqlalchemy`: 2.0.23 → **2.0.36**

### `/merchant-backend/requirements.txt`
- Same updates as above

## Verification

After running `pip install -r requirements.txt`, verify with:

```bash
~/.pyenv/versions/3.13.0/bin/python3 -c "import pydantic; print(pydantic.__version__)"
# Should output: 2.10.3

~/.pyenv/versions/3.13.0/bin/python3 -c "import fastapi; print(fastapi.__version__)"
# Should output: 0.115.6
```

## Important Note

Your system has multiple Python installations:
- **pyenv Python 3.13.0**: `/Users/shanliu/.pyenv/versions/3.13.0/bin/python3` (packages installed here)
- **Homebrew Python**: `/opt/homebrew/bin/python3` (different environment)

When running the services, ensure you're using the pyenv Python or set up your shell to use pyenv by default:

```bash
# Add to ~/.zshrc if not already present
eval "$(pyenv init -)"
```

## Next Steps

You can now start the services as documented in the README:

```bash
# Agent Registry (port 8001)
cd agent-registry && python main.py

# Merchant Backend (port 8000)
cd merchant-backend && python -m uvicorn app.main:app --reload

# TAP Agent (port 8501)
cd tap-agent && streamlit run agent_app.py
```

All Python services should now work correctly with Python 3.13.
