"""
MCP Server for Lenina - Anvil Management

This server exposes all Lenina API endpoints as MCP tools,
enabling AI coding assistants to control Anvil instances.
"""

import asyncio
import logging
from typing import Any, Optional

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("lenina-mcp")

# Initialize FastMCP server
mcp = FastMCP("lenina-mcp")

# Configuration
LENINA_BASE_URL = "http://192.168.1.12:8000"


# ============================================================================
# Pydantic Models - Matching Lenina API Schemas
# ============================================================================


class AnvilConfig(BaseModel):
    """Configuration for Anvil instance."""

    port: int = Field(default=8545, description="Port to run Anvil on")
    chainId: int = Field(default=31337, description="Chain ID")
    blockTime: int = Field(
        default=0, description="Block time in seconds (0 for manual)"
    )
    gasLimit: int = Field(default=30000000, description="Gas limit per block")
    mnemonic: Optional[str] = Field(
        default=None, description="Mnemonic for deterministic accounts"
    )


class AnvilStatusResponse(BaseModel):
    """Response from /anvil/status endpoint."""

    running: bool = Field(description="Whether Anvil is currently running")
    pid: Optional[int] = Field(default=None, description="Process ID if running")
    uptime: Optional[int] = Field(
        default=None, description="Uptime in seconds if running"
    )
    port: Optional[int] = Field(default=None, description="Port Anvil is running on")


class HealthResponse(BaseModel):
    """Response from /health endpoint."""

    status: str = Field(description="Health status (healthy/unhealthy)")
    timestamp: int = Field(description="Unix timestamp of health check")


class AccountInfo(BaseModel):
    """Account information with address and private key."""

    address: str = Field(description="Ethereum address")
    privateKey: str = Field(description="Private key (0x-prefixed)")


class KeysResponse(BaseModel):
    """Response from /anvil/keys endpoint."""

    accounts: list[AccountInfo] = Field(description="List of accounts")
    mnemonic: Optional[str] = Field(default=None, description="Mnemonic if configured")


class ContractInfo(BaseModel):
    """Contract information."""

    address: str = Field(description="Contract address")
    bytecode: str = Field(description="Deployed bytecode")
    bytecodeHash: str = Field(description="Hash of bytecode")
    deploymentBlock: int = Field(description="Block number where contract was deployed")


class ContractsResponse(BaseModel):
    """Response from /anvil/contracts endpoint."""

    contracts: list[ContractInfo] = Field(description="List of deployed contracts")


class RpcRequest(BaseModel):
    """JSON-RPC request."""

    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    method: str = Field(description="RPC method name")
    params: list[Any] = Field(default_factory=list, description="RPC method parameters")
    id: int = Field(default=1, description="Request ID")


class RpcResponse(BaseModel):
    """JSON-RPC response."""

    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: int = Field(description="Request ID")
    result: Optional[Any] = Field(default=None, description="RPC result if successful")
    error: Optional[dict[str, Any]] = Field(
        default=None, description="Error object if failed"
    )


class LogEntry(BaseModel):
    """Single log entry"""

    line: str = Field(description="Log line content")
    timestamp: float = Field(description="Unix timestamp when log was captured")
    sequence: int = Field(description="Sequence number for ordering")


class AnvilLogsResponse(BaseModel):
    """Response from getting Anvil logs"""

    lines: list[LogEntry] = Field(description="List of log entries")
    totalLines: int = Field(description="Total number of lines in buffer")
    truncated: bool = Field(description="Whether results were truncated")
    format: str = Field(description="Output format (markdown/json/text)")


# ============================================================================
# HTTP Client Helper
# ============================================================================


async def get_http_client() -> httpx.AsyncClient:
    """Get an async HTTP client for Lenina API calls."""
    return httpx.AsyncClient(base_url=LENINA_BASE_URL, timeout=30.0)


# ============================================================================
# MCP Tools - Server Configuration
# ============================================================================


@mcp.tool(
    description="Get the MCP server configuration including LENINA_BASE_URL. Useful for understanding which Lenina API endpoint this MCP server connects to."
)
async def get_server_config() -> dict[str, Any]:
    """
    Get the MCP server configuration.

    Returns:
        dict: Server configuration including LENINA_BASE_URL
    """
    logger.info("Getting server configuration")
    return {
        "LENINA_BASE_URL": LENINA_BASE_URL,
        "description": "This is the base URL of the Lenina API server that this MCP server connects to. All Anvil management requests are sent to this endpoint.",
        "usage": "Use this URL to understand which Lenina instance you're controlling. All MCP tools here proxy requests to this base URL.",
    }


