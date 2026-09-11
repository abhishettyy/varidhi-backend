"""Prompt templates for extracting geographic locations, harbors, coordinates, and time windows."""

SPATIO_TEMPORAL_EXTRACTION_PROMPT = """Extract the spatial and temporal entities from this marine query.

Spatial Extraction Targets:
- Place / coastal region name (e.g. 'Kochi', 'Veraval', 'Gulf of Mannar', 'Visakhapatnam', 'Chennai coast')
- Specific harbor / port (e.g. 'Munambam Harbor', 'Kasimedu Fishing Harbour')
- Explicit coordinates (latitude, longitude) if provided
- Radius or distance from shore (in nautical miles or km)

Temporal Extraction Targets:
- Time phrase (e.g. 'tomorrow 4am', 'this weekend', 'next 24 hours', 'today afternoon')
- Forecast horizon in hours (default to 24 if unspecified)
- Whether the query refers to historical/past data

Query: "{query}"
Current Reference Time: "{current_time}"
"""
