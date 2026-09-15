"""
Report Agent (Fully Deterministic)
--------------------------------------
No LLM call - pure Python string formatting, compiling the Shared
Context into a Markdown report. Now includes the Pipeline Execution
Log, making each step's deterministic validation outcome visible and
traceable (per reviewer requirement #6).
"""


def generate_report(state_dict: dict) -> str:
    extracted = state_dict.get("extracted", {})
    viability = state_dict.get("viability_score", {})
    market = state_dict.get("market_analysis", {})
    competitors = state_dict.get("competitors", {})
    swot = state_dict.get("swot", {})
    mvp = state_dict.get("mvp", {})
    gtm = state_dict.get("gtm", {})
    log = state_dict.get("execution_log", [])

    log_lines = "\n".join(
        f"- {entry['step']}: {'OK' if entry['is_valid'] else 'VALIDATION ISSUE'}"
        + (f" ({entry['note']})" if entry.get("note") else "")
        for entry in log
    )

    report = f"""# Startup Validation Report

## Executive Summary
{state_dict.get('honest_summary', '')}

## Startup Idea
- **Name:** {extracted.get('idea_name', '')}
- **Problem:** {extracted.get('problem', '')}
- **Solution:** {extracted.get('solution', '')}
- **Target Customer:** {extracted.get('target_customer', '')}
- **Industry:** {extracted.get('industry', '')}
- **Business Model:** {extracted.get('business_model', '')}

## Viability Score
**{viability.get('overall_score', 'N/A')}/100** — {viability.get('verdict', '')}

Score breakdown: {viability.get('breakdown', {})}

## Market Analysis
- Growth Trend: {market.get('growth_trend', 'Not yet analyzed')}
- Customer Segments: {', '.join(market.get('customer_segments', [])) or 'Not yet analyzed'}
- Data Quality: {market.get('data_quality', {})}

## Competitor Analysis
{competitors.get('market_gap', 'Not yet analyzed')}
- Data Quality: {competitors.get('data_quality', {})}

## SWOT Analysis
- Strengths: {', '.join(swot.get('strengths', [])) or 'Not yet analyzed'}
- Weaknesses: {', '.join(swot.get('weaknesses', [])) or 'Not yet analyzed'}
- Opportunities: {', '.join(swot.get('opportunities', [])) or 'Not yet analyzed'}
- Threats: {', '.join(swot.get('threats', [])) or 'Not yet analyzed'}
- Risk Score: {swot.get('risk_score', 'N/A')}/10

## MVP Recommendation (MoSCoW)
{chr(10).join('- [' + f.get('priority', '') + '] ' + f.get('feature', '') for f in mvp.get('mvp_features', []))}
Timeline: {mvp.get('estimated_timeline', 'Not yet analyzed')}

## Go-To-Market Strategy
{gtm.get('positioning_statement', 'Not yet analyzed')}
- Channels: {', '.join(gtm.get('marketing_channels', []))}
- Pricing: {gtm.get('pricing_strategy', '')}

## Blind Spots to Consider
{chr(10).join('- ' + q for q in state_dict.get('blind_spots', []))}

## Elevator Pitch
{state_dict.get('elevator_pitch', {}).get('elevator_pitch', '')}

## Suggested Funding Paths
{chr(10).join('- ' + f.get('funding_type', '') + ': ' + f.get('reason', '') for f in state_dict.get('funding_suggestions', []))}

## Pipeline Execution Log
{log_lines}
"""
    return report
