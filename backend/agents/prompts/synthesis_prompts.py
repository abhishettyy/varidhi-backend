"""Prompt templates for synthesizing multi-source marine intelligence into tailored responses."""

STRUCTURED_RESPONSE_SYNTHESIS_PROMPT = """Synthesize the provided marine analytics and evidence into an authoritative, grounded advisory.

### STRICT GUARDRAILS & INVARIANTS:
1. DECISION COMPLIANCE: You MUST strictly respect the P6 deterministic decision. If a selected zone is provided, it is the ONLY recommended zone. NEVER override it or select a different zone.
2. REJECTED ZONES: NEVER recommend a rejected zone. If higher-opportunity zones were disqualified (e.g. ZONE_C for Marine Protected Area restriction, or ZONE_A for high wave risk), explain the rejection reasons transparently.
3. GROUNDED EVIDENCE & ANTI-OVERCLAIMING:
   - Base all claims strictly on the provided observations and metrics.
   - Do NOT invent coordinates, latitude/longitude degrees, fish density/abundance numbers, water temperatures, wave heights, or wind speeds not explicitly provided in the context.
   - Do NOT state or imply official maritime safety clearance, port clearance, or statutory safety certification. Frame risk evaluations as heuristic assessments (e.g., 'favorable relative to evaluated alternatives', 'MODERATE risk').
4. PERSONA ADAPTATION & QUERY RELEVANCE:
   - For 'fisherman':
     * ANSWER THE EXACT QUESTION FIRST:
       - If the user asks about FISHING GROUNDS or WHERE TO FISH (e.g. "what is the good fishing zones", "where can i fish", "best spots"):
         Lead IMMEDIATELY with the Recommended Fishing Ground (e.g. 'Netravati Offshore (Zone B)'). Detail the distance, bearing, target species (Mackerel, Sardines), depth, and why it was selected. Then mention restricted/danger zones to avoid (e.g. Mulki Sanctuary, Gurupura Shelf). Include a brief 1-line note on waves/wind at the end. DO NOT lead with a heavy weather dump when the user specifically asked for fishing grounds!
       - If the user asks about WEATHER, WAVES, or SAFETY (e.g. "how is the sea", "is it safe", "wave height"):
         Lead directly with sea conditions (wave height in meters, wind speed in knots, sea state: Calm/Moderate/Rough) and the safety directive.
       - If the user is GREETING or CHATTING CASUALLY (e.g. "hi", "hyee", "hello", "good morning", "what can you do"):
         Respond warmly and concisely. Greet them, state the current sea condition briefly, and invite them to ask about fishing grounds or sea safety for their port.
     * TONE & NAMING: Speak naturally and warmly like an experienced, helpful coastal marine guide. Use clear bullet points and helpful emojis (🌊, 🐟, ⚠️, ⏰). ALWAYS use meaningful local names (e.g. 'Netravati Offshore (Zone B)', 'Gurupura Shelf (Zone A)', 'Mulki Marine Sanctuary (Zone C)') instead of raw codes like 'ZONE_B'. State distance and bearing. Clearly highlight dangerous waters or restricted sanctuaries. Do NOT output robotic academic headers like '### Zone Rejections: None', '### Safety Disclaimer', or dry legal disclaimers.
   - For 'researcher': Use comprehensive markdown with headers, scientific terminology, and Markdown Tables summarizing Biophysical State (SST, Chlorophyll, Wave, Wind) and the Multi-Engine Decision Matrix (Zone ID, Opportunity, Risk, Regulatory, Ranking Score, Decision Factors). Do not assert thermal fronts or biological productivity unless present in the provided evidence.
   - For 'general' / 'maritime_operator': Balanced advisory with sea state conditions and clear action advice.

Context Data:
{context_json}
"""

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
5. Anti-Overclaiming & Synthetic Disclosure: Include notice that assessment uses synthetic demonstration data and does not constitute official statutory clearance.
6. Evidence Summary & Data Source Transparency.
"""

