// Fynix Frontend TypeScript Types

export interface User {
  id: string;
  email: string;
  business_name: string;
  trade: 'HVAC' | 'Plumbing' | 'Roofing' | 'Electrical' | 'General';
  state: string;
  tier: 'essentials' | 'professional' | 'growth' | 'enterprise';
  created_at: string;
  subscription_status: 'trial' | 'active' | 'past_due' | 'canceled';
  trial_ends_at?: string;
}

export interface Receipt {
  id: string;
  user_id: string;
  vendor: string;
  date: string;
  total: number;
  tax?: number;
  subtotal?: number;
  payment_method?: string;
  image_url: string;
  thumbnail_url?: string;
  confidence?: number;
  status: 'pending' | 'processed' | 'reviewed' | 'approved' | 'rejected';
  receipt_number?: string;
  line_items?: LineItem[];
  created_at: string;
  notes?: string;
}

export interface LineItem {
  id?: string;
  description: string;
  quantity: number;
  unit_price?: number;
  total: number;
  category?: string;
  subcategory?: string;
}

export interface Job {
  id: string;
  user_id: string;
  job_number: string;
  customer_name: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  trade_type: string;
  status: 'quoted' | 'active' | 'completed' | 'billed' | 'closed';
  start_date?: string;
  end_date?: string;
  estimated_material_cost?: number;
  estimated_labor_cost?: number;
  actual_cost?: number;
  scope_keywords?: string[];
  created_at: string;
  notes?: string;
}

export interface JobMatch {
  job_id: string;
  job_number: string;
  job_name: string;
  confidence: number;
  reasons: string[];
}

export interface Transaction {
  id: string;
  user_id: string;
  receipt_id?: string;
  job_id?: string;
  date: string;
  description: string;
  vendor?: string;
  amount: number;
  category: string;
  subcategory?: string;
  confidence?: number;
  auto_approved: boolean;
  manually_reviewed: boolean;
  tax_deductible: boolean;
  payment_method?: string;
  source: 'receipt' | 'bank' | 'manual' | 'invoice';
  created_at: string;
  notes?: string;
}

export interface ComplianceItem {
  id: string;
  user_id: string;
  item_type: 'license' | 'insurance' | 'tax' | 'permit';
  name: string;
  description?: string;
  due_date?: string;
  last_completed?: string;
  status: 'compliant' | 'warning' | 'overdue' | 'critical';
  estimated_cost?: number;
  created_at: string;
  notes?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface ReceiptUploadResponse {
  receipt_id: string;
  extracted: {
    vendor: string;
    date: string;
    total: number;
    tax?: number;
    confidence: number;
    line_items: LineItem[];
    payment_method?: string;
    receipt_number?: string;
  };
  job_suggestions: JobMatch[];
  status: string;
}

export interface DashboardStats {
  total_receipts: number;
  this_week_receipts: number;
  total_spent: number;
  this_week_spent: number;
  pending_reviews: number;
  active_jobs: number;
  compliance_alerts: number;
}
