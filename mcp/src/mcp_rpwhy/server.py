import sys
import os
from pathlib import Path
from fastmcp import FastMCP

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scripts"

scripts_override = os.environ.get("RPWHY_SCRIPTS_PATH")
if scripts_override:
    SCRIPTS_DIR = Path(scripts_override)

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

INSTRUCTIONS = """
rp-why measures AI collaboration quality across three dimensions:
- DOK (Depth of Knowledge): Cognitive complexity of human prompts (1.0-4.0, Webb's framework)
- TM (Tool Maturity): Intentional orchestration of AI tools (Orchestra Model, Tiers 1-6)
- ADT (Agentic Delegation Trust): Diagnostic zone from TM x DOK matrix

Usage guidance:
- Call rpwhy_current at session end to reflect on the session's cognitive depth
- Call rpwhy_compare for daily check-ins against baseline
- Call rpwhy_classify_prompt when you want to assess a single prompt's DOK (useful for spore interoception integration)
- rpwhy_baseline and rpwhy_overall are for periodic review, not every session
- rpwhy_ce measures configuration adherence - run when the practitioner asks about config effectiveness
- rpwhy_token_spend provides daily token consumption breakdown
"""

mcp = FastMCP("rp-why", instructions=INSTRUCTIONS)

from mcp_rpwhy.tools.analysis import register_analysis_tools
from mcp_rpwhy.tools.baseline import register_baseline_tools
from mcp_rpwhy.tools.classify import register_classify_tools
from mcp_rpwhy.tools.ce import register_ce_tools

register_analysis_tools(mcp)
register_baseline_tools(mcp)
register_classify_tools(mcp)
register_ce_tools(mcp)


def main():
    mcp.run()
