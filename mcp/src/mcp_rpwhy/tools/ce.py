import json
from dataclasses import asdict
from fastmcp import FastMCP

from rp_why_ce import (
    find_agents_md_files,
    parse_implicit_commands,
    load_runs_from_db,
    compute_ce_report,
    CEReport,
)
from rp_why_baseline import RPWhyAnalyzer


def register_ce_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def rpwhy_ce(limit: int = 20) -> str:
        """Configuration Effectiveness report. Measures AGENTS.md adherence by detecting implicit command executions in recent sessions."""
        agents_files = find_agents_md_files()
        if not agents_files:
            return json.dumps({
                "error": "no_agents_md",
                "message": "No AGENTS.md files found in standard locations."
            }, indent=2)

        all_commands = []
        for agents_file in agents_files:
            commands = parse_implicit_commands(agents_file)
            all_commands.extend(commands)

        if not all_commands:
            return json.dumps({
                "error": "no_commands_parsed",
                "message": "No implicit commands found in AGENTS.md files.",
                "agents_files": agents_files,
            }, indent=2)

        runs = load_runs_from_db(limit=limit)
        if not runs:
            return json.dumps({
                "error": "no_runs",
                "message": "No session runs found in sessions.db.",
                "commands_parsed": len(all_commands),
            }, indent=2)

        analyzer = RPWhyAnalyzer()
        baseline = analyzer.load_baseline()
        adt_zone = "Expected"
        if baseline:
            adt_zone = baseline.get("three_dimensions", {}).get("adt_zone", "Expected")

        report = compute_ce_report(all_commands, runs, adt_zone)

        result = {
            "overall_score": report.overall_score,
            "band": report.band,
            "confidence": report.confidence,
            "total_instructions": report.total_instructions,
            "measured_instructions": report.measured_instructions,
            "token_waste_pct": report.token_waste_pct,
            "adt_quadrant": report.adt_quadrant,
            "nudge": report.nudge,
            "reflection": report.reflection,
            "dead_commands": [
                {"trigger": cmd.trigger, "source_file": cmd.source_file}
                for cmd in report.dead_commands
            ],
            "command_reports": [
                {
                    "trigger": cr.command.trigger,
                    "total_opportunities": cr.total_opportunities,
                    "success_rate": cr.success_rate,
                    "is_dead": cr.is_dead,
                }
                for cr in report.command_reports
            ],
            "agents_files": agents_files,
        }
        return json.dumps(result, indent=2)
