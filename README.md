# Lenina MCP Server

MCP (Model Context Protocol) Server for Lenina - Anvil Management. This server exposes all Lenina API endpoints as MCP tools, enabling AI coding assistants (Cursor, Cline, etc.) to control Anvil instances.

## Features

- **Full Lenina API Coverage**: All 10 Lenina API endpoints exposed as MCP tools
- **Type-Safe**: All tools use Pydantic models for parameter validation
- **Async**: Built with async/await for optimal performance
- **No Authentication**: Designed for local development only (matching Lenina)

## Installation

```bash
pip install -r requirements.txt
```

Or using uv:

```bash
uv pip install -r requirements.txt
```

## Configuration

The server connects to Lenina API at a configurable base URL:

- **Default**: `http://localhost:8000`
- **Environment Variable**: Set `LENINA_BASE_URL` to change (not yet implemented, hardcoded in `mcp_server.py`)

To change the URL, edit the `LENINA_BASE_URL` constant in `mcp_server.py`.

## Running the Server

```bash
python mcp_server.py
```

Or using the installed command:

```bash
lenina-mcp
```

## Available Tools

### Health Check
- **`health_check`**: Verify connectivity to Lenina API

### Anvil Lifecycle
- **`anvil_start`**: Start an Anvil instance with configuration
  - `port` (default: 8545): Port to run Anvil on
  - `chainId` (default: 31337): Chain ID
  - `blockTime` (default: 0): Block time in seconds (0 = manual mining)
  - `gasLimit` (default: 30000000): Gas limit per block
  - `mnemonic` (optional): Mnemonic for deterministic accounts

- **`anvil_stop`**: Stop the running Anvil instance

- **`anvil_restart`**: Restart Anvil with optional new configuration
  - Same parameters as `anvil_start`

### Status and Configuration
- **`anvil_status`**: Get current Anvil status (running state, PID, uptime, port)

- **`get_config`**: Get the current Anvil configuration

### Keys and Accounts
- **`get_private_keys`**: Get all private keys and account information
  - Returns list of accounts with addresses and private keys
  - Includes mnemonic if configured

### Contract Management
- **`list_contracts`**: List all deployed contracts
  - Returns addresses, bytecode, bytecode hashes, and deployment blocks

- **`get_contract`**: Get information about a specific contract
  - `address`: The contract address (0x-prefixed)

### RPC Proxy
- **`rpc_proxy`**: Send JSON-RPC requests to Anvil
  - `method`: RPC method name (e.g., `eth_blockNumber`, `eth_getBalance`)
  - `params`: Method parameters (list)
  - `request_id`: JSON-RPC request ID (default: 1)
  - Supports all standard Ethereum JSON-RPC methods

## MCP Client Configuration

### Cursor

Add to your `.cursor/mcp.json`:

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

### Cline

Add to your Cline MCP settings:

```json
{
  "mcpServers": [
    {
      "name": "lenina",
      "command": "python",
      "args": ["/path/to/lenina-mcp/mcp_server.py"],
      "cwd": "/path/to/lenina-mcp"
    }
  ]
}
```

### Claude Desktop

Add to your Claude Desktop config:

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

## Example Usage

Once connected, you can use natural language commands like:

- "Start Anvil on port 8545 with chain ID 31337"
- "Check if Anvil is running"
- "Get the private keys for the first 3 accounts"
- "List all deployed contracts"
- "What's the current block number?" (uses rpc_proxy)
- "Stop the Anvil instance"

## Development

### Type Checking

```bash
mypy --strict mcp_server.py
```

### Running Tests

(No tests implemented yet)

## Requirements

- Python 3.10+
- Lenina API running at `http://localhost:8000` (or configured URL)

## Dependencies

- `mcp>=1.0.0`: MCP protocol implementation
- `fastmcp>=0.1.0`: FastMCP server framework
- `httpx>=0.27.0`: Async HTTP client
- `pydantic>=2.0.0`: Data validation
- `pydantic-settings>=2.0.0`: Settings management

## License

MIT
