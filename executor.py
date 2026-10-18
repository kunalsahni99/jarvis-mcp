# executor.py - Sandbox Script Execution Engine
# ================================================
# Core engine that runs scripts in a subprocess and returns results
#
# Functions to implement:
#
# 1. check_blocked_commands(script: str, language: str) -> str | None
#    - Scans script text for dangerous/destructive commands
#    - Returns the blocked command name if found, None if clean
#    - Maintain separate block lists for Python and PowerShell
#    - Python blocklist ideas: os.remove, shutil.rmtree, subprocess.*, os.system, __import__
#    - PowerShell blocklist ideas: Remove-*, Format-*, Stop-Computer, del /f
#
# 2. execute_script(language, script, parameters, timeout) -> dict
#    - Validate language against ALLOWED_LANGUAGES
#    - Check for blocked commands before execution
#    - Inject parameters as variables at the top of the script
#      - Python: variable = value (use json.dumps for values)
#      - PowerShell: $variable = value
#    - Execute via subprocess.run with:
#      - capture_output=True, text=True
#      - timeout from config (use min of requested vs MAX_TIMEOUT)
#      - safe working directory (e.g., /tmp)
#    - Handle subprocess.TimeoutExpired and general exceptions
#    - Truncate output if exceeds MAX_OUTPUT_SIZE
#    - Return dict: executionId, success, exitCode, stdout, stderr, executionTime
#
# 3. log_execution(execution_id, language, script, response)
#    - Append execution metadata to a daily JSONL log file in ./logs/
#    - Include: timestamp, language, script preview (first 500 chars), exit code, timing
#
# Dependencies: subprocess, time, uuid, json, os, datetime
# Config imports: MAX_TIMEOUT, MAX_OUTPUT_SIZE, ALLOWED_LANGUAGES, LOG_EXECUTIONS
