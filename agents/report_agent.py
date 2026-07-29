"""
Report Agent
---------------
Compiles all agent outputs into a structured final validation report
(Markdown format), matching docs/architecture.md's Report Agent role.
"""


def generate_report(state_dict: dict) -> str:
    extracted = state_dict.get("extracted", {})
    viability = state_dict.get("viability_score", {})
    market = state_dict.get("market_analysis", {})
    competitors = state_dict.get("competitors", {})
    swot = state_dict.get("swot", {})
    mvp = state_dict.get("mvp", {})
    gtm = state_dict.get("gtm", {})

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

## Market Analysis
- TAM: {market.get('tam_estimate', 'Not yet analyzed')}
- SAM: {market.get('sam_estimate', 'Not yet analyzed')}
- SOM: {market.get('som_estimate', 'Not yet analyzed')}
- Growth Trend: {market.get('growth_trend', 'Not yet analyzed')}

## Competitor Analysis
{competitors.get('market_gap', 'Not yet analyzed')}

## SWOT Analysis
- Strengths: {', '.join(swot.get('strengths', [])) or 'Not yet analyzed'}
- Weaknesses: {', '.join(swot.get('weaknesses', [])) or 'Not yet analyzed'}
- Opportunities: {', '.join(swot.get('opportunities', [])) or 'Not yet analyzed'}
- Threats: {', '.join(swot.get('threats', [])) or 'Not yet analyzed'}

## MVP Recommendation
{mvp.get('estimated_timeline', 'Not yet analyzed')}

## Go-To-Market Strategy
{gtm.get('positioning_statement', 'Not yet analyzed')}

## Blind Spots to Consider
{chr(10).join('- ' + q for q in state_dict.get('blind_spots', []))}

## Elevator Pitch
{state_dict.get('elevator_pitch', {}).get('elevator_pitch', '')}

## Suggested Funding Paths
{chr(10).join('- ' + f.get('funding_type', '') + ': ' + f.get('reason', '') for f in state_dict.get('funding_suggestions', []))}
"""
    return report
