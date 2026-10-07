import sys
import json

def validate_diff_tool(diff_text: str, max_lines: int = 300) -> dict:
    if not diff_text or not isinstance(diff_text, str) or not diff_text.strip():
        return {
            "error": "INVALID_INPUT",
            "message": "Параметр diff_text не может быть пустым или нестроковым"
        }
    
    lines = diff_text.strip().splitlines()
    count = len(lines)
    if count > max_lines:
        return {
            "status": "REJECTED",
            "lines": count,
            "max_allowed": max_lines,
            "reason": f"Размер diff ({count} строк) превышает лимит ({max_lines}). Отклонено до вызова LLM."
        }
        
    return {
        "status": "ACCEPTED",
        "lines": count,
        "max_allowed": max_lines,
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

        if method == "tools/list":
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
                                "max_lines": {"type": "integer", "default": 300}
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
                result = validate_diff_tool(args.get("diff_text"), args.get("max_lines", 300))
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
            # Общие методы initialize и т.д.
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
