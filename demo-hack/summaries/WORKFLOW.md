Step 1: Start the Watcher

  Open a terminal and run:
  cd /mnt/d/hackathon-0/My_AI_Employee
  uv run python run_watcher.py

  You'll see output like:
  ============================================================
  Bronze Tier AI Employee - Filesystem Watcher
  ============================================================
  Vault path: /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault
  Watch folder: /mnt/d/hackathon-0/My_AI_Employee/test_watch_folder
  Watch mode: polling
  Check interval: 60s
  ============================================================
  FilesystemWatcher initialized
  Watching folder: /mnt/d/hackathon-0/My_AI_Employee/test_watch_folder
  Press Ctrl+C to stop

  Leave this terminal running! The watcher is now monitoring your watch folder.

  ---
  Step 2: Add a File (ANY File)

  Open a new terminal (keep the watcher running in the first one) and drop ANY file into the watch folder:

  Example 1: Text file
  echo "Please review this urgent proposal.

  The client needs a response by Friday.

  Priority: High
  Category: Client Work" > /mnt/d/hackathon-0/My_AI_Employee/test_watch_folder/urgent_proposal.txt

  Example 2: Copy an existing file
  cp /path/to/your/document.pdf /mnt/d/hackathon-0/My_AI_Employee/test_watch_folder/

  Example 3: Create any file
  # Any file type works: .txt, .pdf, .docx, .jpg, etc.
  touch /mnt/d/hackathon-0/My_AI_Employee/test_watch_folder/meeting_notes.txt

  ---
  Step 3: Watcher Detects and Creates Action Item

  Wait 5-60 seconds (depending on your CHECK_INTERVAL setting).

  In the watcher terminal, you'll see:
  2026-01-13 18:30:45 - FilesystemWatcher - INFO - New file detected: urgent_proposal.txt
  2026-01-13 18:30:45 - FilesystemWatcher - INFO - Created action item: 20260113_183045_123456_urgent_proposal.md

  What happened?
  - Watcher saw the new file
  - Generated a unique ID (SHA256 hash)
  - Created a markdown file in Needs_Action/ folder
  - Added frontmatter with metadata

  ---
  Step 4: Check the Action Item

  Look in the Needs_Action/ folder:
  ls -la /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault/Needs_Action/

  You'll see a file like: 20260113_183045_123456_urgent_proposal.md

  View it:
  cat /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault/Needs_Action/20260113_183045_123456_urgent_proposal.md

  It looks like:
  ---
  detected: '2026-01-13T18:30:45.123456'
  file_id: abc123def456...
  received: '2026-01-13T18:30:45.123456'
  source_path: /path/to/urgent_proposal.txt
  status: pending
  type: file_drop
  ---

  # Action Required: urgent_proposal.txt

  ## Source File
  - **Path**: `/path/to/urgent_proposal.txt`
  - **Size**: 196 bytes
  - **Modified**: 2026-01-13T18:30:40

  ## Description
  New file detected in watch folder. Review and determine appropriate action.

  ## Next Steps
  - [ ] Review file contents
  - [ ] Determine priority and category
  - [ ] Create plan if needed
  - [ ] Archive to Done when complete

  ---
  Step 5: Process with Claude Code

  Open Claude Code in your project and type:
  @needs-action-triage

  Or say:
  Process the pending action items in Needs_Action folder

  Claude will:
  1. Read all .md files in Needs_Action/
  2. Read Company_Handbook.md for rules
  3. Analyze each item
  4. Create a plan file in Plans/ folder
  5. Update Dashboard.md with activity
  6. Move the processed item to Done/ folder

  ---
  Step 6: Check the Results

  Check the Plan:
  ls -la /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault/Plans/
  cat /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault/Plans/Plan_urgent_proposal.md

  You'll see a plan with checkboxes like:
  # Plan: urgent_proposal.txt

  ## Priority: High
  ## Category: Client Work

  ## Action Items
  - [ ] Review the proposal document
  - [ ] Check client requirements
  - [ ] Draft response email
  - [ ] Get approval from manager
  - [ ] Send response by Friday

  ## Done Condition
  All checkboxes completed and client response sent.

  Check the Dashboard:
  cat /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault/Dashboard.md

  You'll see updated stats:
  ## Status Overview
  **Pending Items**: 0
  **Last Updated**: 2026-01-13 18:35:22

  ## Recent Activity
  - **2026-01-13 18:35:22**: Processed action item: urgent_proposal.md

  Check Done folder:
  ls -la /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault/Done/

  The original action item is now archived there with metadata added.

  ---
  3. What to Check in Obsidian?

  Open the Vault in Obsidian:

  1. Open Obsidian app
  2. Click "Open folder as vault"
  3. Select: /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault/

  What You'll See:

  Left Sidebar (File Explorer):
  AI_Employee_Vault/
  ├── 📁 Inbox/              (empty for now)
  ├── 📁 Needs_Action/       ← NEW ACTION ITEMS APPEAR HERE
  ├── 📁 Done/               ← PROCESSED ITEMS GO HERE
  ├── 📁 Plans/              ← GENERATED PLANS GO HERE
  ├── 📄 Dashboard.md        ← SYSTEM STATUS
  └── 📄 Company_Handbook.md ← RULES AND SETTINGS

  Things to Check:

  1. Dashboard.md - Your main status page
  - Pending item count
  - Recent activity log
  - System warnings
  - Last update time

  2. Needs_Action/ folder - New items from watcher
  - Each file is an action item waiting to be processed
  - Click to view details
  - Has frontmatter with metadata

  3. Plans/ folder - Generated plans from Claude
  - Each plan has checkboxes
  - Shows priority and category
  - Has done conditions

  4. Done/ folder - Archived completed items
  - Original action items after processing
  - Has processed timestamp added
  - Has related_plan link

  5. Company_Handbook.md - Your rules
  - Edit this to customize how Claude processes items
  - Set priority rules
  - Define categories
  - Set communication preferences

  ---
  Complete Workflow Example:

  1. You: Drop "client_email.txt" into test_watch_folder/
     ↓
  2. Watcher: Detects file, creates action item in Needs_Action/
     ↓
  3. Obsidian: You see new file in Needs_Action/ folder
     ↓
  4. You: Tell Claude "@needs-action-triage"
     ↓
  5. Claude: Reads item, creates plan, updates dashboard, archives to Done/
     ↓
  6. Obsidian: You see:
     - New plan in Plans/ folder
     - Updated Dashboard.md
     - Item moved to Done/ folder
     ↓
  7. You: Follow the plan checkboxes manually

  ---
  Quick Test Right Now:

  Terminal 1:
  cd /mnt/d/hackathon-0/My_AI_Employee
  uv run python run_watcher.py

  Terminal 2:
  echo "Test document" > /mnt/d/hackathon-0/My_AI_Employee/test_watch_folder/test.txt

  Wait 10 seconds, then check:
  ls /mnt/d/hackathon-0/My_AI_Employee/AI_Employee_Vault/Needs_Action/

  You should see a new .md file! 🎉