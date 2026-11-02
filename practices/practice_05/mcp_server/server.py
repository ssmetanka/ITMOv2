import sys
import json

def validate_diff_tool(diff_text: str, max_lines: int = 300, max_chars: int = 10000) -> dict:
    if not isinstance(diff_text, str):
        return {
            "status": "INVALID_INPUT",
            "reason": "diff_text должен быть строкой"
        }
    if not diff_text.strip():
        return {
            "status": "INVALID_INPUT",
            "reason": "diff_text не может быть пустым"
        }

    # count lines by normalized CRLF/LF
    lines = diff_text.strip().splitlines()
    count = len(lines)
    # count chars as UTF-16 code units to align with UI
    chars = len(diff_text.encode('utf-16-le')) // 2
    if count > max_lines or chars > max_chars:
        return {
            "status": "REJECTED",
            "lines": count,
            "chars": chars,
            "max_lines": max_lines,
            "max_chars": max_chars,
            "reason": "Превышены лимиты размера diff"
        }
    return {
        "status": "ACCEPTED",
        "lines": count,
        "chars": chars,
        "max_lines": max_lines,
        "max_chars": max_chars,
        "summary": "Diff прошёл проверку безопасности и готов к анализу."
    }

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")

        # Нотификации (уведомления без id) не требуют ответа
        if req_id is None:
            continue

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "diff-guard",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [{
                        "name": "validate_diff_stats",
                        "description": "Анализирует diff и валидирует его лимиты",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "diff_text": {"type": "string"},
                                "max_lines": {"type": "integer", "default": 300},
                                "max_chars": {"type": "integer", "default": 10000}
                            },
                            "required": ["diff_text"]
                        }
                    }]
                }
            }
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            if name == "validate_diff_stats":
                result = validate_diff_tool(
                    args.get("diff_text"),
                    args.get("max_lines", 300),
                    args.get("max_chars", 10000)
                )
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
                    }
                }
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
        else:
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
