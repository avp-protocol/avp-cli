<p align="center">
  <img src="https://raw.githubusercontent.com/avp-protocol/spec/main/assets/avp-shield.svg" alt="AVP Shield" width="80" />
</p>

<h1 align="center">avp-cli</h1>

<p align="center">
  <strong>Command-line interface for Agent Vault Protocol</strong><br>
  Store · Retrieve · Migrate · All platforms
</p>

<p align="center">
  <a href="https://github.com/avp-protocol/avp-cli/releases"><img src="https://img.shields.io/github/v/release/avp-protocol/avp-cli?style=flat-square&color=00D4AA" alt="Release" /></a>
  <a href="https://github.com/avp-protocol/avp-cli/actions"><img src="https://img.shields.io/github/actions/workflow/status/avp-protocol/avp-cli/ci.yml?style=flat-square" alt="CI" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-blue?style=flat-square" alt="License" /></a>
</p>

---

## Overview

`avp` is the official command-line tool for the [Agent Vault Protocol](https://github.com/avp-protocol/spec). It lets you store, retrieve, and migrate secrets across backends — from encrypted files to hardware secure elements.

## Installation

### macOS

```bash
brew install avp-protocol/tap/avp
```

### Linux

```bash
curl -fsSL https://avp.dev/install.sh | sh
```

### Windows

```powershell
winget install avp-protocol.avp
```

### From Source

```bash
cargo install avp-cli
```

## Quick Start

### Store a secret

```bash
avp store anthropic_api_key "sk-ant-..." --backend file
```

### Retrieve a secret

```bash
avp get anthropic_api_key
# sk-ant-...
```

### List secrets

```bash
avp list
# anthropic_api_key    file     2026-02-18
# openai_api_key       keychain 2026-02-15
```

### Delete a secret

```bash
avp delete anthropic_api_key
```

## Migration

Upgrade your security without changing agent code:

```bash
# Step 1: Migrate from file to OS keychain (free, blocks 90% of attacks)
avp migrate --from file --to keychain

# Step 2: Migrate from keychain to hardware (FIPS 140-3 Level 3)
avp migrate --from keychain --to hardware
```

Each migration is **verifiable** — the CLI compares source and destination before deleting the source.

## Backend Configuration

### File Backend

```bash
avp config set backend file
avp config set file.path ~/.avp/secrets.enc
avp config set file.cipher chacha20-poly1305
```

### Keychain Backend

```bash
avp config set backend keychain
# Uses macOS Keychain, Windows Credential Manager, or libsecret on Linux
```

### Hardware Backend

```bash
avp config set backend hardware
avp config set hardware.device /dev/ttyUSB0
# or auto-detect
avp config set hardware.device auto
```

### Remote Backend

```bash
avp config set backend remote
avp config set remote.url https://vault.company.com
avp login  # Opens browser for auth
```

## Commands

| Command | Description |
|---------|-------------|
| `avp store <name> <value>` | Store a secret |
| `avp get <name>` | Retrieve a secret |
| `avp delete <name>` | Delete a secret |
| `avp list` | List all secrets |
| `avp rotate <name>` | Rotate a secret |
| `avp migrate` | Migrate between backends |
| `avp config` | View/set configuration |
| `avp discover` | Show vault capabilities |
| `avp login` | Authenticate to remote vault |
| `avp logout` | End session |

## Environment Variables

```bash
AVP_CONFIG      # Config file path (default: ~/.avp/config.toml)
AVP_BACKEND     # Backend type: file, keychain, hardware, remote
AVP_WORKSPACE   # Workspace name (default: "default")
AVP_DEBUG       # Enable debug logging
```

## Shell Integration

### Bash/Zsh

```bash
# Add to ~/.bashrc or ~/.zshrc
eval "$(avp completion bash)"
```

### Fish

```fish
avp completion fish | source
```

### PowerShell

```powershell
avp completion powershell | Out-String | Invoke-Expression
```

## Security

- Secrets are never logged or written to shell history
- Values can be piped: `avp get key | xargs -I {} curl -H "Authorization: {}"`
- Interactive PIN entry for hardware backends
- Session tokens stored in OS keychain

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

<p align="center">
  <a href="https://github.com/avp-protocol/spec">Specification</a> ·
  <a href="https://github.com/avp-protocol/avp-cli/issues">Issues</a>
</p>
