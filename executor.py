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


import json, os, re, subprocess, sys, tempfile, time
from uuid import uuid4
from datetime import datetime, timezone
from config import MAX_TIMEOUT, MAX_OUTPUT_SIZE, LOG_EXECUTIONS, ALLOWED_LANGUAGES

BLOCKED = {
    "python": [
        r"\bos\.(remove|unlink|rmdir|removedirs|system|popen|exec\w*|spawn\w*|kill)\b",
        r"\bshutil\.(rmtree|move)\b",
        r"\bsubprocess\b", r"__import__", r"\beval\s*\(", r"\bexec\s*\(",
        r"\bsocket\b", r"\bctypes\b",
    ]
}

# Helper functions
def check_blocked_commands(script: str, language: str) -> str | None:
    for pattern in BLOCKED.get(language, []):
        m = re.search(pattern, script, re.IGNORECASE)
        if m:
            return m.group(0)
    return None

def _truncate(text: str) -> str:
    if len(text) > MAX_OUTPUT_SIZE:
        return text[MAX_OUTPUT_SIZE] + "\n...[output truncated]"
    return text

def _as_text(x) -> str:
    return x.decode(errors="replace") if isinstance(x, bytes) else (x or "")

def _inject_params(language: str, parameters: dict | None) -> str:
    if not parameters:
        return ""

    lines = []
    for k, v in parameters.items():
        if not k.isidentifier():
            raise ValueError(f"Invalid parameter name: {k!r}")
        if language == "python":
            lines.append(f"{k} = {v!r}")
        #TODO: add the else condition to inject Powershell parameters/variables

    return "\n".join(lines) + "\n"

# Main function - invoked by the tool
def execute_script(language, script, parameters=None, timeout=None) -> dict:
    execution_id = str(uuid4())
    start = time.time()
    language = (language or "").lower()

    def respond(success, code, out="", err=""):
        resp = {
            "executionId": execution_id,
            "success": success,
            "exitCode": code,
            "stdout": _truncate(out),
            "stderr": _truncate(err),
            "executionTime": round(time.time() - start, 3)
        }

        if LOG_EXECUTIONS:
            log_execution(execution_id, language, script, resp)
        return resp

    if language not in ALLOWED_LANGUAGES:
        return respond(False, -1, err=f"Language {language} not allowed. Allowed ones are: {list(ALLOWED_LANGUAGES)}")

    blocked = check_blocked_commands(script, language)
    if blocked:
        return respond(False, -1, err=f"Blocked: script contains disallowed command '{blocked}'")

    try:
        code = _inject_params(language, parameters) + script
    except ValueError as e:
        return respond(False, -1, err=str(e))

    if language == "python":
        cmd = [sys.executable, "-I", "-c", code]
    #TODO: add an else condition for PowerShell execution

    effective_timeout = min(timeout or MAX_TIMEOUT, MAX_TIMEOUT)
    safe_env = {"PATH": os.environ.get("PATH", ""), "HOME": tempfile.gettempdir()}

    try:
        r = subprocess.run(cmd, capture_output=True,
                           text=True, timeout=effective_timeout,
                           cwd=tempfile.gettempdir(), env=safe_env)
        return respond(r.returncode == 0, r.returncode, r.stdout, r.stderr)
    except subprocess.TimeoutExpired as e:
        return respond(False, -1, _as_text(e.stdout), f"Timed out after {effective_timeout}s")
    except Exception as e:
        return respond(False, -1, err=f"Execution error: {e}")

# Logs the execution after each run
def log_execution(execution_id, language, script, response) -> None:
    try:
        os.makedirs("logs", exist_ok=True)
        now = datetime.now(timezone.utc)
        
        entry = {
            "timestamp": now.isoformat(), "executionId": execution_id,
            "language": language, "scriptPreview": script[:500],
            "exitCode": response["exitCode"], "success": response["success"],
            "executionTime": response["executionTime"]
        }

        with open(f"logs/{now:%d-%m-%Y}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    except Exception:
        pass