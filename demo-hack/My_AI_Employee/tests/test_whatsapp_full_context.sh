#!/bin/bash
# WhatsApp Watcher - Full Context Test
# Tests the new click-into-chats implementation

echo "=========================================="
echo "WhatsApp Watcher - Full Context Test"
echo "=========================================="
echo ""
echo "NEW FEATURES:"
echo "✓ Clicks into chats to read ALL messages"
echo "✓ Provides full conversation context"
echo "✓ Fixed deduplication (phone number vs name)"
echo "✓ Messages marked as read (natural deduplication)"
echo ""
echo "EXPECTED BEHAVIOR:"
echo "1. Scan QR code to login"
echo "2. Watcher detects unread messages from monitored contacts"
echo "3. Clicks into each chat with unread messages"
echo "4. Reads ALL messages (not just last preview)"
echo "5. Creates action item with full context"
echo "6. No duplicate action items on subsequent runs"
echo ""
echo "TEST SCENARIO:"
echo "If you have 3 messages:"
echo "  - 'hey john how are you?'"
echo "  - 'john are you comming to the party'"
echo "  - 'reply asap'"
echo ""
echo "The action item will contain ALL 3 messages with timestamps,"
echo "not just 'reply asap'"
echo ""
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop after messages are detected"
echo ""

cd "$(dirname "$0")/.."

# Clear deduplication file for fresh test
if [ -f .whatsapp_dedupe.json ]; then
    echo "Clearing deduplication file for fresh test..."
    rm .whatsapp_dedupe.json
    echo ""
fi

# Run the watcher with uv
uv run python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault
