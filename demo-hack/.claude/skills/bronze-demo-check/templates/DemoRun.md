# Bronze tier demo run (filesystem watcher)

## 1) Show vault structure

- Open vault root
- Show: `Dashboard.md`, `Company_Handbook.md`, `Inbox/`, `Needs_Action/`, `Done/`

## 2) Trigger watcher

- Start watcher
- Create a new file in WATCH_FOLDER

## 3) Show watcher output

- Show the new `Needs_Action/*.md` created by watcher

## 4) Process with Claude

- Run Claude with a prompt like:
  - "@needs-action-triage\nProcess Needs_Action and create plans + update Dashboard."

## 5) Show results

- Show plan file created
- Show `Dashboard.md` updated
- Show original item moved to `Done/`
