import json
from fastmcp import FastMCP

from rp_why_core import classify_dok, detect_compression, DOK_NAMES


def register_classify_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def rpwhy_classify_prompt(text: str) -> str:
        """Classify a single prompt's DOK level. Returns DOK level, confidence, matched keywords, and compression detection. Useful for spore interoception integration."""
        dok_level, confidence, matched_keywords = classify_dok(text)
        is_compressed = detect_compression(text, session_prompt_index=1)

        adjusted_level = min(dok_level + 1, 4) if is_compressed else dok_level

        result = {
            "text_preview": text[:150],
            "dok_level": dok_level,
            "dok_name": DOK_NAMES.get(dok_level, "Unknown"),
            "confidence": round(confidence, 3),
            "matched_keywords": matched_keywords,
            "is_compressed": is_compressed,
            "dok_adjusted": adjusted_level,
            "dok_adjusted_name": DOK_NAMES.get(adjusted_level, "Unknown"),
        }
        return json.dumps(result, indent=2)
