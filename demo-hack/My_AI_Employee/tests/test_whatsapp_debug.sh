#!/bin/bash
# WhatsApp Watcher Debug Test

echo "=========================================="
echo "WhatsApp Watcher - Debug Mode"
echo "=========================================="
echo ""
echo "This will show detailed debug information about:"
echo "- How many chats are in your chat list"
echo "- Which chats have unread badges"
echo "- What contact names are detected"
echo "- Which selector is working/not working"
echo ""
echo "After scanning QR code, wait for one check cycle (60 seconds)"
echo "Then press Ctrl+C and share the debug output"
echo ""
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault
