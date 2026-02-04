#!/bin/bash
# Quick test script for WhatsApp watcher

echo "=========================================="
echo "WhatsApp Watcher Test"
echo "=========================================="
echo ""
echo "This will:"
echo "1. Ask you to scan QR code (session persistence issue)"
echo "2. Detect ALL messages from 'Uneeza BETA.'"
echo "3. Create action items in Needs_Action/"
echo ""
echo "Expected: 4 action items created (one for each unread message)"
echo ""
echo "Press Ctrl+C to stop the watcher after messages are detected"
echo ""
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault
