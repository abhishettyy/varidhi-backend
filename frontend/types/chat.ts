import { RoleType, SafetySeverity } from './marine';

export interface SafetyAlertData {
  severity: SafetySeverity;
  title: string;
  description: string;
  action_advice: string;
  issued_at?: string;
}

export interface DecisionSummary {
  selected_zone_id: string;
  status: 'SELECTED' | 'ELIGIBLE' | 'REJECTED_RISK' | 'REJECTED_LEGAL' | 'NO_ELIGIBLE_ZONES';
  opportunity_score?: number;
  risk_score?: number;
  regulatory_status?: string;
  ranking_score?: number;
  distance_nm?: number;
  bearing?: string;
  species?: string[];
  latitude?: number;
  longitude?: number;
  reasons: string[];
  safety_level?: string;
  action_advice?: string;
}

export interface ZoneSummary {
  zone_id: string;
  status: string;
  opportunity_score?: number;
  risk_score?: number;
  regulatory_status?: string;
  ranking_score?: number;
  distance_nm?: number;
  bearing?: string;
  species?: string[];
  latitude?: number;
  longitude?: number;
  reasons: string[];
}

export interface EvidenceItemResponse {
  evidence_id: string;
  evidence_type: string;
  source: string;
  summary: string;
  metrics: Record<string, unknown>;
  confidence: number;
  spatial_tag?: string;
  timestamp?: string;
  raw_payload?: Record<string, unknown>;
}

export interface VisualPayloadData {
  map_features_geojson?: Record<string, unknown>;
  charts_data?: Array<Record<string, unknown>>;
  metric_badges?: Record<string, string>;
  focus_zone_id?: string;
  highlight_layer?: string;
}

export interface QueryContextResponse {
  intent: string;
  confidence: number;
  location?: Record<string, unknown>;
  time_range?: Record<string, unknown>;
  variables?: string[];
  vessel?: Record<string, unknown>;
  route?: Record<string, unknown>;
  constraints?: Record<string, unknown>;
}

export interface TelemetryResponse {
  total_pipeline_ms: number;
  understand_query_ms?: number;
  planner_ms?: number;
  tool_selection_ms?: number;
  executor_ms?: number;
  evidence_assembly_ms?: number;
  response_generation_ms?: number;
  tool_timings_ms?: Record<string, number>;
  llm_used?: boolean;
  llm_fallback?: boolean;
  llm_fallback_reason?: string;
  llm_provider?: string;
  llm_model?: string;
  parser_mode?: string;
  node_latencies_ms?: Record<string, number>;
}

export interface AgentResponseData {
  // Phase 8 Canonical Structured Fields
  message?: string;
  decision?: DecisionSummary;
  zones?: ZoneSummary[];
  evidence?: EvidenceItemResponse[];
  visual_payload?: VisualPayloadData;
  query_context?: QueryContextResponse;
  telemetry?: TelemetryResponse;
  disclaimer?: string;

  // Backward-Compatible & UI Fields
  response_id: string;
  role: RoleType;
  markdown_content: string;
  safety_alert?: SafetyAlertData;
  key_recommendations: string[];
  evidence_summary: string[];
  status: 'success' | 'partial_fallback' | 'error';
  execution_time_seconds?: number;
}

export interface ChatMessageItem {
  id: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  content: string;
  data?: AgentResponseData;
}

export interface QuickPrompt {
  id: string;
  label: string;
  query: string;
  icon?: string;
  category?: 'advisory' | 'safety' | 'monitoring' | 'analytics';
}
