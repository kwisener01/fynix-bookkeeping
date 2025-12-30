'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Camera, CheckCircle, DollarSign, Calendar, Package, TrendingUp, ArrowLeft } from 'lucide-react';
import { getDemoUser } from '@/lib/demo-session';

// Mock result data structure (in production, would fetch from API/state)
interface ResultData {
  receipt_id: string;
  extracted: {
    vendor: string;
    date: string;
    total: number;
    tax: number;
    confidence: number;
    line_items: Array<{ description: string; quantity: number; price: number }>;
    payment_method: string;
  };
  job_suggestions: Array<{
    job_id: string;
    job_number: string;
    job_name: string;
    confidence: number;
    reasons: string[];
  }>;
}

export default function DemoResultPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const receiptId = searchParams.get('id');
  const [demoUser] = useState(getDemoUser());
  const [loading, setLoading] = useState(true);

  // Mock data for demo (in production, would come from API response stored in state/localStorage)
  const [result, setResult] = useState<ResultData | null>(null);

  useEffect(() => {
    if (!demoUser) {
      router.push('/');
      return;
    }

    if (!receiptId) {
      router.push('/demo/capture');
      return;
    }

    // Load actual result from localStorage
    try {
      const storedResult = localStorage.getItem('lastReceiptResult');
      if (storedResult) {
        const apiResponse = JSON.parse(storedResult);

        // Only use if receipt ID matches (to prevent showing old cached data)
        if (apiResponse.receipt_id === receiptId) {
          // Transform API response to match ResultData interface
          setResult({
            receipt_id: apiResponse.receipt_id,
            extracted: {
              vendor: apiResponse.extracted.vendor,
              date: apiResponse.extracted.date,
              total: apiResponse.extracted.total,
              tax: apiResponse.extracted.tax || 0,
              confidence: apiResponse.extracted.confidence,
              line_items: apiResponse.extracted.line_items || [],
              payment_method: apiResponse.extracted.payment_method || 'Unknown',
            },
            job_suggestions: apiResponse.job_suggestions || [],
          });

          // Clear after loading to prevent stale data
          localStorage.removeItem('lastReceiptResult');
        } else {
          console.warn('Receipt ID mismatch - clearing stale data');
          localStorage.removeItem('lastReceiptResult');
        }
      }
    } catch (error) {
      console.error('Error loading receipt result:', error);
    } finally {
      setLoading(false);
    }
  }, [receiptId, demoUser, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Processing receipt...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">No result found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4">
          <button
            onClick={() => router.push('/demo/capture')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Capture
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Receipt Processed</h1>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {/* Success Banner */}
        <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6 rounded flex items-start gap-3">
          <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-green-900">Receipt Extracted Successfully</h3>
            <p className="text-sm text-green-700 mt-1">
              Confidence: {(result.extracted.confidence * 100).toFixed(0)}%
            </p>
          </div>
        </div>

        {/* Extracted Data */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Extracted Data</h2>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <DataField icon={<Package />} label="Vendor" value={result.extracted.vendor} />
            <DataField icon={<Calendar />} label="Date" value={result.extracted.date} />
            <DataField
              icon={<DollarSign />}
              label="Total"
              value={`$${result.extracted.total.toFixed(2)}`}
            />
            <DataField
              icon={<DollarSign />}
              label="Tax"
              value={`$${result.extracted.tax.toFixed(2)}`}
            />
          </div>

          {/* Line Items */}
          {result.extracted.line_items && result.extracted.line_items.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Line Items</h3>
              <div className="space-y-2">
                {result.extracted.line_items.map((item, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center p-3 bg-gray-50 rounded"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{item.description}</p>
                      <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                    </div>
                    <p className="font-semibold text-gray-900">${item.price.toFixed(2)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Job Suggestions */}
        {result.job_suggestions && result.job_suggestions.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              Job Match Suggestions
            </h2>
            <div className="space-y-4">
              {result.job_suggestions.map((job) => (
                <div
                  key={job.job_id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-900">{job.job_name}</h3>
                      <p className="text-sm text-gray-500">{job.job_number}</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        job.confidence > 0.7
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {(job.confidence * 100).toFixed(0)}% match
                    </span>
                  </div>
                  <div className="mt-3">
                    <p className="text-sm text-gray-600 font-medium mb-1">Match reasons:</p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {job.reasons.map((reason, idx) => (
                        <li key={idx} className="flex gap-2">
                          <span>•</span>
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={() => router.push('/demo/capture')}
            className="flex-1 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
          >
            <Camera className="w-5 h-5" />
            Capture Another Receipt
          </button>
        </div>
      </div>
    </div>
  );
}

function DataField({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
      <div className="text-blue-600">{icon}</div>
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
        <p className="font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  );
}
