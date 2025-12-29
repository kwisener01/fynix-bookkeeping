'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Camera, Zap, TrendingUp, CheckCircle } from 'lucide-react';
import { getDemoUser, createDemoUser } from '@/lib/demo-session';

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing demo session
    const existingUser = getDemoUser();
    if (existingUser) {
      router.push('/demo/capture');
    } else {
      setLoading(false);
    }
  }, [router]);

  const startDemo = () => {
    createDemoUser();
    router.push('/demo/capture');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-600 mb-6 shadow-lg">
            <Camera className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Fynix Receipt Capture
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto">
            AI-powered receipt scanning designed for contractors
          </p>
          <p className="text-lg text-gray-500 mt-4">
            Mobile camera → Claude Vision → Job matching → Done
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <FeatureCard
            icon={<Camera className="w-10 h-10" />}
            title="Mobile Camera"
            description="Snap a photo of any receipt with your phone camera - works on any job site"
            color="blue"
          />
          <FeatureCard
            icon={<Zap className="w-10 h-10" />}
            title="AI Extraction"
            description="Claude Vision automatically extracts vendor, date, line items, and totals"
            color="purple"
          />
          <FeatureCard
            icon={<TrendingUp className="w-10 h-10" />}
            title="Job Matching"
            description="Intelligent matching to active jobs using date, vendor, and material keywords"
            color="indigo"
          />
        </div>

        {/* Benefits */}
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12 mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            Why Contractors Love It
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <BenefitItem text="No manual data entry - camera does it all" />
            <BenefitItem text="Works offline - receipts queue automatically" />
            <BenefitItem text="PWA installable - add to home screen" />
            <BenefitItem text="Trade-specific categorization (HVAC, Plumbing, etc.)" />
            <BenefitItem text="Job costing made easy" />
            <BenefitItem text="Bank-ready bookkeeping" />
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <button
            onClick={startDemo}
            className="group px-10 py-5 bg-blue-600 text-white text-xl font-semibold rounded-xl hover:bg-blue-700 shadow-2xl hover:shadow-blue-500/50 transition-all transform hover:scale-105"
          >
            <span className="flex items-center gap-3">
              Try Demo - No Login Required
              <Camera className="w-6 h-6 group-hover:rotate-12 transition-transform" />
            </span>
          </button>
          <p className="text-sm text-gray-500 mt-6">
            Demo session lasts 24 hours • No credit card • No signup
          </p>
        </div>

        {/* Tech Stack Footer */}
        <div className="mt-16 text-center text-sm text-gray-500">
          <p className="font-medium text-gray-700 mb-2">Built with:</p>
          <p>Next.js • Claude Vision • IndexedDB • Service Workers • PWA</p>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    purple: 'bg-purple-100 text-purple-600',
    indigo: 'bg-indigo-100 text-indigo-600',
  };

  return (
    <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
      <div
        className={`inline-flex p-4 rounded-xl mb-4 ${colorClasses[color as keyof typeof colorClasses]}`}
      >
        {icon}
      </div>
      <h3 className="font-bold text-xl mb-3 text-gray-900">{title}</h3>
      <p className="text-gray-600 leading-relaxed">{description}</p>
    </div>
  );
}

function BenefitItem({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-3">
      <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
      <p className="text-gray-700">{text}</p>
    </div>
  );
}
