import json
from fastmcp import FastMCP

from rp_why_baseline import RPWhyAnalyzer


def register_baseline_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def rpwhy_baseline(regenerate: bool = False) -> str:
        """Generate or retrieve the current baseline. If baseline exists and regenerate=False, returns it. If regenerate=True or no baseline exists, generates fresh from all session history."""
        analyzer = RPWhyAnalyzer()
        existing = analyzer.load_baseline()

        if existing and not regenerate:
            return json.dumps(existing, indent=2, default=str)

        baseline = analyzer.generate_baseline()
        if baseline is None:
            return json.dumps({
                "error": "generation_failed",
                "message": "Could not generate baseline. Ensure goose sessions.db exists."
            }, indent=2)

        if 'error' in baseline:
            return json.dumps(baseline, indent=2)

        analyzer.save_baseline(baseline)
        return json.dumps(baseline, indent=2, default=str)