# ============================================================================
# MCP Tools - Health Check
# ============================================================================


@mcp.tool(
    description="Check health and connectivity to Lenina API. Returns the current timestamp if healthy."
)
async def health_check() -> dict[str, Any]:
    """
    Verify connectivity to the Lenina API server.

    Returns:
        dict: Health status with timestamp
    """
    logger.info("Performing health check")
    async with await get_http_client() as client:
        try:
            response = await client.get("/health")
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Health check successful: {data}")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            return {"status": "unhealthy", "error": "Cannot connect to Lenina API"}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return {"status": "unhealthy", "error": str(e)}


# ============================================================================
# MCP Tools - Anvil Lifecycle Management
# ============================================================================


@mcp.tool(description="Start an Anvil instance with optional configuration parameters.")
async def anvil_start(
    port: int = Field(default=8545, description="Port to run Anvil on"),
    chainId: int = Field(default=31337, description="Chain ID"),
    blockTime: int = Field(
        default=0, description="Block time in seconds (0 for manual mining)"
    ),
    gasLimit: int = Field(default=30000000, description="Gas limit per block"),
    mnemonic: Optional[str] = Field(
        default=None, description="Mnemonic for deterministic accounts"
    ),
) -> dict[str, Any]:
    """
    Start an Anvil blockchain instance.

    Args:
        port: Port number for the RPC endpoint
        chainId: Chain ID for the network
        blockTime: Block time in seconds (0 = manual mining)
        gasLimit: Maximum gas per block
        mnemonic: Optional mnemonic for deterministic account generation

    Returns:
        dict: Start response from Lenina API
    """
    logger.info(f"Starting Anvil on port {port}")
    config = AnvilConfig(
        port=port,
        chainId=chainId,
        blockTime=blockTime,
        gasLimit=gasLimit,
        mnemonic=mnemonic,
    )
    async with await get_http_client() as client:
        try:
            response = await client.post("/anvil/start", json=config.model_dump())
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Anvil started: {data}")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"Failed to start Anvil: {e.response.text}")


@mcp.tool(description="Stop the running Anvil instance.")
async def anvil_stop() -> dict[str, Any]:
    """
    Stop the currently running Anvil instance.

    Returns:
        dict: Stop response from Lenina API
    """
    logger.info("Stopping Anvil")
    async with await get_http_client() as client:
        try:
            response = await client.post("/anvil/stop")
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Anvil stopped: {data}")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"Failed to stop Anvil: {e.response.text}")


@mcp.tool(description="Restart an Anvil instance with optional new configuration.")
async def anvil_restart(
    port: int = Field(default=8545, description="Port to run Anvil on"),
    chainId: int = Field(default=31337, description="Chain ID"),
    blockTime: int = Field(default=0, description="Block time in seconds"),
    gasLimit: int = Field(default=30000000, description="Gas limit per block"),
    mnemonic: Optional[str] = Field(default=None, description="Mnemonic for accounts"),
) -> dict[str, Any]:
    """
    Restart an Anvil instance with optional new configuration.

    Args:
        port: Port number for the RPC endpoint
        chainId: Chain ID for the network
        blockTime: Block time in seconds
        gasLimit: Maximum gas per block
        mnemonic: Optional mnemonic for account generation

    Returns:
        dict: Restart response from Lenina API
    """
    logger.info(f"Restarting Anvil on port {port}")
    config = AnvilConfig(
        port=port,
        chainId=chainId,
        blockTime=blockTime,
        gasLimit=gasLimit,
        mnemonic=mnemonic,
    )
    async with await get_http_client() as client:
        try:
            response = await client.post("/anvil/restart", json=config.model_dump())
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Anvil restarted: {data}")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"Failed to restart Anvil: {e.response.text}")


# ============================================================================
# MCP Tools - Status and Configuration
# ============================================================================


@mcp.tool(description="Get the current status of the Anvil instance.")
async def anvil_status() -> dict[str, Any]:
    """
    Get the current status of Anvil.

    Returns:
        dict: Status including running state, PID, uptime, and port
    """
    logger.info("Getting Anvil status")
    async with await get_http_client() as client:
        try:
            response = await client.get("/anvil/status")
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Anvil status: {data}")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"Failed to get status: {e.response.text}")


