# 📝 RXIV-MAKER TODO LIST

**Last Updated**: 2025-08-15  
**Current Branch**: dev  
**Main Branch**: main  

---

## 🚨 URGENT - Before Dev→Main Merge

### **Immediate Blockers** (49 files modified in dev)
- [ ] 🔴 **Fix NotImplementedError bombs** in `bibliography_cache.py` (lines 387, 403, 414)
  - [ ] Implement actual parsing logic (line 387)
  - [ ] Implement actual validation logic (line 403)  
  - [ ] Implement actual analysis logic (line 414)
  - **Impact**: These are placeholder functions that will crash if called

- [ ] 🟠 **Stage and commit modified files**
  - [ ] Review all 49 modified files for final quality check
  - [ ] Stage changes: `git add -A`
  - [ ] Commit with comprehensive message

- [ ] 🟠 **Run full test suite**: `nox -s "test(test_type='full')"`
  - [ ] Ensure coverage stays above 85% threshold
  - [ ] Fix any failing tests before merge

- [ ] 🟡 **Update version** in `pyproject.toml` (current: 1.5.3)

- [ ] 🟢 **Create comprehensive PR** documenting:
  - [ ] Engine architecture refactoring (abstract base classes)
  - [ ] Docker/Podman workflow consolidation (9→3 workflows)
  - [ ] Test coverage improvements (640+ test methods)
  - [ ] Figure generation enhancements with checksum validation
  - [ ] DOI validator improvements
  - [ ] Dependency updates (pytest 8.3.4, GitHub Actions v5)

---

## 🐛 Critical Bugs & Technical Debt

### **High Priority Issues**
- [ ] **Fix 15+ silent exception handlers** - Errors swallowed without logging:
  - [ ] `generate_figures.py:160` - Cache update failure
  - [ ] `cache_management.py:235` - ValueError/TypeError ignored
  - [ ] `engines/factory.py:128` - Engine detection failure
  - [ ] `docker/manager.py:262,570,838,898` - Multiple silent failures
  - [ ] `security/scanner.py:691` - Exception ignored
  - [ ] Add proper logging to all exception handlers

### **Medium Priority Issues**  
- [ ] **Fix 17 skipped tests**:
  - [ ] Fix skipped DOI validator tests (`test_doi_validator.py`)
  - [ ] Enable container engine tests (`test_container_engines.py`)
  - [ ] Fix cross-platform optimization tests
  - [ ] Enable system package manager tests

- [ ] **Remove deprecated functions**:
  - [ ] Remove `rxiv install-deps` command redirect
  - [ ] Remove `rxiv bibliography validate` redirect
  - [ ] Clean up deprecation warnings in engine modules

### **Code Quality**
- [ ] Remove XXSUBNOTEPROTECTEDXX placeholder system
- [ ] Clean up LaTeX multi-pass comments
- [ ] Standardize error handling patterns
- [ ] Remove hardcoded DEBUG references

---

## 🧪 Test Coverage & Quality (Current: ~85%)

### **Priority Coverage Targets**
- [ ] Improve module coverage to 90%:
  - [ ] `build_manager.py` (27% → 90%)
  - [ ] `platform.py` (24% → 90%)  
  - [ ] `file_helpers.py` (20% → 90%)
  - [ ] DOI validators (8-15% → 90%)

### **Testing Infrastructure**
- [ ] Convert `test-binary.sh` to Python-based pytest module
- [ ] Add integration tests for container engine support
- [ ] Implement smoke tests for quick validation
- [ ] Fix `container-engines.yml` workflow (currently reduced)

### **Recommended Approach**
- [ ] Use `tests/unit/test_setup_environment.py` pattern as template:
  - [ ] Comprehensive method coverage
  - [ ] Mock-based isolation
  - [ ] Error handling completeness
  - [ ] Cross-platform validation
  - [ ] Integration workflow testing

---

## 🚧 Active Development

