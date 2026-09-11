"""Prompt templates for synthesizing multi-source marine intelligence into tailored responses."""

RESPONSE_SYNTHESIS_PROMPT = """Synthesize the assembled marine evidence into a clear, persona-tailored response.

User Role: {user_role}
User Query: {query}
Safety Level: {safety_level}

Assembled Evidence:
{evidence_text}

Response Structure Guidelines:
1. Safety Header: Start with a clear safety assessment banner (SAFE / CAUTION / WARNING / DANGER).
2. Key Directives / Insights: 2-3 high-impact actionable points.
3. Detailed Analysis: Oceanographic conditions (waves, wind, SST, Chlorophyll, currents).
4. Spatial / Coordinates Summary: Specific recommendations with distance and bearing if applicable.
5. Evidence Summary & Data Source Transparency.
"""
