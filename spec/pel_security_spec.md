# PEL Security Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Canonical URL:** https://spec.pel-lang.org/v0.1/security

---

## 1. Threat Model

### 1.1 Assumptions

**Trusted:**
- PEL compiler (built from source or official binaries)
- PEL runtime (same)
- Operating system

**Untrusted:**
- Third-party PEL modules (downloaded from internet)
- User-authored model code (could contain errors or malice)
- Data sources (CSV files, APIs)

### 1.2 Security Goals

1. **Sandbox execution:** Models cannot access files, network, or system resources unless explicitly granted
2. **Data confidentiality:** Models cannot exfiltrate sensitive data
3. **Resource limits:** Models cannot consume unbounded CPU/memory
4. **Code integrity:** Verify third-party modules are unmodified
5. **Supply chain security:** Package provenance and signing

---

## 2. Execution Sandbox

### 2.1 Restrictions

**PEL models execute in restricted environment:**

**DENIED by default:**
- File system access (read/write)
- Network access (HTTP, TCP, UDP)
- Process spawning (subprocess, shell commands)
- System calls (raw access to OS)
- Dynamic code execution (eval, exec)

**ALLOWED:**
- Pure computation (arithmetic, functions)
- Memory allocation (within limits)
- Reading pre-loaded data (passed at invocation)

### 2.2 Capability-Based Permissions

**Explicit opt-in required for I/O:**

```pel
// At top of model file
capabilities: {
  file_read: ["data/cohorts.csv"],  // Whitelist specific files
  http: ["https://api.stripe.com"]  // Whitelist specific domains
}
```

**Runtime enforcement:**
```python
runtime = PELRuntime(
    model="model.pel",
    capabilities={
        "file_read": ["data/cohorts.csv"],  # Must match model declaration
        "http": []  # Deny all HTTP even if model requests it
    }
)
```

### 2.3 Implementation (Python)

**Use Python's restricted execution:**

```python
import ast
import types

class SafeExecutor:
    ALLOWED_BUILTINS = frozenset([
        'abs', 'min', 'max', 'sum', 'len', 'range', 'enumerate',
        'zip', 'map', 'filter', 'sorted'
    ])
    
    def execute(self, code: str, globals_dict: dict):
        # Parse AST
        tree = ast.parse(code)
        
        # Validate: no imports, no file I/O, no subprocess
        validator = SafetyValidator()
        validator.visit(tree)  # Raises SecurityError if unsafe
        
        # Execute with restricted builtins
        safe_globals = {
            '__builtins__': {k: __builtins__[k] for k in self.ALLOWED_BUILTINS}
        }
        safe_globals.update(globals_dict)
        
        exec(compile(tree, '<model>', 'exec'), safe_globals)
        return safe_globals

class SafetyValidator(ast.NodeVisitor):
    def visit_Import(self, node):
        raise SecurityError("Import statements not allowed")
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ['open', 'exec', 'eval', '__import__']:
                raise SecurityError(f"Unsafe function call: {node.func.id}")
        self.generic_visit(node)
```

---

## 3. Resource Limits

### 3.1 Memory Limit

**Prevent OOM attacks:**

```python
import resource

# Set memory limit to 2GB
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))

runtime.run(model)  # Will raise MemoryError if exceeded
```

### 3.2 Execution Timeout

**Prevent infinite loops:**

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Model execution exceeded time limit")

# Set 60-second timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)

try:
    runtime.run(model)
finally:
    signal.alarm(0)  # Cancel alarm
```

### 3.3 Iteration Limits

**Compiler enforces maximum loop bounds:**

```pel
// This is REJECTED at compile time:
for t in 0..1_000_000_000 {  
  // error[E0700]: Loop bound exceeds maximum (1,000,000)
}
```

**Rationale:** Economic models rarely need >1M timesteps.

---

## 4. Data Input Validation

### 4.1 CSV Injection Prevention

**Malicious CSV can contain formulas:**

```csv
username,email
Alice,alice@example.com
=cmd|'/c calc',bob@example.com  # Excel formula injection
```

**PEL sanitizes:**
```python
def sanitize_csv(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=['object']).columns:
        # Remove leading = + -@ that trigger formula eval
        df[col] = df[col].str.replace(r'^[=+\-@]', '', regex=True)
    return df