### **Container & Docker Improvements**
- [ ] Add Podman-specific optimizations to build process
- [ ] Document Podman usage in user guides
- [ ] Add container engine auto-detection for seamless switching
- [ ] Remove deprecated workflows after 30 days (check: 2025-02-14)

### **Documentation Updates**
- [ ] Update README.md - Consolidate quickstart sections
- [ ] Create Podman guide for Docker alternative
- [ ] Update installation docs for unified setup command
- [ ] Add troubleshooting guide for common issues
- [ ] Document new test structure and architecture
- [ ] Create plugin development guide

---

## 📋 Backlog - Future Enhancements

### **Release & Distribution**
- [ ] Test automated Homebrew PR creation on next release
- [ ] Create APT repository with Debian packaging:
  - Create `debian/` directory with packaging files
  - Implement `.deb` package build process
  - Set up GPG signing for repository
  - Create `publish-apt.yml` workflow
  - Host repository on `apt-repo` branch

### **Advanced Features**

#### **Inline Code Execution**
- [ ] Design markdown syntax for code blocks
- [ ] Create code execution engine
- [ ] Implement Python code runner
- [ ] Implement R code runner
- [ ] Add security sandboxing
- [ ] Create example manuscripts with dynamic content

#### **Google Colab Integration**  
- [ ] Create Podman-based Colab notebook
- [ ] Add Playwright automation for testing
- [ ] Document Colab-specific setup
- [ ] Test with real manuscripts

### **Cache System Improvements** (Low Priority)
- [ ] Remove legacy `.rxiv_cache` references after Nov 2025
- [ ] Add cache statistics reporting (hit rates, size metrics)
- [ ] Implement cache pruning strategy
- [ ] Add cache integrity checks

### **Performance Optimizations**
- [ ] Profile slow test cases and optimize
- [ ] Implement caching for repeated operations
- [ ] Optimize Docker build times
- [ ] Add parallel processing for figure generation

### **Enhanced CLI Output**
- [ ] Implement consistent `rich` logging across all modules
- [ ] Add progress bars for long-running operations
- [ ] Improve error message clarity

---

## 📊 Project Status

### **Git Status**
- **Current Branch**: dev (49 files modified)
- **Untracked Files**: 
  - [ ] Stage `tests/unit/test_add_bibliography.py`
  - [ ] Stage `tests/unit/test_fix_bibliography.py`
  - [ ] Stage `tests/unit/test_validate_manuscript.py`

### **Code Metrics**
- **Overall Coverage**: ~85% (enforced minimum)
- **Total Test Methods**: 640+
- **Test Execution**: <10 minutes full suite
- **Lines Changed**: +2,061 / -2,383 (net -322)

### **Key Commands**
```bash
# Testing
nox -s "test(test_type='fast')"   # Quick validation
nox -s "test(test_type='full')"   # Complete suite
nox -s coverage                    # Check coverage
nox -s security                    # Security scan
nox -s docs                        # Generate docs

# Development
rxiv setup                         # Setup environment
rxiv validate EXAMPLE_MANUSCRIPT   # Validate manuscript
rxiv pdf EXAMPLE_MANUSCRIPT        # Generate PDF
```

---

## ✅ Recent Achievements Summary

### **2025-08-14: Major Milestones**
- [x] **Cache Migration**: Platform-standard cache locations with automatic migration
- [x] **Test Coverage Push**: Engine module coverage 0%→95%, 126 new test methods
- [x] **CI/CD Hardening**: 85% coverage enforcement, UV migration, security automation
- [x] **Workflow Consolidation**: 9 workflows → 3 unified workflows
- [x] **Documentation System**: Comprehensive API docs with CI validation

### **Key Infrastructure Wins**
- [x] Container engine abstraction (Docker + Podman)
- [x] Security testing framework (643+ tests)
- [x] Homebrew release automation
- [x] Cross-platform test coverage