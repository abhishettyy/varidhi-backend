import { RoleType, SafetySeverity } from './marine';

export interface SafetyAlertData {
  severity: SafetySeverity;
  title: string;
  description: string;
  action_advice: string;
  issued_at?: string;
}

export interface VisualPayloadData {
  map_features_geojson?: Record<string, unknown>;
  charts_data?: Array<Record<string, unknown>>;
  metric_badges?: Record<string, string>;
  focus_zone_id?: string;
  highlight_layer?: string;
}

export interface AgentResponseData {
  response_id: string;
  role: RoleType;
  markdown_content: string;
  safety_alert?: SafetyAlertData;
  key_recommendations: string[];
  evidence_summary: string[];
  visual_payload?: VisualPayloadData;
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
