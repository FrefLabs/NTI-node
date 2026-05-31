"""
Script Executor - Executes Python scripts received from Gateway
Uses a separate virtual environment for scripts to avoid dependency conflicts
"""

import asyncio
import subprocess
import tempfile
import logging
import base64
import sys
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class ScriptExecutor:
    def __init__(self, config):
        self.config = config
        self.timeout = config["execution"]["timeout"]
        self.temp_dir = Path(__file__).parent.parent / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Virtual environment for scripts
        self.venv_dir = Path(__file__).parent.parent / "scripts_venv"
        self.venv_python = self._get_venv_python_path()
        
        # Initialize virtual environment on first run
        self._ensure_venv_exists()
        
    def _get_venv_python_path(self):
        """Get path to Python executable in virtual environment"""
        if sys.platform == "win32":
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"
    
    def _ensure_venv_exists(self):
        """Create virtual environment if it doesn't exist and install dependencies"""
        if self.venv_dir.exists() and self.venv_python.exists():
            logger.info("Virtual environment for scripts already exists")
            return
        
        logger.info("Creating virtual environment for scripts...")
        try:
            # Create virtual environment
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_dir)],
                check=True,
                capture_output=True
            )
            logger.info("Virtual environment created successfully")
            
            # Install script dependencies (yfinance, pandas, numpy)
            logger.info("Installing script dependencies in virtual environment...")
            subprocess.run(
                [str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                capture_output=True
            )
            subprocess.run(
                [str(self.venv_python), "-m", "pip", "install", "yfinance", "pandas", "numpy"],
                check=True,
                capture_output=True
            )
            logger.info("Script dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating virtual environment: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception("Failed to create virtual environment for scripts")
    
    async def execute_script(self, task_id: str, script_name: str, script_code: str, 
                            args: list, timeout: int) -> dict:
        """
        Execute a Python script in isolated virtual environment
        
        Args:
            task_id: Unique task identifier
            script_name: Name of the script (for logging)
            script_code: Python code to execute
            args: Command line arguments
            timeout: Execution timeout in seconds
            
        Returns:
            dict with success, output, exit_code, error, and optionally file_content
        """
        logger.info(f"Executing task {task_id}: {script_name} with args {args}")
        
        # Save script to temp file
        temp_script = self.temp_dir / f"{task_id}.py"
        
        try:
            # Write script code with UTF-8 encoding
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(script_code)
            
            # Check if this is a file-generating script (has output file argument)
            generates_file = len(args) > 0 and (args[-1].endswith('.csv') or 
                                                 args[-1].endswith('.json') or
                                                 args[-1].endswith('.txt'))
            
            if generates_file:
                # Create temp output file
                output_file = self.temp_dir / f"{task_id}_output.csv"
                # Replace last argument with our temp file path
                modified_args = args[:-1] + [str(output_file)]
            else:
                modified_args = args
                output_file = None
            
            # Build command using virtual environment Python
            command = [str(self.venv_python), str(temp_script)] + modified_args
            
            # Execute
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise Exception(f"Script execution timed out after {timeout}s")
            
            output = stdout.decode() if stdout else ""
            error = stderr.decode() if stderr else ""
            
            # Build result
            result = {
                "success": process.returncode == 0,
                "output": output,
                "exit_code": process.returncode,
                "error": error if process.returncode != 0 else None
            }
            
            # If script generates a file, include it in result
            if generates_file and output_file and output_file.exists():
                with open(output_file, 'rb') as f:
                    file_content = f.read()
                result["file_content"] = base64.b64encode(file_content).decode()
                # Clean up output file
                output_file.unlink()
            
            logger.info(f"Task {task_id} completed with exit code {process.returncode}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            return {
                "success": False,
                "output": "",
                "exit_code": 1,
                "error": str(e)
            }
        finally:
            # Clean up temp script
            if temp_script.exists():
                temp_script.unlink()
