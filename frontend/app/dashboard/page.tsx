'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Receipt,
  Briefcase,
  TrendingUp,
  AlertTriangle,
  DollarSign,
  Calendar
} from 'lucide-react';
import ReceiptUpload from '@/components/ReceiptUpload';
import { db, auth } from '@/lib/supabase';
import type { DashboardStats, User } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      // Get authenticated user
      const { data: { user: authUser }, error: authError } = await auth.getUser();

      if (authError || !authUser) {
        router.push('/login');
        return;
      }

      // Get user profile
      const { data: profile } = await db.getUserProfile(authUser.id);
      if (profile) {
        setUser(profile);
      }

      // Get dashboard stats
      const { data: receipts } = await db.getReceipts(authUser.id);
      const { data: jobs } = await db.getJobs(authUser.id);
      const { data: transactions } = await db.getTransactions(authUser.id);

      // Calculate stats
      const now = new Date();
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

      const thisWeekReceipts = receipts?.filter(
        r => new Date(r.created_at) >= weekAgo
      ) || [];

      const thisWeekSpent = thisWeekReceipts.reduce(
        (sum, r) => sum + (r.total || 0), 0
      );

      const totalSpent = receipts?.reduce(
        (sum, r) => sum + (r.total || 0), 0
      ) || 0;

      const activeJobs = jobs?.filter(
        j => j.status === 'active' || j.status === 'quoted'
      ).length || 0;

      const pendingReviews = receipts?.filter(
        r => r.status === 'pending' || r.status === 'processed'
      ).length || 0;

      setStats({
        total_receipts: receipts?.length || 0,
        this_week_receipts: thisWeekReceipts.length,
        total_spent: totalSpent,
        this_week_spent: thisWeekSpent,
        pending_reviews: pendingReviews,
        active_jobs: activeJobs,
        compliance_alerts: 0, // TODO: Implement compliance alerts
      });
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {user?.business_name || 'Dashboard'}
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                {user?.trade} • {user?.tier} Plan
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => router.push('/receipts')}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                View All Receipts
              </button>
              <button
                onClick={() => router.push('/jobs')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Manage Jobs
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Receipt className="w-6 h-6" />}
            label="Total Receipts"
            value={stats?.total_receipts || 0}
            subtext={`${stats?.this_week_receipts || 0} this week`}
            color="blue"
          />
          <StatCard
            icon={<DollarSign className="w-6 h-6" />}
            label="Total Spent"
            value={`$${(stats?.total_spent || 0).toLocaleString()}`}
            subtext={`$${(stats?.this_week_spent || 0).toLocaleString()} this week`}
            color="green"
          />
          <StatCard
            icon={<Briefcase className="w-6 h-6" />}
            label="Active Jobs"
            value={stats?.active_jobs || 0}
            subtext="Projects in progress"
            color="purple"
          />
          <StatCard
            icon={<AlertTriangle className="w-6 h-6" />}
            label="Pending Reviews"
            value={stats?.pending_reviews || 0}
            subtext="Receipts to review"
            color="orange"
          />
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Upload Receipt</h2>
          <ReceiptUpload
            clientId={user?.id || ''}
            onSuccess={() => {
              loadDashboard(); // Reload stats after upload
            }}
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <QuickActionCard
            icon={<Calendar className="w-8 h-8" />}
            title="Compliance Calendar"
            description="View upcoming deadlines and renewals"
            onClick={() => router.push('/compliance')}
          />
          <QuickActionCard
            icon={<TrendingUp className="w-8 h-8" />}
            title="Flash Report"
            description="This week's financial summary"
            onClick={() => router.push('/reports')}
          />
          <QuickActionCard
            icon={<Briefcase className="w-8 h-8" />}
            title="Job Profitability"
            description="See which jobs are most profitable"
            onClick={() => router.push('/jobs')}
          />
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, subtext, color }: any) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className={`inline-flex p-3 rounded-lg ${colors[color as keyof typeof colors]}`}>
        {icon}
      </div>
      <div className="mt-4">
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        <p className="text-xs text-gray-500 mt-1">{subtext}</p>
      </div>
    </div>
  );
}

function QuickActionCard({ icon, title, description, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className="bg-white rounded-lg shadow p-6 text-left hover:shadow-lg transition-shadow"
    >
      <div className="text-blue-600 mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-500">{description}</p>
    </button>
  );
}
