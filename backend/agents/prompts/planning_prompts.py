"""Prompt templates for planning multi-source marine intelligence retrieval."""

PLANNING_PROMPT = """Given the user's intent, location, and timeframe, construct a minimal, ordered execution plan.

Intent: {intent}
Location: {spatial_summary}
Timeframe: {temporal_summary}
User Persona: {user_role}

Select required tool steps from available subsystems:
1. P4 External Tools:
   - fetch_ocean_weather (wind speed, wave height, swell period, visibility)
   - fetch_sst_data (sea surface temperature)
   - fetch_chlorophyll_data (chlorophyll-a concentration)
   - fetch_hazard_bulletins (INCOIS / IMD warning bulletins)
2. P6 Marine Analytics & Risk Calculations:
   - compute_pfz_zones (PFZ hotspot calculation using SST + Chlorophyll gradients)
   - calculate_sea_state_risk (vessel safety index and wave hazard score)
   - detect_algal_bloom_risk (HAB index computation)

Rules:
- ALWAYS calculate the sea state risk index before recommending potential fishing zones.
- Only invoke tools necessary for the classified intent.
"""
