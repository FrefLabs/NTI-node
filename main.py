"""
NTI Node - Script Execution Node
Connects to Gateway via WebSocket and executes scripts
"""

import asyncio
import websockets
import json
import logging
import yaml
import socket
import time
from pathlib import Path
import sys
import subprocess

from node.executor import ScriptExecutor
from node.connection import NodeConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_python_installation():
    """Verify Python is installed and functional"""
    try:
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            logger.info(f"Python check passed: {version}")
            return True
        else:
            logger.error("Python3 is not functional")
            return False
    except FileNotFoundError:
        logger.error("Python3 is not installed or not in PATH")
        return False
    except Exception as e:
        logger.error(f"Error checking Python installation: {str(e)}")
        return False


def generate_node_id():
    """Generate unique node ID: hostname_timestamp_ms"""
    hostname = socket.gethostname()
    timestamp_ms = int(time.time() * 1000)
    return f"{hostname}_{timestamp_ms}"


async def main():
    """Main entry point"""
    logger.info("Starting NTI Node...")
    
    # Check Python installation
    if not check_python_installation():
        logger.error("Python installation check failed. Please install Python 3.9+ and ensure it's in PATH")
        sys.exit(1)
    
    # Load configuration
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
    else:
        logger.error("config.yaml not found. Please create configuration file.")
        sys.exit(1)
    
    # Generate node ID
    node_id = generate_node_id()
    hostname = config["node"].get("hostname") or socket.gethostname()
    
    logger.info(f"Node ID: {node_id}")
    logger.info(f"Hostname: {hostname}")
    
    # Initialize components
    executor = ScriptExecutor(config)
    connection = NodeConnection(config, node_id, hostname, executor)
    
    # Connect to gateway
    await connection.connect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Node stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
