import json
from datetime import datetime, date
from typing import Optional
from fastmcp import FastMCP

from rp_why_baseline import RPWhyAnalyzer
from rp_why_core import (
    calculate_adt_zone,
    estimate_tm_tier,
    aggregate_session_metadata,
    get_zone_nudges,
    get_zone_reflection,
)


def _get_today_prompts(analyzer: RPWhyAnalyzer) -> list:
    all_prompts = analyzer.get_all_user_prompts()
    today = date.today().isoformat()
    return [p for p in all_prompts if p.get('session_date', '')[:10] == today]


def _get_current_session_prompts(analyzer: RPWhyAnalyzer) -> list:
    all_prompts = analyzer.get_all_user_prompts()
    if not all_prompts:
        return []
    last_session_id = all_prompts[-1]['session_id']
    return [p for p in all_prompts if p['session_id'] == last_session_id]


def register_analysis_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def rpwhy_current() -> str:
        """Analyze the current/most recent session. Returns DOK scores, compression %, distribution, peak prompt, ADT zone, and growth nudge."""
        analyzer = RPWhyAnalyzer()
        if not analyzer.connect():
            return json.dumps({"error": "sessions_db_not_found", "message": "Could not connect to goose sessions.db"}, indent=2)

        try:
            prompts = _get_today_prompts(analyzer)
            if not prompts:
                prompts = _get_current_session_prompts(analyzer)

            if not prompts:
                return json.dumps({"error": "no_prompts", "message": "No prompts found for current session or today"}, indent=2)

            analysis = analyzer.analyze_prompts(prompts)
            if 'error' in analysis:
                return json.dumps(analysis, indent=2)

            session_ids = set(p['session_id'] for p in prompts)
            session_meta = analyzer.get_session_metadata()
            relevant_meta = {sid: session_meta[sid] for sid in session_ids if sid in session_meta}

            tm_tiers = [analyzer.estimate_tm_tier(meta) for meta in relevant_meta.values()]
            avg_tm = round(sum(tm_tiers) / len(tm_tiers)) if tm_tiers else 3

            adt_zone = analyzer.calculate_adt_zone(analysis['dok_adjusted'], avg_tm)
            nudges = get_zone_nudges(adt_zone)
            reflection = get_zone_reflection(adt_zone)

            peak = analysis.get('peak_prompt')
            peak_text = peak['text'][:200] if peak else None

            result = {
                "session_date": date.today().isoformat(),
                "prompts_analyzed": analysis['total_prompts'],
                "dok_adjusted": analysis['dok_adjusted'],
                "dok_raw": analysis['dok_raw'],
                "dok_lift": analysis['dok_lift'],
                "compression_pct": analysis['compression_pct'],
                "dok_3_4_pct": analysis['dok_3_4_pct'],
                "dok_distribution": analysis['dok_distribution'],
                "tm_tier": avg_tm,
                "adt_zone": adt_zone,
                "peak_dok": analysis['peak_dok'],
                "peak_prompt_preview": peak_text,
                "growth_nudge": {
                    "zone": adt_zone,
                    "reflection": reflection,
                    "nudges": nudges,
                },
            }
            return json.dumps(result, indent=2)
        finally:
            analyzer.close()

    @mcp.tool()
    def rpwhy_compare() -> str:
        """Compare current session to baseline. Returns delta analysis with trajectory, zone shift, and growth nudge."""
        analyzer = RPWhyAnalyzer()
        baseline = analyzer.load_baseline()
        if not baseline:
            return json.dumps({
                "error": "no_baseline",
                "message": "No baseline found. Run rpwhy_baseline with regenerate=True to generate one."
            }, indent=2)

        if not analyzer.connect():
            return json.dumps({"error": "sessions_db_not_found", "message": "Could not connect to goose sessions.db"}, indent=2)

        try:
            prompts = _get_today_prompts(analyzer)
            if not prompts:
                prompts = _get_current_session_prompts(analyzer)

            if not prompts:
                return json.dumps({"error": "no_prompts", "message": "No prompts found for current session or today"}, indent=2)

            analysis = analyzer.analyze_prompts(prompts)
            if 'error' in analysis:
                return json.dumps(analysis, indent=2)

            session_ids = set(p['session_id'] for p in prompts)
            session_meta = analyzer.get_session_metadata()
            relevant_meta = {sid: session_meta[sid] for sid in session_ids if sid in session_meta}

            tm_tiers = [analyzer.estimate_tm_tier(meta) for meta in relevant_meta.values()]
            avg_tm = round(sum(tm_tiers) / len(tm_tiers)) if tm_tiers else 3

            adt_zone = analyzer.calculate_adt_zone(analysis['dok_adjusted'], avg_tm)

            baseline_dims = baseline.get('three_dimensions', {})
            baseline_dok = baseline_dims.get('dok_adjusted', baseline.get('average_dok_score', 2.0))
            baseline_tm = baseline_dims.get('tm_tier', 3)
            baseline_zone = baseline_dims.get('adt_zone', 'unknown')

            dok_delta = round(analysis['dok_adjusted'] - baseline_dok, 3)
            tm_delta = avg_tm - baseline_tm
            zone_shifted = adt_zone != baseline_zone

            dok_3_4_baseline = baseline.get('dok_3_4_pct', 0)
            dok_3_4_delta = round(analysis['dok_3_4_pct'] - dok_3_4_baseline, 1)

            compression_baseline = baseline.get('compression_pct', 0)
            compression_delta = round(analysis['compression_pct'] - compression_baseline, 1)

            if dok_delta > 0.2:
                trajectory = "ascending"
            elif dok_delta < -0.2:
                trajectory = "descending"
            else:
                trajectory = "stable"

            nudges = get_zone_nudges(adt_zone)
            reflection = get_zone_reflection(adt_zone)

            result = {
                "current": {
                    "dok_adjusted": analysis['dok_adjusted'],
                    "tm_tier": avg_tm,
                    "adt_zone": adt_zone,
                    "dok_3_4_pct": analysis['dok_3_4_pct'],
                    "compression_pct": analysis['compression_pct'],
                },
                "baseline": {
                    "dok_adjusted": baseline_dok,
                    "tm_tier": baseline_tm,
                    "adt_zone": baseline_zone,
                    "dok_3_4_pct": dok_3_4_baseline,
                    "compression_pct": compression_baseline,
                },
                "deltas": {
                    "dok": dok_delta,
                    "tm": tm_delta,
                    "dok_3_4_pct": dok_3_4_delta,
                    "compression_pct": compression_delta,
                },
                "trajectory": trajectory,
                "zone_shifted": zone_shifted,
                "growth_nudge": {
                    "zone": adt_zone,
                    "reflection": reflection,
                    "nudges": nudges,
                },
            }
            return json.dumps(result, indent=2)
        finally:
            analyzer.close()

    @mcp.tool()
    def rpwhy_overall() -> str:
        """Full longitudinal report. Daily breakdown, phase detection, trajectory, token spend summary."""
        analyzer = RPWhyAnalyzer()
        if not analyzer.connect():
            return json.dumps({"error": "sessions_db_not_found", "message": "Could not connect to goose sessions.db"}, indent=2)

        try:
            prompts = analyzer.get_all_user_prompts()
            if not prompts:
                return json.dumps({"error": "no_prompts", "message": "No prompts found in sessions.db"}, indent=2)

            analysis = analyzer.analyze_prompts(prompts)
            if 'error' in analysis:
                return json.dumps(analysis, indent=2)

            session_meta = analyzer.get_session_metadata()
            tm_tiers = [analyzer.estimate_tm_tier(meta) for meta in session_meta.values()]
            avg_tm = round(sum(tm_tiers) / len(tm_tiers)) if tm_tiers else 3

            daily_scores = analyzer.get_daily_breakdown(prompts)
            phases = analyzer.detect_phases(daily_scores)
            trajectory = analyzer.calculate_trajectory(daily_scores)
            adt_zone = analyzer.calculate_adt_zone(analysis['dok_adjusted'], avg_tm, trajectory)

            daily_tokens = analyzer.get_daily_token_spend()
            total_tokens = sum(d['total_tokens'] for d in daily_tokens)
            daily_avg_tokens = round(total_tokens / len(daily_tokens)) if daily_tokens else 0

            baseline = analyzer.load_baseline()

            result = {
                "period": {
                    "first_session": prompts[0]['session_date'][:10] if prompts else None,
                    "last_session": prompts[-1]['session_date'][:10] if prompts else None,
                    "total_days": len(daily_scores),
                },
                "three_dimensions": {
                    "dok_adjusted": analysis['dok_adjusted'],
                    "dok_raw": analysis['dok_raw'],
                    "tm_tier": avg_tm,
                    "adt_zone": adt_zone,
                },
                "analysis": {
                    "total_prompts": analysis['total_prompts'],
                    "dok_3_4_pct": analysis['dok_3_4_pct'],
                    "compression_pct": analysis['compression_pct'],
                    "dok_distribution": analysis['dok_distribution'],
                },
                "trajectory": trajectory,
                "phases": phases,
                "daily_scores_last_14": daily_scores[-14:],
                "token_spend": {
                    "total_tokens": total_tokens,
                    "daily_avg": daily_avg_tokens,
                    "days_tracked": len(daily_tokens),
                },
                "baseline_exists": baseline is not None,
                "baseline_generated_at": baseline.get('generated_at') if baseline else None,
            }
            return json.dumps(result, indent=2, default=str)
        finally:
            analyzer.close()

    @mcp.tool()
    def rpwhy_token_spend() -> str:
        """Daily token spend breakdown. Shows sessions, prompts, total/input/output tokens per day."""
        analyzer = RPWhyAnalyzer()
        if not analyzer.connect():
            return json.dumps({"error": "sessions_db_not_found", "message": "Could not connect to goose sessions.db"}, indent=2)

        try:
            daily_tokens = analyzer.get_daily_token_spend()
            if not daily_tokens:
                return json.dumps({"error": "no_token_data", "message": "No token spend data found"}, indent=2)

            total_tokens = sum(d['total_tokens'] for d in daily_tokens)
            total_prompts = sum(d['prompts'] for d in daily_tokens)
            total_sessions = sum(d['sessions'] for d in daily_tokens)

            result = {
                "summary": {
                    "total_tokens": total_tokens,
                    "total_prompts": total_prompts,
                    "total_sessions": total_sessions,
                    "days_tracked": len(daily_tokens),
                    "daily_avg_tokens": round(total_tokens / len(daily_tokens)) if daily_tokens else 0,
                    "tokens_per_prompt": round(total_tokens / total_prompts) if total_prompts > 0 else 0,
                },
                "daily_last_14": daily_tokens[-14:],
            }
            return json.dumps(result, indent=2)
        finally:
            analyzer.close()
