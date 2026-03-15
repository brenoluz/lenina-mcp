# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - Remove Unreliable Contract Listing

### 🗑️ Removed

- **Tool Removed**
  - `list_contracts` - Removed unreliable contract listing tool
  - Lenina v0.1.1 removed the `/anvil/contracts` endpoint
  - Contract tracking via stdout parsing was unreliable for RPC deployments

### ✅ Remaining Contract Features

- `get_contract` - Check if contract exists at address (uses eth_getCode)

### 📝 Documentation

- Updated README.md to reflect removed tool
- Updated endpoint count from 10 to 9

### 🔗 Compatibility

- **Minimum Lenina version required**: v0.1.1
- Compatible with Lenina v0.1.1 and greater

---

## [0.1.0] - Initial Release

### 🚀 Added

- **Health Check**
  - `health_check` - Verify connectivity to Lenina API

- **Anvil Lifecycle Management**
  - `anvil_start` - Start Anvil instance with optional configuration
  - `anvil_stop` - Stop running Anvil instance
  - `anvil_restart` - Restart Anvil with preserved or new configuration

- **Information Tools**
  - `anvil_status` - Get Anvil running status (PID, uptime, port)
  - `get_config` - Get current Anvil configuration

- **Keys and Accounts**
  - `get_private_keys` - Retrieve all private keys and addresses

- **Contract Management**
  - `list_contracts` - List all deployed contracts (deprecated)
  - `get_contract` - Get information about specific contract by address

- **Log Management**
  - `anvil_logs` - Get Anvil console logs from circular buffer

- **RPC Proxy**
  - `rpc_proxy` - Forward JSON-RPC requests to Anvil

- **Documentation**
  - Complete README with installation and usage instructions
  - MCP client configuration examples (Cursor, Cline, Claude Desktop)

### 🔧 Technical

- FastMCP for MCP server framework
- Pydantic for request/response validation
- httpx for async HTTP requests to Lenina API
- Type-safe tool definitions with Field descriptions

### 📦 Configuration

Default connection:
- Lenina API: `http://localhost:8000`

---

## Versioning

This project uses Git tags for versioning. Versions are automatically derived from tags.

### Compatibility Matrix

| lenina-mcp | Minimum Lenina | Maximum Lenina |
|------------|----------------|----------------|
| 0.1.1      | 0.1.1          | latest         |
| 0.1.0      | 0.1.0          | 0.1.0          |

To release a new version:
```bash
git tag -a v0.2.0 -m "Release description"
git push origin v0.2.0
```

[Unreleased]: https://github.com/your-org/lenina-mcp/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/your-org/lenina-mcp/releases/tag/v0.1.1
[0.1.0]: https://github.com/your-org/lenina-mcp/releases/tag/v0.1.0
