import re
import json

def parse_entities_flexible(output):
    if isinstance(output, dict):
        return output

    try:
        # Remove leading/trailing whitespace
        cleaned = output.strip()
        
        # Match and remove triple backtick code block with optional language tag
        code_block_match = re.match(r"^```(?:\s*)(\w+)?(?:\s*)\n?(.*)```$", cleaned, re.DOTALL | re.IGNORECASE)
        if code_block_match:
            language = code_block_match.group(1) or ""
            content = code_block_match.group(2).strip()
        else:
            # Fallback: remove stray backticks if not a full code block
            content = cleaned.strip("`").strip()
            language = ""

        if language.lower() == "json":
            try:
                return json.loads(content)
            except Exception as e:
                print("Error parsing JSON:", e)
                return {"names": []}
        else:
            # For non-JSON (e.g., cypher), just return the content as-is
            return content

    except Exception as e:
        print("Unexpected error:", e)
        return {"names": []}
