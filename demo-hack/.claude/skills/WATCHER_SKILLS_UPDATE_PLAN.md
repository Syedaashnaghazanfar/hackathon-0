# Watcher Skills Update Action Plan

This document provides step-by-step instructions for updating both watcher skills to align with the new unified `run_watcher.py` and reorganized project structure.

## Executive Summary

**Status**: Both watcher skills need updates to reference the new unified runner
**Impact**: Medium - Skills will work but reference outdated commands
**Effort**: 30 minutes to complete all updates
**Priority**: High - Should be done before next use

## Files Status Overview

### watcher-runner-filesystem (Bronze Tier)

| File | Status | Action |
|------|--------|--------|
| `SKILL.md` | ⚠️ Needs update | Replace with SKILL_UPDATED.md |
| `examples.md` | ⚠️ Needs update | Replace with examples_UPDATED.md |
| `references/runbook.md` | ✅ OK | Minor updates only (optional) |
| `scripts/create_test_drop.py` | ✅ OK | No changes needed |
| `templates/` | ✅ OK | No changes needed |

### multi-watcher-runner (Silver Tier)

| File | Status | Action |
|------|--------|--------|
| `SKILL.md` | ⚠️ Needs update | Replace with SKILL_UPDATED.md |
| `examples.md` | ⚠️ Needs update | Replace with examples_UPDATED.md |
| `references/watcher-configuration.md` | ⚠️ Minor updates | Update paths to scripts/ |
| `references/gmail-api-setup.md` | ✅ OK | No changes needed |
| `references/whatsapp-web-session.md` | ✅ OK | No changes needed |
| `references/error-recovery.md` | ✅ OK | No changes needed |
| `scripts/orchestrate_watchers.py` | ❌ Obsolete | Delete (replaced by run_watcher.py) |
| `scripts/monitor_watchers.py` | ❌ Obsolete | Delete (use PM2 or logs) |
| `scripts/restart_watcher.py` | ❌ Obsolete | Delete (use PM2 restart) |
| `templates/company_handbook_section.md` | ✅ OK | No changes needed |

## Step-by-Step Update Instructions

### Phase 1: Backup Current Files (5 minutes)

```bash
cd /mnt/d/hackathon-0/.claude/skills

# Backup watcher-runner-filesystem
cd watcher-runner-filesystem
cp SKILL.md SKILL_OLD.md
cp examples.md examples_OLD.md
cd ..

# Backup multi-watcher-runner
cd multi-watcher-runner
cp SKILL.md SKILL_OLD.md
cp examples.md examples_OLD.md
cd ..
```

### Phase 2: Update watcher-runner-filesystem (5 minutes)

```bash
cd /mnt/d/hackathon-0/.claude/skills/watcher-runner-filesystem

# Replace SKILL.md
mv SKILL_UPDATED.md SKILL.md

# Replace examples.md
mv examples_UPDATED.md examples.md

# Optional: Update runbook.md (minor changes)
# Edit references/runbook.md to mention:
# - Use "uv run python run_watcher.py --watcher filesystem" instead of direct watcher file
# - Reference WATCHER_RUNNER_GUIDE.md for detailed usage
```

### Phase 3: Update multi-watcher-runner (10 minutes)

```bash
cd /mnt/d/hackathon-0/.claude/skills/multi-watcher-runner

# Replace SKILL.md
mv SKILL_UPDATED.md SKILL.md

# Replace examples.md
mv examples_UPDATED.md examples.md

# Delete obsolete scripts
rm scripts/orchestrate_watchers.py
rm scripts/monitor_watchers.py
rm scripts/restart_watcher.py

# Optional: Update watcher-configuration.md
# Edit references/watcher-configuration.md to:
# - Update script paths to point to My_AI_Employee/scripts/
# - Reference unified run_watcher.py
```

### Phase 4: Verify Updates (5 minutes)

```bash
# Test watcher-runner-filesystem skill
# In Claude Code, invoke:
/watcher-runner-filesystem

# Test multi-watcher-runner skill
# In Claude Code, invoke:
/multi-watcher-runner

# Verify both skills reference:
# - uv run python run_watcher.py
# - Correct paths to scripts/setup/, scripts/debug/, scripts/validate/
# - WATCHER_RUNNER_GUIDE.md
```

### Phase 5: Clean Up (5 minutes)

```bash
cd /mnt/d/hackathon-0/.claude/skills

# After verifying skills work correctly, delete backups
rm watcher-runner-filesystem/SKILL_OLD.md
rm watcher-runner-filesystem/examples_OLD.md
rm multi-watcher-runner/SKILL_OLD.md
rm multi-watcher-runner/examples_OLD.md
```

## Detailed File Changes

### watcher-runner-filesystem/SKILL.md

**Old approach:**
```bash
# Direct watcher file execution
python watchers/filesystem_watcher.py
```

**New approach:**
```bash
# Unified runner
uv run python run_watcher.py --watcher filesystem
```

**Key changes:**
- All commands use `run_watcher.py --watcher filesystem`
- References to `scripts/setup/`, `scripts/debug/`, `scripts/validate/`
- Links to `WATCHER_RUNNER_GUIDE.md`
- Updated troubleshooting section

### watcher-runner-filesystem/examples.md

**Old approach:**
- Examples showed direct watcher execution
- Referenced old project structure

**New approach:**
- All examples use unified runner
- Reference new scripts/ organization
- Include validation script examples
- Show integration with other skills

