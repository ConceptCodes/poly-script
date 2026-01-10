export interface UsageResponse {
  plan: string;
  monthly_upload_count: number;
  monthly_limit: number | "inf";
  extra_credits: number;
}

export interface SubscriptionResponse {
  status: string;
  cancel_at_period_end: boolean;
  current_period_start?: string;
  current_period_end?: string;
  plan_id?: string;
}

export interface CheckoutResponse {
  checkout_url: string;
}

export interface PortalResponse {
  url: string;
}

export interface StatsResponse {
  total_uploads: number;
  total_transcriptions: number;
  total_translations: number;
  monthly_usage: number;
}

export interface Job {
  id: string;
  status: string;
  created_at: string;
  updated_at: string;
  type: string;
  progress?: number;
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
}

export interface PricingPlan {
  plan: string;
  limits: {
    uploads_per_month: number | "inf";
    languages: number | "inf";
    members: number | "inf";
  };
}

export interface PricingData {
  credit_price?: number;
  plans: PricingPlan[] | {
    FREE: { price: number; limit: number };
    STANDARD: { price: number; limit: number };
    PRO: { price: number; limit: number };
  };
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: "owner" | "admin" | "member";
  language?: string;
  email_notifications?: boolean;
  in_app_notifications?: boolean;
  created_at: string;
}

export interface TeamMember {
  id: string;
  email: string;
  name: string;
  role: "owner" | "admin" | "member";
  joined_at: string;
}

export interface Team {
  id: string;
  name: string;
  default_language: string;
  created_at: string;
  members: TeamMember[];
}
