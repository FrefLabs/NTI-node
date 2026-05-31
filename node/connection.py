"""
Node Connection - Manages WebSocket connection to Gateway
"""

import asyncio
import websockets
import json
import logging

logger = logging.getLogger(__name__)


class NodeConnection:
    def __init__(self, config, node_id, hostname, executor):
        self.config = config
        self.node_id = node_id
        self.hostname = hostname
        self.executor = executor
        self.gateway_url = config["gateway"]["url"]
        self.reconnect_interval = config["gateway"]["reconnect_interval"]
        self.max_reconnect_attempts = config["gateway"]["max_reconnect_attempts"]
        self.active_tasks = 0
        
    async def connect(self):
        """Connect to Gateway with automatic reconnection"""
        attempt = 0
        
        while True:
            try:
                attempt += 1
                logger.info(f"Connecting to Gateway at {self.gateway_url} (attempt {attempt})...")
                
                async with websockets.connect(self.gateway_url) as websocket:
                    logger.info("Connected to Gateway")
                    
                    # Send registration message
                    await self.register(websocket)
                    
                    # Reset attempt counter on successful connection
                    attempt = 0
                    
                    # Handle messages
                    await self.message_loop(websocket)
                    
            except websockets.exceptions.WebSocketException as e:
                logger.error(f"WebSocket error: {str(e)}")
            except Exception as e:
                logger.error(f"Connection error: {str(e)}")
            
            # Check if we should stop reconnecting
            if self.max_reconnect_attempts > 0 and attempt >= self.max_reconnect_attempts:
                logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached. Stopping.")
                break
            
            # Wait before reconnecting
            logger.info(f"Reconnecting in {self.reconnect_interval} seconds...")
            await asyncio.sleep(self.reconnect_interval)
    
    async def register(self, websocket):
        """Send registration message to Gateway"""
        message = {
            "type": "register",
            "node_id": self.node_id,
            "hostname": self.hostname,
            "capabilities": ["python3"]
        }
        await websocket.send(json.dumps(message))
        logger.info(f"Registered as {self.node_id}")
    
    async def message_loop(self, websocket):
        """Handle incoming messages from Gateway"""
        async for message in websocket:
            try:
                data = json.loads(message)
                await self.handle_message(websocket, data)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {str(e)}")
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
    
    async def handle_message(self, websocket, data: dict):
        """Handle a message from Gateway"""
        msg_type = data.get("type")
        
        if msg_type == "ping":
            # Respond to heartbeat
            await self.send_pong(websocket)
            
        elif msg_type == "execute":
            # Execute task
            await self.handle_execute(websocket, data)
            
        else:
            logger.warning(f"Unknown message type: {msg_type}")
    
    async def send_pong(self, websocket):
        """Send heartbeat response"""
        message = {
            "type": "pong",
            "active_tasks": self.active_tasks
        }
        await websocket.send(json.dumps(message))
    
    async def handle_execute(self, websocket, data: dict):
        """Handle script execution request"""
        task_id = data.get("task_id")
        script_name = data.get("script_name")
        script_code = data.get("script_code")
        args = data.get("args", [])
        timeout = data.get("timeout", 60)
        
        logger.info(f"Received task {task_id}: {script_name}")
        
        # Increment active tasks
        self.active_tasks += 1
        
        try:
            # Execute script
            result = await self.executor.execute_script(
                task_id=task_id,
                script_name=script_name,
                script_code=script_code,
                args=args,
                timeout=timeout
            )
            
            # Send result back to Gateway
            response = {
                "type": "result",
                "task_id": task_id,
                **result
            }
            
            await websocket.send(json.dumps(response))
            logger.info(f"Task {task_id} result sent to Gateway")
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            # Send error result
            error_response = {
                "type": "result",
                "task_id": task_id,
                "success": False,
                "output": "",
                "exit_code": 1,
                "error": str(e)
            }
            await websocket.send(json.dumps(error_response))
        finally:
            # Decrement active tasks
            self.active_tasks = max(0, self.active_tasks - 1)