data = pd.read_csv("input.csv")
data = sanitize_csv(data)  # Safe to use
```

### 4.2 Type Validation

**Runtime validates data types match declarations:**

```pel
param churnRate: Rate per Month = load("data.csv", "churn_rate")
```

**If `data.csv` contains string instead of number:**
```
error[E0102]: Type mismatch
  Expected: Rate per Month
  Got: String
  Location: data.csv, row 5, column "churn_rate"
```

---

## 5. Package Signing and Verification

### 5.1 Package Format

**PEL packages distributed as signed tarballs:**

```
mypackage-1.0.0.pel.tar.gz      # Package contents
mypackage-1.0.0.pel.tar.gz.sig  # Detached GPG signature
```

### 5.2 Signing Process (Publisher)

```bash
# Create package
pel package create --name mypackage --version 1.0.0

# Sign with GPG key
gpg --detach-sign --armor mypackage-1.0.0.pel.tar.gz

# Publish
pel package publish mypackage-1.0.0.pel.tar.gz
```

### 5.3 Verification Process (Consumer)

```bash
# Download package
pel package install mypackage@1.0.0

# Runtime verifies signature before extraction:
# 1. Fetch publisher's public key from keyserver
# 2. Verify signature: gpg --verify *.sig *.tar.gz
# 3. If valid, extract and install
# 4. If invalid, reject with error
```

### 5.4 Trust Model

**Two-tier trust:**

1. **Core stdlib:** Signed by PEL core team (hardcoded trusted keys)
2. **Community packages:** Signed by authors (user decides to trust)

**Trust-on-first-use (TOFU):**
```bash
pel package install community/pricing-models@2.1.0

# Output:
Warning: Package signed by unknown key: A1B2C3D4
  Fingerprint: 1234 5678 ABCD EF01
  Owner: Alice <alice@example.com>
  
Do you trust this key? [y/N] y

# Key fingerprint stored in ~/.pel/trusted_keys
```

---

## 6. Supply Chain Security

### 6.1 Package Provenance

**Each package includes manifest:**

```json
{
  "name": "pricing-models",
  "version": "2.1.0",
  "authors": ["Alice <alice@example.com>"],
  "license": "AGPL-3.0-or-later",
  "source_url": "https://github.com/alice/pricing-models",
  "commit_hash": "abc123...",
  "build_date": "2026-02-13T10:00:00Z",
  "dependencies": [
    {"name": "pel-std-demand", "version": "0.1.0"}
  ],
  "checksum": "sha256:def456..."
}
```

### 6.2 Dependency Pinning

**Lock file ensures reproducible builds:**

```toml
# pel.lock (auto-generated)
[[package]]
name = "pricing-models"
version = "2.1.0"
checksum = "sha256:abc123..."

[[package]]
name = "pel-std-demand"
version = "0.1.0"
checksum = "sha256:def456..."
```

**Any change in dependency triggers warning:**
```
Warning: pel.lock checksum mismatch for pel-std-demand
  Expected: sha256:def456...
  Got: sha256:999888...
  
Possible supply chain attack detected.
```

---

## 7. Vulnerability Disclosure

### 7.1 Reporting Process

**Security issues reported to:** security@pel-lang.org (GPG: 0x12345678)

**Response timeline:**
- Acknowledgment within 48 hours
- Initial assessment within 1 week
- Fix timeline negotiated with reporter
- Public disclosure after fix released

### 7.2 Security Advisories

**Format:** GitHub Security Advisories (GHSA)

**Example:**
```
GHSA-XXXX-YYYY-ZZZZ: Arbitrary file read via crafted model

Severity: High
CVSS: 7.5
Affected versions: pel-runtime < 0.1.1

