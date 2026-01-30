---
name: execution-standards
description: Enforces cross-platform portability and safe execution conventions for all scripts and shell commands. Always apply when running scripts or shell commands.
---

# Execution Standards

## Portability

All skills and scripts MUST be portable across Windows, macOS, and Linux. Avoid OS-specific commands or paths. Use Python for scripts instead of platform-specific shell scripts.

## Python

ALWAYS run Python scripts with the `python` CLI (not `python3`).

## Shell Safety

When executing shell commands, ALWAYS quote arguments that may contain special characters (e.g., URLs with `?`, `&`, whitespace) to prevent shell parsing errors.
