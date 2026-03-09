---
name: lenina
description: "Manage Anvil blockchain servers remotely using Lenina MCP. Use for starting, stopping, and monitoring Anvil instances, managing accounts, and interacting with smart contracts."
user-invocable: true
---

# Lenina - Anvil Management

Remote management of Anvil blockchain development servers through the Lenina MCP server.

## Architecture

```
AI Assistant ←MCP→ lenina-mcp ←REST→ Lenina API ←→ Anvil Server
```

- **Anvil**: Blockchain development server (by Foundry)
- **Lenina**: RESTful API server that manages Anvil instances
- **lenina-mcp**: MCP server that wraps the Lenina REST API for AI assistants

---

## What is Lenina

**Lenina** is a RESTful API server that manages Anvil instances.

**lenina-mcp** is an MCP server that wraps the Lenina REST API, enabling AI assistants to control Anvil through natural language:

- Start/stop/restart Anvil blockchain servers
- Manage accounts and private keys
- Deploy and inspect smart contracts
- Send JSON-RPC requests to the blockchain

The MCP server communicates with Lenina via HTTP REST calls, which then controls the Anvil process.

---

## Setup

### 1. Ensure Lenina API is Running

The Lenina API server must be running before using this skill. Typically at:
- `http://localhost:8000` or
- `http://192.168.1.12:8000` (network accessible)

### 2. Configure MCP Client

Add the Lenina MCP server to your MCP client configuration:

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "lenina": {
      "command": "python",
      "args": ["/path/to/lenina-mcp/mcp_server.py"],
      "cwd": "/path/to/lenina-mcp"
    }
  }
}
```

**Claude Desktop** (`config.json`):
```json
{
  "mcpServers": {
    "lenina": {
      "command": "python",
      "args": ["/path/to/lenina-mcp/mcp_server.py"],
      "cwd": "/path/to/lenina-mcp"
    }
  }
}
```

---

## Usage

### Check Server Configuration

**Always start by checking the server configuration** to know which Lenina REST API instance you're connected to:

```
get_server_config
```

This returns:
- `LENINA_BASE_URL`: The base URL of the Lenina REST API server
- Description and usage information

The MCP server uses this URL to make REST calls to Lenina, which then manages Anvil.

### Get Anvil Connection Details

**Critical:** Before connecting tools like MetaMask, Hardhat, or Foundry to Anvil, you must get the correct IP and port:

```
get_config
```

This returns the Anvil configuration including:
- `host`: The IP address Anvil is listening on (e.g., `192.168.1.12`)
- `port`: The port Anvil is running on (e.g., `8545`)

**Use this information to configure your tools:**
- RPC URL: `http://{host}:{port}` (e.g., `http://192.168.1.12:8545`)
- Chain ID: As returned by get_config (typically `31337`)

### Start Anvil

```
anvil_start
  port: 8545
  chainId: 31337
  blockTime: 0 (0 = manual mining, set >0 for auto-mining)
  gasLimit: 30000000
  mnemonic: optional custom mnemonic
```

### Check Status

```
anvil_status
```

Returns:
- `running`: boolean
- `pid`: process ID
- `uptime`: seconds running
- `port`: port Anvil is listening on

### Get Accounts and Private Keys

```
get_private_keys
```

Returns all accounts with addresses and private keys for testing.

### Deploy and List Contracts

```
list_contracts
```

Returns all deployed contracts with addresses and bytecode.

### Send RPC Requests

```
rpc_proxy
  method: "eth_blockNumber"
  params: []
```

Common RPC methods:
- `eth_blockNumber` - Get current block
- `eth_getBalance` - Get account balance
- `eth_sendTransaction` - Send transaction
- `eth_call` - Call contract method

### Get Logs

```
anvil_logs
  lines: 100
  format: "json" (or "markdown", "text")
```

---

## Common Workflows

### 1. Start Development Environment

```
1. get_server_config (verify connection)
2. anvil_start (start Anvil)
3. get_config (get RPC URL for tools)
4. get_private_keys (get test accounts)
```

### 2. Connect Hardhat/Foundry

After starting Anvil:
1. Run `get_config` to get host and port
2. Set RPC URL in Hardhat config: `http://{host}:{port}`
3. Set Chain ID to match Anvil's chainId

### 3. Debug Smart Contracts

```
1. list_contracts (find contract address)
2. get_contract address: "0x..." (get bytecode)
3. rpc_proxy method: "eth_call" params: [...] (call methods)
4. anvil_logs (check Anvil console output)
```

### 4. Reset Environment

```
1. anvil_stop
2. anvil_start (fresh state)
```

---

## Important Notes

### Why Check `get_config`

The `get_config` function is **essential** because:

1. **Dynamic Host/Port**: Anvil may be configured to listen on different IPs (localhost vs network IP)
2. **Remote Access**: If Lenina runs on another machine, you need the actual IP to connect tools
3. **Port Conflicts**: Default port 8545 may change if in use
4. **Chain ID Matching**: Your development tools must use the same chainId as Anvil

**Architecture reminder:**
- `get_config` queries the Lenina REST API
- Lenina returns the Anvil configuration it's managing
- Use this info to connect your tools directly to Anvil's RPC endpoint

### Network Configuration

**Architecture:**
```
Your Tools → Anvil RPC (http://host:port)
lenina-mcp → Lenina REST API → Anvil Management
```

If Anvil is running on a remote machine:
- The `host` from `get_config` tells you the IP to connect to
- Configure firewall to allow traffic on the Anvil port
- Use `http://{host}:{port}` as RPC URL in all tools
- The Lenina REST API must be accessible to lenina-mcp

### Security

- **Local Development Only**: Lenina has no authentication
- **Private Keys Exposed**: `get_private_keys` returns all account private keys
- **Never Use in Production**: Anvil is a test blockchain with deterministic keys

---

## Available Tools Summary

| Tool | Purpose |
|------|---------|
| `get_server_config` | Get Lenina MCP server configuration |
| `health_check` | Verify Lenina API connectivity |
| `anvil_start` | Start Anvil instance |
| `anvil_stop` | Stop Anvil instance |
| `anvil_restart` | Restart Anvil with new config |
| `anvil_status` | Get running status |
| `get_config` | Get Anvil configuration (host, port, chainId) |
| `get_private_keys` | Get accounts and private keys |
| `list_contracts` | List deployed contracts |
| `get_contract` | Get specific contract details |
| `rpc_proxy` | Send JSON-RPC requests |
| `anvil_logs` | Get Anvil console logs |