Description:
  A malicious PEL model can bypass sandbox restrictions
  and read arbitrary files if capabilities incorrectly configured.

Mitigation:
  Upgrade to pel-runtime 0.1.1 or later.
  
Credit: Bob Security Researcher
```

---

## 8. Secure Defaults

### 8.1 Principle of Least Privilege

**Default configuration denies all capabilities:**

```python
# Secure by default
runtime = PELRuntime("model.pel")  # No file/network access

# Explicit opt-in required
runtime = PELRuntime("model.pel", capabilities={"file_read": ["data.csv"]})
```

### 8.2 No Silent Failures

**Security violations raise exceptions:**

```python
try:
    runtime.run(model)
except SecurityError as e:
    print(f"Security violation: {e}")
    # Example: "File access denied: /etc/passwd"
```

---

## 9. Audit Logging

### 9.1 Security-Relevant Events

**Log to immutable audit trail:**

- Capability grants (file access, network access)
- Package installations
- Model executions (who, when, what)
- Security violations (attempted escapes)

**Example log entry:**
```json
{
  "timestamp": "2026-02-13T14:32:10Z",
  "event": "model_execution",
  "user": "analyst@company.com",
  "model_hash": "sha256:abc123...",
  "capabilities_granted": ["file_read: data/revenue.csv"],
  "status": "success"
}
```

### 9.2 Tamper Detection

**Audit logs signed with append-only structure:**

```python
# Each log entry includes hash of previous entry
log_entry = {
    "prev_hash": "sha256:previous_entry_hash",
    "timestamp": ...,
    "event": ...,
    "signature": sign(hash(entry), private_key)
}
```

**Tampering detected:** If hash chain breaks.

---

## 10. Third-Party Module Isolation

### 10.1 Separate Namespaces

**Modules cannot access each other's internals:**

```pel
import pricing_models
import demand_models

// pricing_models cannot call private functions in demand_models
```

**Implementation:** Each module gets isolated namespace.

### 10.2 Explicit Exports

**Modules declare public API:**

```pel
// In pricing_models.pel
export func calculate_price(...) { ... }

private func internal_helper(...) { ... }  // Not accessible to importers
```

---

## 11. Security Testing

### 11.1 Fuzzing

**Automated input fuzzing to find crashes/escapes:**

```bash
# Fuzz compiler with malformed PEL files
pel fuzz compiler --duration 1h

# Fuzz runtime with random models
pel fuzz runtime --duration 1h
```

### 11.2 Penetration Testing

**Manual security review:**
- Attempt sandbox escapes
- Try supply chain attacks (malicious packages)
- Test resource exhaustion (memory/CPU bombs)

---

## 12. Compliance Considerations

### 12.1 Data Privacy (GDPR, CCPA)

**PEL models may process personal data.**

**Requirements:**
- Models must document data usage (provenance `source`)
- Audit trail enables compliance reports
- Data minimization (only load necessary columns)

### 12.2 Financial Regulations (SOX, MiFID II)

**Models used for financial reporting must be:**
- Auditable (assumption register, run artifacts)
- Reproducible (deterministic seeding)
- Access-controlled (who can run models)

**PEL provides primitives; organizations implement policies.**

---

## Appendix A: Security Checklist

Before production deployment:

- [ ] Sandbox enabled (no unintended file/network access)
- [ ] Resource limits configured (memory, timeout)
- [ ] Package signatures verified
- [ ] Dependencies pinned (pel.lock committed)
- [ ] Audit logging enabled
- [ ] Security updates monitored (subscribe to security advisories)
- [ ] Third-party modules reviewed (code audit if critical)
- [ ] Data input validation enabled
- [ ] Least privilege principle applied (minimal capabilities)
- [ ] Incident response plan documented

---

**Document Maintainers:** PEL Core Team  
**Security Contact:** security@pel-lang.org (GPG: 0x12345678)  
**Feedback:** [github.com/pel-lang/pel/discussions](https://github.com/pel-lang/pel/discussions)
