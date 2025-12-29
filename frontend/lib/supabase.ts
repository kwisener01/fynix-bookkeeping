import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Auth helpers
export const auth = {
  signUp: async (email: string, password: string, metadata: any) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata,
      },
    });
    return { data, error };
  },

  signIn: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    return { data, error };
  },

  signOut: async () => {
    const { error } = await supabase.auth.signOut();
    return { error };
  },

  getSession: async () => {
    const { data, error } = await supabase.auth.getSession();
    return { data, error };
  },

  getUser: async () => {
    const { data, error } = await supabase.auth.getUser();
    return { data, error };
  },
};

// Database helpers
export const db = {
  // Receipts
  getReceipts: async (userId: string) => {
    const { data, error } = await supabase
      .from('receipts')
      .select('*, receipt_items(*)')
      .eq('user_id', userId)
      .order('date', { ascending: false });
    return { data, error };
  },

  getReceipt: async (id: string) => {
    const { data, error } = await supabase
      .from('receipts')
      .select('*, receipt_items(*)')
      .eq('id', id)
      .single();
    return { data, error };
  },

  // Jobs
  getJobs: async (userId: string) => {
    const { data, error } = await supabase
      .from('jobs')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
    return { data, error };
  },

  getActiveJobs: async (userId: string) => {
    const { data, error } = await supabase
      .from('jobs')
      .select('*')
      .eq('user_id', userId)
      .in('status', ['quoted', 'active'])
      .order('start_date', { ascending: false });
    return { data, error };
  },

  // Transactions
  getTransactions: async (userId: string) => {
    const { data, error } = await supabase
      .from('transactions')
      .select('*')
      .eq('user_id', userId)
      .order('date', { ascending: false });
    return { data, error };
  },

  // Compliance
  getComplianceItems: async (userId: string) => {
    const { data, error } = await supabase
      .from('compliance_items')
      .select('*')
      .eq('user_id', userId)
      .order('due_date', { ascending: true });
    return { data, error };
  },

  // User profile
  getUserProfile: async (userId: string) => {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .single();
    return { data, error };
  },

  updateUserProfile: async (userId: string, updates: any) => {
    const { data, error } = await supabase
      .from('users')
      .update(updates)
      .eq('id', userId);
    return { data, error };
  },
};