@mcp.tool(description="Get the current Anvil configuration.")
async def get_config() -> dict[str, Any]:
    """
    Get the current Anvil configuration.

    Returns:
        dict: Full Anvil configuration
    """
    logger.info("Getting Anvil configuration")
    async with await get_http_client() as client:
        try:
            response = await client.get("/anvil/config")
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Anvil config: {data}")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"Failed to get config: {e.response.text}")


# ============================================================================
# MCP Tools - Keys and Accounts
# ============================================================================


@mcp.tool(description="Get all private keys and accounts from the Anvil instance.")
async def get_private_keys() -> dict[str, Any]:
    """
    Get all private keys and account information.

    Returns:
        dict: List of accounts with addresses and private keys, plus mnemonic if configured
    """
    logger.info("Getting private keys")
    async with await get_http_client() as client:
        try:
            response = await client.get("/anvil/keys")
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Retrieved {len(data.get('accounts', []))} accounts")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"Failed to get keys: {e.response.text}")


# ============================================================================
# MCP Tools - Contract Management
# ============================================================================


@mcp.tool(description="Get Anvil console logs from the circular buffer.")
async def anvil_logs(
    lines: int = Field(
        default=100, ge=1, le=1000, description="Number of recent log lines to retrieve"
    ),
    since: Optional[int] = Field(
        default=None, description="Get logs after this sequence number"
    ),
    format: str = Field(
        default="json", description="Output format: json, markdown, or text"
    ),
) -> dict[str, Any]:
    """
    Get Anvil console logs from the circular buffer.

    Args:
        lines: Number of recent lines to retrieve (1-1000, default: 100)
        since: Optional sequence number to get logs after this point
        format: Output format - json (default), markdown, or text

    Returns:
        dict: Log entries with line content, timestamps, and sequence numbers
    """
    logger.info(f"Getting Anvil logs (lines={lines}, since={since}, format={format})")
    async with await get_http_client() as client:
        try:
            params = {"lines": lines, "format": format}
            if since is not None:
                params["since"] = since
            response = await client.get("/anvil/logs", params=params)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Retrieved {len(data.get('lines', []))} log lines")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"Failed to get logs: {e.response.text}")


@mcp.tool(description="List all deployed contracts tracked by Anvil.")
async def list_contracts() -> dict[str, Any]:
    """
    List all deployed contracts.

    Returns:
        dict: List of contracts with addresses, bytecode, and deployment info
    """
    logger.info("Listing contracts")
    async with await get_http_client() as client:
        try:
            response = await client.get("/anvil/contracts")
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Found {len(data.get('contracts', []))} contracts")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"Failed to list contracts: {e.response.text}")


@mcp.tool(description="Get information about a specific contract by address.")
async def get_contract(
    address: str = Field(description="The contract address (0x-prefixed)"),
) -> dict[str, Any]:
    """
    Get information about a specific contract.

    Args:
        address: The Ethereum address of the contract (0x-prefixed)

    Returns:
        dict: Contract information including bytecode and deployment block
    """
    logger.info(f"Getting contract at {address}")
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/anvil/contract/{address}")
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"Contract found: {data}")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            if e.response.status_code == 404:
                raise RuntimeError(f"No contract found at address {address}")
            raise RuntimeError(f"Failed to get contract: {e.response.text}")


# ============================================================================
# MCP Tools - RPC Proxy
# ============================================================================


@mcp.tool(description="Send a JSON-RPC request to Anvil.")
async def rpc_proxy(
    method: str = Field(description="The RPC method name (e.g., eth_blockNumber)"),
    params: list[Any] = Field(default_factory=list, description="Method parameters"),
    request_id: int = Field(default=1, description="JSON-RPC request ID"),
) -> dict[str, Any]:
    """
    Send a JSON-RPC request to Anvil.

    Args:
        method: The RPC method to call (e.g., eth_blockNumber, eth_getBalance)
        params: Parameters for the RPC method
        request_id: JSON-RPC request ID

    Returns:
        dict: JSON-RPC response with result or error
    """
    logger.info(f"RPC call: {method} with {len(params)} params")
    rpc_request = RpcRequest(
        method=method,
        params=params,
        id=request_id,
    )
    async with await get_http_client() as client:
        try:
            response = await client.post("/anvil/rpc", json=rpc_request.model_dump())
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            logger.info(f"RPC response: {data}")
            return data
        except httpx.ConnectError as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Cannot connect to Lenina API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise RuntimeError(f"RPC call failed: {e.response.text}")


# ============================================================================
# Main Entry Point
# ============================================================================


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting Lenina MCP Server")
    mcp.run()


if __name__ == "__main__":
    main()
