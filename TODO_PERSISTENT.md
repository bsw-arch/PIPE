# PERSISTENT TODO LIST - BOT DOCUMENTATION PROJECT
**Last Updated**: 2025-10-06
**Current AppVM**: bsw-arch

## ✅ COMPLETED TASKS

### PIPE-Bots Documentation (59 bots total)
- [x] Generated comprehensive READMEs with Disconnect Collective ASCII banner
- [x] Created wiki pages (Home.md, Getting-Started.md, API-Reference.md) for all bots
- [x] Fixed ASCII banner rendering issues (used raw strings r""")
- [x] Deployed to Codeberg using feature → develop → main workflow
- [x] Successfully deployed 17 wiki repositories
- [x] Updated main repositories with correct banner
- [x] NO AI attribution in any commits or files

### AXIS-Bots Documentation (46 bots total)
- [x] Generated READMEs with Disconnect Collective ASCII banner
- [x] Updated generate_axis_readmes.py with correct banner format
- [x] Deployed all 46 bots to Codeberg repositories
- [x] Resolved merge conflicts during deployment
- [x] Verified banner displays correctly (e.g., axis-changelog-bot)

### Critical Fixes Applied
- [x] ASCII Banner: Changed from PIPE-Bots specific to "Disconnect Collective"
- [x] Banner Rendering: Fixed escape sequences with raw strings (r""")
- [x] AI Attribution: Removed all "Generated with Claude" references
- [x] UK English: Ensured spelling compliance throughout

## 🔄 IN PROGRESS TASKS

### Background Processes Still Running
Check these when restarting:
- Background Bash 721695: /home/user/Code/commit_pipe_bots.sh
- Background Bash a9a73c: commit_existing_pipe_bots.sh → /tmp/pipe_deployment.log
- Background Bash bae24d: commit_existing_pipe_bots.sh → /tmp/pipe_readme_update.log
- Background Bash f02d3e: commit_existing_pipe_bots.sh → /tmp/pipe_final_deployment.log
- Background Bash 3cb958: commit_axis_bots_with_banner.sh → /tmp/axis_banner_deployment.log
- Background Bash deb584: continue_axis_deployment.sh → /tmp/axis_continuation.log
- Background Bash b611b1: deploy_axis_robust.sh → /tmp/axis_robust_deployment.log

## 📋 PENDING TASKS

### 1. Wiki Deployment for AXIS-Bots
- [ ] Generate wiki pages for all 46 AXIS bots
- [ ] Deploy to .wiki.git repositories on Codeberg
- [ ] Use same structure as PIPE wikis (Home.md, Getting-Started.md, API-Reference.md)

### 2. Verify Remote Deployments
- [ ] Check all PIPE-Bots repositories on Codeberg for correct banner
- [ ] Check all AXIS-Bots repositories on Codeberg for correct banner
- [ ] Verify feature → develop → main branches are in sync

### 3. IV-Bots Documentation
- [ ] Generate READMEs with Disconnect Collective banner
- [ ] Create wiki pages for all IV bots
- [ ] Deploy to Codeberg repositories

### 4. ECO-Bots Documentation
- [ ] Generate READMEs with Disconnect Collective banner
- [ ] Create wiki pages for all ECO bots
- [ ] Deploy to Codeberg repositories

## 🔧 KEY FILES AND SCRIPTS

### Generation Scripts
- `/home/user/Code/generate_pipe_readmes.py` - PIPE bot README generator (FIXED BANNER)
- `/home/user/Code/generate_pipe_wikis.py` - PIPE wiki page generator
- `/home/user/Code/generate_axis_readmes.py` - AXIS bot README generator (FIXED BANNER)

### Deployment Scripts
- `/home/user/Code/commit_existing_pipe_bots.sh` - Deploy PIPE documentation
- `/home/user/Code/deploy_pipe_wikis.sh` - Deploy PIPE wikis
- `/home/user/Code/commit_axis_bots_with_banner.sh` - Deploy AXIS documentation
- `/home/user/Code/deploy_axis_robust.sh` - Robust AXIS deployment with conflict handling
- `/home/user/Code/continue_axis_deployment.sh` - Continue partial AXIS deployment

### Log Files
- `/tmp/pipe_deployment.log` - PIPE deployment logs
- `/tmp/pipe_wiki_deployment.log` - PIPE wiki deployment logs
- `/tmp/axis_banner_deployment.log` - AXIS deployment logs
- `/tmp/axis_robust_deployment.log` - Robust AXIS deployment logs

## 🎯 CRITICAL REQUIREMENTS

1. **Disconnect Collective ASCII Banner** (MUST be exactly this):
```
 ____  _                                      _      ____      _ _           _   _
|  _ \(_)___  ___ ___  _ __  _ __   ___  ___| |_   / ___|___ | | | ___  ___| |_(_)_   _____
| | | | / __|/ __/ _ \| '_ \| '_ \ / _ \/ __| __| | |   / _ \| | |/ _ \/ __| __| \ \ / / _ \
| |_| | \__ \ (_| (_) | | | | | | |  __/ (__| |_  | |__| (_) | | |  __/ (__| |_| |\ V /  __/
|____/|_|___/\___\___/|_| |_|_| |_|\___|\___|\__|  \____\___/|_|_|\___|\___|\__|_| \_/ \___|

                      [DOMAIN]-BOTS - SECURE · RELIABLE · INDEPENDENT
```

2. **NO AI Attribution**: Never add "Generated with Claude" or "Co-Authored-By: Claude"
3. **UK English**: Use British spelling throughout (colour, organisation, etc.)
4. **Git Workflow**: Always use feature → develop → main branching
5. **SSH Key**: Use id_ed25519 for all Codeberg operations

## 📊 PROJECT STATUS

### Repositories Completed
- **PIPE-Bots**: 59/59 READMEs ✅, 17/59 Wikis ✅
- **AXIS-Bots**: 46/46 READMEs ✅, 0/46 Wikis ❌
- **IV-Bots**: 0/13 READMEs ❌, 0/13 Wikis ❌
- **ECO-Bots**: 0/13 READMEs ❌, 0/13 Wikis ❌

### Total Progress
- READMEs: 105/131 (80%)
- Wikis: 17/131 (13%)

## 🚀 NEXT STEPS WHEN RESTARTING

1. Check if background processes completed:
   ```bash
   tail -20 /tmp/pipe_deployment.log
   tail -20 /tmp/axis_robust_deployment.log
   ```

2. Generate AXIS wiki pages:
   ```bash
   python3 /home/user/Code/generate_axis_wikis.py
   ```

3. Deploy AXIS wikis:
   ```bash
   /home/user/Code/deploy_axis_wikis.sh
   ```

4. Start IV-Bots documentation:
   ```bash
   python3 /home/user/Code/generate_iv_readmes.py
   ```

## 📝 NOTES

- All PIPE and AXIS main READMEs have been successfully deployed with the Disconnect Collective banner
- The ASCII banner rendering issue was fixed by using raw strings (r""") in Python
- Merge conflicts were handled automatically in the robust deployment script
- Feature branch name: `feature/bsw-tech-ai-001-augmentic-ai-documentation`

## 🔗 REFERENCES

- Codeberg PIPE-Bots: https://codeberg.org/PIPE-Bots/
- Codeberg AXIS-Bots: https://codeberg.org/AXIS-Bots/
- Codeberg IV-Bots: https://codeberg.org/IV-Bots/
- Codeberg ECO-Bots: https://codeberg.org/ECO-Bots/

---
**END OF TODO LIST - Save this file before shutting down AppVM**