### multi-watcher-runner/SKILL.md

**Old approach:**
```bash
# Old orchestrator script
python scripts/orchestrate_watchers.py
```

**New approach:**
```bash
# Unified runner with orchestration
uv run python run_watcher.py --watcher all
```

**Key changes:**
- All commands use `run_watcher.py --watcher all` or `--watcher <name>`
- Removed references to obsolete scripts
- Added PM2 and systemd deployment options
- Updated architecture diagram
- References to new scripts/ organization

### multi-watcher-runner/examples.md

**Old approach:**
- Examples showed old orchestrator script
- Referenced scripts that no longer exist

**New approach:**
- All examples use unified runner
- Individual watcher examples: `--watcher gmail`, `--watcher linkedin`, etc.
- Orchestrated mode: `--watcher all`
- Production deployment with PM2
- Integration with approval workflow

### multi-watcher-runner/scripts/ (DELETE)

**Files to delete:**
- `orchestrate_watchers.py` - Replaced by `run_watcher.py --watcher all`
- `monitor_watchers.py` - Use PM2 monitoring or logs instead
- `restart_watcher.py` - Use PM2 restart or just restart run_watcher.py

**Why delete:**
- Functionality duplicated in unified runner
- Confusing to have multiple ways to run watchers
- Maintenance burden

## Optional Updates (Low Priority)

### watcher-runner-filesystem/references/runbook.md

**Current**: References direct watcher execution
**Update**: Add note about unified runner

```markdown
## Running the Watcher

**New (Recommended):**
```bash
uv run python run_watcher.py --watcher filesystem
```

**Old (Deprecated):**
```bash
python watchers/filesystem_watcher.py
```

See `WATCHER_RUNNER_GUIDE.md` for detailed usage.
```

### multi-watcher-runner/references/watcher-configuration.md

**Current**: References old script paths
**Update**: Update paths to new structure

```markdown
## Setup Scripts

Located in `My_AI_Employee/scripts/setup/`:
- `setup_gmail_oauth.py` - Gmail OAuth setup
- `setup_gmail_oauth_manual.py` - Manual OAuth for WSL
- `complete_oauth.py` - Complete OAuth flow

## Debug Scripts

Located in `My_AI_Employee/scripts/debug/`:
- `debug_gmail.py` - Test Gmail connection
- `debug_gmail_send.py` - Test email sending
- `debug_pm2_dashboard.py` - Test PM2 integration
```

## Testing Checklist

After completing updates, verify:

- [ ] `/watcher-runner-filesystem` skill loads without errors
- [ ] `/multi-watcher-runner` skill loads without errors
- [ ] SKILL.md references `run_watcher.py` correctly
- [ ] examples.md shows correct commands
- [ ] No references to deleted scripts
- [ ] Links to `WATCHER_RUNNER_GUIDE.md` work
- [ ] References to `scripts/setup/`, `scripts/debug/`, `scripts/validate/` are correct
- [ ] Obsolete scripts deleted from multi-watcher-runner/scripts/

## Rollback Plan

If updates cause issues:

```bash
cd /mnt/d/hackathon-0/.claude/skills

# Restore watcher-runner-filesystem
cd watcher-runner-filesystem
mv SKILL_OLD.md SKILL.md
mv examples_OLD.md examples.md
cd ..

# Restore multi-watcher-runner
cd multi-watcher-runner
mv SKILL_OLD.md SKILL.md
mv examples_OLD.md examples.md
# Restore deleted scripts from git if needed
cd ..
```

## Benefits of Updates

### For Users
✅ **Consistent interface** - One command for all watchers
✅ **Better documentation** - Clear examples and troubleshooting
✅ **Easier debugging** - Unified logging and error handling
✅ **Production ready** - PM2 and systemd deployment options

### For Maintenance
✅ **Less duplication** - One runner instead of multiple scripts
✅ **Easier updates** - Update run_watcher.py, skills stay current
✅ **Clear organization** - Scripts in scripts/, tests in tests/
✅ **Better discoverability** - WATCHER_RUNNER_GUIDE.md as single source of truth

## Timeline

- **Phase 1 (Backup)**: 5 minutes
- **Phase 2 (Update filesystem skill)**: 5 minutes
- **Phase 3 (Update multi-watcher skill)**: 10 minutes
- **Phase 4 (Verify)**: 5 minutes
- **Phase 5 (Clean up)**: 5 minutes

**Total**: ~30 minutes

## Next Steps

1. **Execute Phase 1-5** following the step-by-step instructions above
2. **Test both skills** by invoking them in Claude Code
3. **Update any other documentation** that references old watcher commands
4. **Clean up backups** once verified working

## Questions?

- **Q: Can I keep the old scripts for backward compatibility?**
  - A: Not recommended. Having multiple ways to run watchers is confusing. The unified runner is better in every way.

- **Q: What if I have custom scripts that reference the old orchestrator?**
  - A: Update them to use `run_watcher.py --watcher all` instead.

- **Q: Do I need to update .env or other configuration?**
  - A: No, the unified runner uses the same .env variables.

- **Q: Will this break existing workflows?**
  - A: No, the unified runner is a superset of functionality. Everything that worked before still works.

## Summary

**Action Required**: Replace 4 files, delete 3 obsolete scripts
**Time Required**: 30 minutes
**Risk**: Low (easy rollback with backups)
**Benefit**: High (consistent interface, better documentation, easier maintenance)

**Recommendation**: Complete all updates now to avoid confusion later.
