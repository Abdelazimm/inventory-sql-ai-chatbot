export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  metadata?: ChatMetadata;
}

export interface ChatMetadata {
  intent?: string;
  generated_sql?: string;
  is_valid_sql?: boolean;
  retry_count?: number;
  execution_time_ms?: number;
  row_count?: number;
  model?: string;
}

export interface ChatSession {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  user_id: number;
  username: string;
  role: 'viewer' | 'manager' | 'admin';
  full_name?: string;
}

export interface IngestPreview {
  entity_type: string;
  total_rows: number;
  columns_found: string[];
  missing_required_columns: string[];
  is_valid: boolean;
  preview: Record<string, any>[];
}

export interface MutationPreview {
  action_id: string;
  action: string;
  entity_type: string;
  entity_id?: string | number;
  fields: Record<string, any>;
  summary: string;
  expires_at: string;
}
