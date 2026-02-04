# Scripts Directory

This directory contains utility scripts for setup, debugging, and validation. These are **NOT automated tests** - they are interactive tools for developers and operators.

## Directory Structure

```
scripts/
├── setup/          # Setup and configuration scripts
├── debug/          # Debugging and diagnostic tools
└── validate/       # Validation and verification scripts
```

## Setup Scripts (`scripts/setup/`)

### Gmail OAuth Setup

**Purpose**: Configure Gmail API OAuth credentials for the Gmail watcher.

#### Option 1: Standard OAuth Flow
```bash
uv run python scripts/setup/setup_gmail_oauth.py
```
- Opens browser for OAuth consent
- Saves credentials to `token.json`
- Best for local development

#### Option 2: Manual OAuth Flow (WSL/Remote)
```bash
uv run python scripts/setup/setup_gmail_oauth_manual.py
```
- Prints OAuth URL to console
- Copy/paste URL in browser
- Best for WSL or remote servers

#### Option 3: Out-of-Band OAuth
```bash
uv run python scripts/setup/setup_gmail_oauth_oob.py
```
- Uses out-of-band OAuth flow
- Manual code entry
- Best for headless environments

#### Complete OAuth Setup
```bash
uv run python scripts/setup/complete_oauth.py
```
- Completes partial OAuth flows
- Refreshes expired tokens
- Troubleshoots OAuth issues

### Prerequisites

1. **Google Cloud Console Setup**:
   - Create project at https://console.cloud.google.com
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` to `My_AI_Employee/`

2. **Add Test Users**:
   - Go to OAuth consent screen
   - Add your email as test user
   - Required for development/testing

## Debug Scripts (`scripts/debug/`)

### Gmail Debugging

#### Debug Gmail Connection
```bash
uv run python scripts/debug/debug_gmail.py
```
- Tests Gmail API connection
- Checks OAuth credentials
- Lists recent emails
- Verifies permissions

#### Debug Gmail Send
```bash
uv run python scripts/debug/debug_gmail_send.py
```
- Sends test email via Gmail API
- Bypasses MCP framework
- Direct API testing
- Useful for troubleshooting email sending

### PM2 Dashboard Debugging

```bash
uv run python scripts/debug/debug_pm2_dashboard.py
```
- Tests PM2 integration
- Queries watcher status from PM2
- Updates dashboard with PM2 data
- Verifies PM2 process management

## Validation Scripts (`scripts/validate/`)

### Silver Tier Validation

```bash
uv run python scripts/validate/validate_silver_tier.py
```

**Purpose**: Validates Silver tier implementation without real credentials.

**What it tests**:
- ✅ Vault structure exists
- ✅ Action item creation works
- ✅ Approval workflow functions
- ✅ Dashboard updates correctly
- ✅ Audit logging works
- ✅ DRY_RUN mode enabled

**Use cases**:
- Pre-deployment validation
- CI/CD smoke tests
- Verify setup before adding credentials
- Troubleshoot configuration issues

**Requirements**:
- Set `DRY_RUN=true` in `.env`
- Vault structure must exist
- No credentials needed

## Usage Patterns

### First-Time Setup

```bash
# 1. Set up Gmail OAuth
uv run python scripts/setup/setup_gmail_oauth.py

# 2. Validate configuration
uv run python scripts/validate/validate_silver_tier.py

# 3. Test Gmail connection
uv run python scripts/debug/debug_gmail.py

# 4. Run watcher
uv run python run_watcher.py --watcher gmail
```

### Troubleshooting

```bash
# OAuth issues
uv run python scripts/setup/complete_oauth.py

# Gmail connection issues
uv run python scripts/debug/debug_gmail.py

# Email sending issues
uv run python scripts/debug/debug_gmail_send.py

# PM2 integration issues
uv run python scripts/debug/debug_pm2_dashboard.py
```

### Pre-Deployment Validation

```bash
# Validate everything works (DRY_RUN mode)
uv run python scripts/validate/validate_silver_tier.py

# If validation passes, proceed with real credentials
uv run python scripts/setup/setup_gmail_oauth.py
```

## Scripts vs Tests

### Scripts (this directory)
- **Purpose**: Interactive tools for developers/operators
- **Run**: Manually when needed
- **Examples**: OAuth setup, debugging, validation
- **No assertions**: Just print output and exit codes

### Tests (`tests/` directory)
- **Purpose**: Automated testing with pytest
- **Run**: Automatically in CI/CD
- **Examples**: Unit tests, integration tests
- **Has assertions**: Pass/fail with test framework

## Common Issues

### OAuth Setup Fails

**Problem**: Browser doesn't open or OAuth fails
**Solution**: Use manual OAuth flow
```bash
uv run python scripts/setup/setup_gmail_oauth_manual.py
```

### Token Expired

**Problem**: Gmail watcher fails with authentication error
**Solution**: Delete token and re-authenticate
```bash
rm token.json
uv run python scripts/setup/setup_gmail_oauth.py
```

### Credentials Not Found

**Problem**: `credentials.json` not found
**Solution**: Download from Google Cloud Console
1. Go to https://console.cloud.google.com
2. Navigate to APIs & Services > Credentials
3. Download OAuth 2.0 Client ID credentials
4. Save as `My_AI_Employee/credentials.json`

### Permission Denied

**Problem**: Gmail API returns 403 Forbidden
**Solution**: Add your email as test user
1. Go to OAuth consent screen in Google Cloud Console
2. Add your email under "Test users"
3. Re-authenticate with `setup_gmail_oauth.py`

## Environment Variables

Scripts respect these environment variables from `.env`:

```bash
# Gmail OAuth
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Vault configuration
VAULT_ROOT=AI_Employee_Vault

# Testing mode
DRY_RUN=true  # For validation scripts
```

## Adding New Scripts

When adding new utility scripts:

1. **Choose the right directory**:
   - `setup/` - Configuration and initialization
   - `debug/` - Diagnostic and troubleshooting tools
   - `validate/` - Verification and smoke tests

2. **Follow naming conventions**:
   - `setup_*.py` - Setup scripts
   - `debug_*.py` - Debug scripts
   - `validate_*.py` - Validation scripts

3. **Add documentation**:
   - Update this README
   - Add docstring to script
   - Include usage examples

4. **Use `uv run`**:
   - All scripts should work with `uv run python scripts/...`
   - Ensures correct dependencies

## See Also

- `tests/` - Automated test suite
- `WATCHER_RUNNER_GUIDE.md` - Watcher usage guide
- `README.md` - Project overview
