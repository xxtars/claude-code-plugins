# Pitfalls & Lessons Learned

Reference this file when debugging. Append new entries when you discover a pitfall.

---

<!-- Example entry:

## Torch compile cache corruption
- **Symptom**: All vLLM jobs FAILED with "checksum mismatch"
- **Root cause**: Shared torch compile cache between vLLM versions
- **Fix**: Isolate cache directory per vLLM version, clear corrupted cache
- **Date**: 2026-03-25

-->
