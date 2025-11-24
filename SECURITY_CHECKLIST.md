# Security Checklist for Collaboration

## 🔒 Critical Security Items

### Before Sharing Repository

- [ ] **Remove hardcoded secrets** from all source files
- [ ] **Review .gitignore** - Ensure sensitive files are excluded
- [ ] **Check commit history** for accidentally committed secrets
- [ ] **Verify .env.example** contains only placeholder values
- [ ] **Remove production API keys** and replace with placeholders
- [ ] **Document secret management** process for team

### Files to Review

1. **src/license/manager.py**
   - ⚠️ Contains hardcoded `SECRET_KEY = "3d_conv_app_secret_2025"`
   - **ACTION REQUIRED**: Move to environment variable

2. **.env files**
   - ✅ `.env` is git-ignored
   - ✅ `.env.example` contains only examples

3. **Configuration files**
   - [ ] Check `config.yaml` for sensitive data
   - [ ] Review any API endpoint configurations

### Recommended Actions

#### 1. Move Secret Key to Environment Variable

**In `.env.example`:**
```bash
# License validation secret key (generate unique key for your environment)
LICENSE_SECRET_KEY=your_secret_key_here
```

**In `src/license/manager.py`:**
```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LicenseManager:
    # Get secret from environment, fallback to default for development
    SECRET_KEY = os.getenv('LICENSE_SECRET_KEY', 'dev_default_secret_key_not_for_production')
    
    # Warn if using default
    if SECRET_KEY == 'dev_default_secret_key_not_for_production':
        import logging
        logging.warning("⚠️  Using default secret key! Set LICENSE_SECRET_KEY in .env for production")
```

#### 2. Generate Production Secret

```python
# Run this to generate a secure secret key
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"LICENSE_SECRET_KEY={secret_key}")
```

#### 3. Update Documentation

Add to README.md or CONTRIBUTING.md:
```markdown
### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

**Required for production:**
- `LICENSE_SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
```

## 🔐 Security Best Practices for Team

### For All Developers

1. **Never commit secrets**
   - No API keys, passwords, or tokens in code
   - Use environment variables
   - Review changes before committing: `git diff`

2. **Use .env files**
   - Store secrets in `.env` (git-ignored)
   - Commit only `.env.example` with placeholders
   - Each developer has their own `.env`

3. **Review pull requests**
   - Check for hardcoded credentials
   - Verify no sensitive data in logs
   - Ensure input validation present

4. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

5. **Scan for secrets**
   ```bash
   # Install git-secrets or gitleaks
   brew install gitleaks  # macOS
   
   # Scan repository
   gitleaks detect --source . --verbose
   ```

### For Repository Maintainers

1. **Enable branch protection**
   - Require pull request reviews
   - Require status checks to pass
   - No force pushes to main/develop

2. **Set up secret scanning**
   - GitHub Advanced Security (if available)
   - Pre-commit hooks with secret detection
   - CI/CD pipeline secret scanning

3. **Manage access properly**
   - Principle of least privilege
   - Use teams for permission management
   - Regular access reviews

4. **Document security procedures**
   - Incident response plan
   - Secret rotation schedule
   - Vulnerability disclosure process

## 🚨 What to Do If Secrets Are Exposed

### If Committed to Local Branch (Not Pushed)

1. **Remove from history:**
   ```bash
   # If last commit
   git reset --soft HEAD~1
   git restore --staged <file>
   
   # Edit file, remove secret
   # Commit again
   git add <file>
   git commit -m "fix: remove sensitive data"
   ```

2. **For older commits:**
   ```bash
   # Use interactive rebase
   git rebase -i HEAD~5  # Adjust number as needed
   # Mark commit as 'edit', remove secret, continue
   git rebase --continue
   ```

### If Pushed to Remote

1. **Rotate the secret immediately**
   - Generate new key/token
   - Update production systems
   - Revoke old secret

2. **Remove from history** (destructive, coordinate with team):
   ```bash
   # Use BFG Repo-Cleaner or git-filter-repo
   brew install bfg  # macOS
   
   # Clone a fresh copy
   git clone --mirror https://github.com/WHICHYOU/3D-APP-PYTHON.git
   
   # Remove secrets
   bfg --replace-text secrets.txt 3D-APP-PYTHON.git
   
   # Push changes (force)
   cd 3D-APP-PYTHON.git
   git reflog expire --expire=now --all && git gc --prune=now --aggressive
   git push --force
   ```

3. **Notify team**
   - All developers need to re-clone
   - Update CI/CD systems
   - Check for usage of old secret

### Immediate Actions Checklist

- [ ] Rotate exposed secret
- [ ] Update production systems with new secret
- [ ] Revoke old secret from all services
- [ ] Remove from git history if pushed
- [ ] Notify security team/lead
- [ ] Document incident
- [ ] Review how it happened
- [ ] Implement preventive measures

## 🛡️ Prevention Strategies

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: detect-private-key
      - id: detect-aws-credentials

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.16.0
    hooks:
      - id: gitleaks
```

Install:
```bash
pip install pre-commit
pre-commit install
```

### Environment Variable Management

**Development:**
```bash
# .env (git-ignored)
DEBUG_MODE=true
LICENSE_SECRET_KEY=dev-key-123-not-for-production
```

**Staging/Production:**
- Use cloud secret managers (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
- Or encrypted configuration management (Ansible Vault, HashiCorp Vault)

### Code Review Checklist

Before approving any PR, check:
- [ ] No hardcoded credentials or API keys
- [ ] No sensitive data in logs
- [ ] Input validation for user data
- [ ] Error messages don't leak sensitive info
- [ ] File operations are safe (no path traversal)
- [ ] Dependencies are secure and up-to-date

## 📚 Additional Resources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [git-secrets Tool](https://github.com/awslabs/git-secrets)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

## ✅ Pre-Share Checklist

Before sharing repository with team:

- [ ] All secrets moved to environment variables
- [ ] `.env.example` updated with required variables
- [ ] No production credentials in code
- [ ] `.gitignore` properly configured
- [ ] Secret scanning enabled (if possible)
- [ ] Pre-commit hooks configured
- [ ] CONTRIBUTING.md documents security practices
- [ ] Team trained on security best practices
- [ ] Incident response plan documented
- [ ] Regular security review scheduled

---

**Remember**: Security is everyone's responsibility. When in doubt, ask!
