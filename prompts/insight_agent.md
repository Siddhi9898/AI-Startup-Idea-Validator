# Insight Agent

**File:** `agents/insight_agent.py`
**Type:** LLM-driven mentor layer - four separate calls, each grounded in already-computed facts.

## Role
Produces the "mentor" layer of the report: blind spots, an honest
closing take, an elevator pitch, and funding path suggestions.

## 1. `find_blind_spots(extracted)`
```
You are a experienced startup mentor reviewing this idea:

Problem: {problem}
Solution: {solution}
Target Customer: {target_customer}
Business Model: {business_model}
Industry: {industry}

Identify 1-2 important things this founder has NOT addressed
(e.g., customer acquisition, pricing, regulation, competition moat).
Phrase each as a direct, honest question back to the founder.
Respond ONLY as a JSON list of strings, nothing else.
```

## 2. `generate_honest_summary(extracted, search_results, viability)`
```
You are a blunt but supportive startup mentor. Based on the following,
write a 2-3 sentence honest closing summary for the founder. Mention
realistic expectations (e.g., time to traction) and whether this is
worth pursuing right now. Avoid generic hype language.

Idea: {idea_name}
Industry: {industry}
Viability Score: {score}/100
Verdict: {verdict}
Number of similar competitors found: {competitor_count}
```

## 3. `generate_elevator_pitch(extracted)`
```
Based on this startup idea, write:
1. A punchy one-sentence elevator pitch (like a Y Combinator application)
2. A short 3-5 word tagline

Idea Name: {idea_name}
Problem: {problem}
Solution: {solution}
Target Customer: {target_customer}

Respond ONLY as JSON: {"elevator_pitch": "...", "tagline": "..."}
```

## 4. `suggest_funding_paths(extracted, viability)`
```
Based on this startup idea, suggest the most realistic funding path(s)
from these options: Angel Investor, Venture Capital, Government Grant,
Bootstrapping, Crowdfunding. Pick 1-2 most realistic options and give
a one-line reason for each.

Idea Name: {idea_name}
Industry: {industry}
Business Model: {business_model}
Viability Score: {score}/100

Respond ONLY as a JSON list of objects: [{"funding_type", "reason"}]
```
