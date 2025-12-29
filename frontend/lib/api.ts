// API client for Fynix backend

import { offlineDB } from './offline-db';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiRequestOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
}

async function apiRequest<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_URL}${endpoint}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || 'Request failed');
  }

  return response.json();
}

export const api = {
  // Receipt upload with offline support
  uploadReceipt: async (file: File, clientId: string) => {
    // Check if online
    if (!navigator.onLine) {
      console.log('Offline: queuing receipt for later upload');

      // Queue for later
      const receiptId = `receipt_${Date.now()}`;
      const blob = new Blob([await file.arrayBuffer()], { type: file.type });

      await offlineDB.addReceipt({
        id: receiptId,
        file: blob,
        clientId,
        timestamp: Date.now(),
        retryCount: 0,
      });

      throw new Error('Offline - receipt queued for upload when connection is restored');
    }

    // Online: upload normally
    const formData = new FormData();
    formData.append('file', file);
    formData.append('client_id', clientId);

    try {
      const response = await fetch(`${API_URL}/api/receipts/capture`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || 'Failed to upload receipt');
      }

      return response.json();
    } catch (error) {
      // If network error while supposedly online, queue for retry
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.log('Network error: queuing receipt for retry');

        const receiptId = `receipt_${Date.now()}`;
        const blob = new Blob([await file.arrayBuffer()], { type: file.type });

        await offlineDB.addReceipt({
          id: receiptId,
          file: blob,
          clientId,
          timestamp: Date.now(),
          retryCount: 0,
        });

        throw new Error('Network error - receipt queued for upload');
      }

      throw error;
    }
  },

  // Client onboarding
  onboardClient: async (data: {
    email: string;
    business_name: string;
    trade: string;
    state: string;
    tier: string;
  }) => {
    return apiRequest('/clients/onboard', {
      method: 'POST',
      body: data,
    });
  },

  // Get client status
  getClientStatus: async (clientId: string) => {
    return apiRequest(`/clients/${clientId}/status`);
  },

  // Generate reports
  generateReport: async (data: {
    client_id: string;
    report_type: string;
    period_start: string;
    period_end: string;
  }) => {
    return apiRequest('/reports/generate', {
      method: 'POST',
      body: data,
    });
  },

  // Get flash report
  getFlashReport: async (clientId: string) => {
    return apiRequest(`/reports/${clientId}/flash`);
  },

  // Get compliance status
  getComplianceStatus: async (clientId: string) => {
    return apiRequest(`/compliance/${clientId}/status`);
  },

  // Get compliance calendar
  getComplianceCalendar: async (clientId: string) => {
    return apiRequest(`/compliance/${clientId}/calendar`);
  },

  // Process invoice
  processInvoice: async (data: {
    client_id: string;
    invoice_url: string;
  }) => {
    return apiRequest('/invoices/process', {
      method: 'POST',
      body: data,
    });
  },

  // Process transactions
  processTransactions: async (data: {
    client_id: string;
    transactions: any[];
    source: string;
  }) => {
    return apiRequest('/transactions/process', {
      method: 'POST',
      body: data,
    });
  },
};
