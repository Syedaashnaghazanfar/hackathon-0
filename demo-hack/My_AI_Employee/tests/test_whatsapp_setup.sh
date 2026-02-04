#!/bin/bash
# WhatsApp Watcher Setup Verification Script
# Run this to verify your WhatsApp watcher setup is correct

set -e  # Exit on error

echo "=========================================="
echo "WhatsApp Watcher Setup Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Python version
echo "Check 1: Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (OK)"
else
    echo -e "${RED}✗${NC} Python $PYTHON_VERSION (Need 3.10+)"
    exit 1
fi
echo ""

# Check 2: Required Python packages
echo "Check 2: Required Python packages..."
REQUIRED_PACKAGES=("dotenv" "playwright" "watchdog" "frontmatter" "pydantic")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $package installed"
    else
        echo -e "${RED}✗${NC} $package missing"
        MISSING_PACKAGES+=($package)
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Missing packages. Install with:${NC}"
    echo "pip install python-dotenv playwright watchdog python-frontmatter pydantic"
    exit 1
fi
echo ""

# Check 3: Playwright browser
echo "Check 3: Playwright browser (chromium)..."
if playwright show-trace 2>&1 | grep -q "chromium"; then
    echo -e "${GREEN}✓${NC} Playwright chromium installed"
else
    echo -e "${YELLOW}⚠${NC} Playwright chromium may not be installed"
    echo "Run: playwright install chromium"
fi
echo ""

# Check 4: Vault directory
echo "Check 4: Vault directory..."
if [ -d "AI_Employee_Vault" ]; then
    echo -e "${GREEN}✓${NC} AI_Employee_Vault exists"

    if [ -d "AI_Employee_Vault/Needs_Action" ]; then
        echo -e "${GREEN}✓${NC} Needs_Action folder exists"
    else
        echo -e "${YELLOW}⚠${NC} Needs_Action folder missing (will be created)"
        mkdir -p AI_Employee_Vault/Needs_Action
    fi
else
    echo -e "${RED}✗${NC} AI_Employee_Vault not found"
    echo "Create it with: mkdir -p AI_Employee_Vault/Needs_Action"
    exit 1
fi
echo ""

# Check 5: .env file
echo "Check 5: .env configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"

    # Check required variables
    if grep -q "VAULT_PATH" .env; then
        echo -e "${GREEN}✓${NC} VAULT_PATH configured"
    else
        echo -e "${YELLOW}⚠${NC} VAULT_PATH not set in .env"
    fi

    if grep -q "WHATSAPP_SESSION_FILE" .env; then
        echo -e "${GREEN}✓${NC} WHATSAPP_SESSION_FILE configured"
    else
        echo -e "${YELLOW}⚠${NC} WHATSAPP_SESSION_FILE not set in .env"
    fi
else
    echo -e "${YELLOW}⚠${NC} .env file not found"
    echo "Create it with: cp .env.whatsapp .env"
fi
echo ""

# Check 6: WhatsApp session
echo "Check 6: WhatsApp session..."
if [ -f ".whatsapp_session.json" ]; then
    echo -e "${GREEN}✓${NC} WhatsApp session file exists"
    echo "  Session is initialized (QR code already scanned)"
else
    echo -e "${YELLOW}⚠${NC} WhatsApp session not initialized"
    echo "  Run: python -m watchers.whatsapp_watcher --init --vault-path AI_Employee_Vault"
fi
echo ""

# Check 7: WhatsApp watcher file
echo "Check 7: WhatsApp watcher module..."
if [ -f "watchers/whatsapp_watcher.py" ]; then
    echo -e "${GREEN}✓${NC} whatsapp_watcher.py exists"

    # Check if it's importable
    if python3 -c "from watchers.whatsapp_watcher import WhatsAppWatcher" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} WhatsAppWatcher class can be imported"
    else
        echo -e "${RED}✗${NC} WhatsAppWatcher class cannot be imported"
        echo "Check for syntax errors or missing dependencies"
    fi
else
    echo -e "${RED}✗${NC} whatsapp_watcher.py not found"
    exit 1
fi
echo ""

# Check 8: Company Handbook
echo "Check 8: Company Handbook..."
if [ -f "AI_Employee_Vault/Company_Handbook.md" ]; then
    echo -e "${GREEN}✓${NC} Company_Handbook.md exists"

    if grep -q "Monitored WhatsApp Contacts" AI_Employee_Vault/Company_Handbook.md; then
        echo -e "${GREEN}✓${NC} Monitored contacts section found"
        CONTACT_COUNT=$(grep -A 10 "Monitored WhatsApp Contacts" AI_Employee_Vault/Company_Handbook.md | grep "^-" | wc -l)
        echo "  Monitoring $CONTACT_COUNT specific contacts"
    else
        echo -e "${YELLOW}⚠${NC} No monitored contacts section (will monitor all contacts)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Company_Handbook.md not found"
    echo "  Watcher will work but won't have contact filtering"
fi
echo ""

# Summary
echo "=========================================="
echo "Setup Verification Summary"
echo "=========================================="
echo ""

if [ -f ".whatsapp_session.json" ]; then
    echo -e "${GREEN}✓ Ready to run!${NC}"
    echo ""
    echo "Start the watcher with:"
    echo "  python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault"
else
    echo -e "${YELLOW}⚠ Almost ready!${NC}"
    echo ""
    echo "Next step: Initialize WhatsApp session"
    echo "  python -m watchers.whatsapp_watcher --init --vault-path AI_Employee_Vault"
fi
echo ""

# Test command
echo "=========================================="
echo "Test Commands"
echo "=========================================="
echo ""
echo "1. Initialize session (first time):"
echo "   python -m watchers.whatsapp_watcher --init --vault-path AI_Employee_Vault"
echo ""
echo "2. Run watcher:"
echo "   python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault"
echo ""
echo "3. Run tests:"
echo "   pytest tests/integration/test_whatsapp_watcher.py -v"
echo ""
echo "4. View help:"
echo "   python -m watchers.whatsapp_watcher --help"
echo ""
