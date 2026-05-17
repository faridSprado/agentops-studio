export type Project = {
  id: string;
  name: string;
  brand_voice: string;
  audience: string;
  constraints: string;
  created_at: string;
  updated_at: string;
};

export type Campaign = {
  id: string;
  project_id: string;
  brief: string;
  channels: string[];
  language: string;
  tone: string;
  human_review: boolean;
  feedback: string;
  status: string;
  output: CampaignOutput | null;
  score: number | null;
  error: string;
  created_at: string;
  updated_at: string;
};

export type AgentEvent = {
  id?: string;
  campaign_id?: string;
  sequence?: number;
  agent: string;
  status: string;
  payload?: Record<string, unknown>;
  created_at?: string;
  score?: number;
};

export type AgentSection = {
  title?: string;
  summary?: string;
  items?: string[];
  data?: Record<string, unknown>;
};

export type ExecutiveItem = {
  label: string;
  title: string;
  summary: string;
  items: string[];
};

export type CampaignOutput = {
  title: string;
  summary: string;
  brief: string;
  channels: string[];
  score: number;
  score_breakdown?: Record<string, number | string>;
  score_rationale?: Record<string, string>;
  revisions: number;
  provider?: string;
  mock_mode?: boolean;
  executive?: ExecutiveItem[];
  sections: Record<string, AgentSection>;
};

export type CampaignRequest = {
  project: {
    name: string;
    brand_voice: string;
    audience: string;
    constraints: string;
  };
  campaign: {
    brief: string;
    channels: string[];
    language: string;
    tone: string;
    human_review: boolean;
  };
};

export type Health = {
  status: string;
  env: string;
  provider: string;
  mock_mode: boolean;
  llm_enabled: boolean;
  database: string;
  version?: string;
  app?: string;
};
