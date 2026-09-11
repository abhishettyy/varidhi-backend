"""Prompt templates for marine intent classification."""

INTENT_CLASSIFICATION_PROMPT = """Analyze the following marine/maritime user query and classify its intent.

Available Intents:
- potential_fishing_zone: Seeking good fishing spots, fish aggregations, SST fronts, chlorophyll areas, tuna or sardine hotspots.
- ocean_weather_safety: Inquiring about wave heights, swell, wind speeds, sea state, visibility, or general conditions for going to sea.
- hazard_alert: Urgent questions regarding cyclones, storms, tsunami warnings, gale alerts, or extreme weather warnings.
- water_quality_algal_bloom: Inquiries about red tides, toxic algae, salinity anomalies, dead zones, or water discoloration.
- navigation_advisory: Safe channel routes, harbor ingress/egress, shoals, shallow reefs, or passage planning.
- general_marine_query: General knowledge, oceanography concepts, or general inquiries not tied to a specific operational action.
- out_of_scope: Queries unrelated to oceans, seas, fishing, weather, or marine domains.

Query: "{query}"

Respond with the primary intent, any secondary intents, confidence score (0.0 to 1.0), and whether this indicates an urgent safety hazard.
"""
