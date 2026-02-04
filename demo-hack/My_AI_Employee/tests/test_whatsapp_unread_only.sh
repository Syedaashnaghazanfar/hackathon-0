#!/bin/bash
# WhatsApp Watcher - Test Unread Messages Only

echo "=========================================="
echo "WhatsApp Watcher - Unread Messages Only Test"
echo "=========================================="
echo ""
echo "FIXED BEHAVIOR:"
echo "✓ Reads ONLY unread messages (not old ones)"
echo "✓ If 2 unread → reads last 2 messages"
echo "✓ If 3 unread → reads last 3 messages"
echo ""
echo "TEST INSTRUCTIONS:"
echo "1. Send 2-3 NEW test messages to Uneeza contact"
echo "2. Watcher will detect unread badge"
echo "3. Click into chat and read ONLY those unread messages"
echo "4. Create action item with ONLY new messages"
echo ""
echo "EXPECTED LOG OUTPUT:"
echo "  'Reading last 2 unread message(s) from Uneeza (total messages in chat: 12)'"
echo ""
echo "This means: 12 total messages in chat, but only reading last 2 (the unread ones)"
echo ""
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# Run the watcher
uv run python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault
