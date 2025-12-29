-- Fynix Bookkeeping Database Schema
-- Created for Supabase PostgreSQL
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS & AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    trade VARCHAR(50) NOT NULL, -- HVAC, Plumbing, Roofing, Electrical, General
    state VARCHAR(2) NOT NULL,
    tier VARCHAR(50) DEFAULT 'essentials', -- essentials, professional, growth, enterprise
    tax_classification VARCHAR(50), -- S-Corp, LLC, Sole Prop
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    stripe_customer_id VARCHAR(255),
    subscription_status VARCHAR(50) DEFAULT 'trial', -- trial, active, past_due, canceled
    trial_ends_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '14 days'
);

-- ============================================================================
-- RECEIPTS
-- ============================================================================

CREATE TABLE receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receipt_number VARCHAR(100),
    vendor VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2),
    subtotal DECIMAL(10, 2),
    payment_method VARCHAR(50),
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,
    confidence DECIMAL(3, 2), -- 0.00 to 1.00
    status VARCHAR(50) DEFAULT 'pending', -- pending, processed, reviewed, approved, rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    notes TEXT
);

CREATE INDEX idx_receipts_user_id ON receipts(user_id);
CREATE INDEX idx_receipts_date ON receipts(date);
CREATE INDEX idx_receipts_vendor ON receipts(vendor);

-- ============================================================================
-- RECEIPT LINE ITEMS
-- ============================================================================

CREATE TABLE receipt_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id UUID NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    quantity DECIMAL(10, 2) DEFAULT 1,
    unit_price DECIMAL(10, 2),
    total DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_receipt_items_receipt_id ON receipt_items(receipt_id);

-- ============================================================================
-- JOBS / PROJECTS
-- ============================================================================

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_number VARCHAR(100) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip VARCHAR(10),
    trade_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'quoted', -- quoted, active, completed, billed, closed
    start_date DATE,
    end_date DATE,
    estimated_material_cost DECIMAL(10, 2),
    estimated_labor_cost DECIMAL(10, 2),
    actual_cost DECIMAL(10, 2) DEFAULT 0,
    scope_keywords TEXT[], -- Array of keywords for matching
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_dates ON jobs(start_date, end_date);

-- ============================================================================
-- TRANSACTIONS (Categorized Expenses)
-- ============================================================================

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receipt_id UUID REFERENCES receipts(id) ON DELETE SET NULL,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    vendor VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    confidence DECIMAL(3, 2),
    auto_approved BOOLEAN DEFAULT FALSE,
    manually_reviewed BOOLEAN DEFAULT FALSE,
    tax_deductible BOOLEAN DEFAULT TRUE,
    tax_flags TEXT[], -- Array of tax-related flags
    payment_method VARCHAR(50),
    external_id VARCHAR(255), -- For bank transaction ID
    source VARCHAR(50) DEFAULT 'receipt', -- receipt, bank, manual, invoice
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_job_id ON transactions(job_id);

-- ============================================================================
-- COMPLIANCE TRACKING
-- ============================================================================

CREATE TABLE compliance_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL, -- license, insurance, tax, permit
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    last_completed DATE,
    renewal_period_months INTEGER DEFAULT 12,
    status VARCHAR(50) DEFAULT 'compliant', -- compliant, warning, overdue, critical
    estimated_cost DECIMAL(10, 2),
    trade_specific VARCHAR(50),
    state_specific VARCHAR(2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_compliance_user_id ON compliance_items(user_id);
CREATE INDEX idx_compliance_due_date ON compliance_items(due_date);
CREATE INDEX idx_compliance_status ON compliance_items(status);

-- ============================================================================
-- REPORTS (Generated Reports)
-- ============================================================================

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL, -- flash, monthly, quarterly, annual, custom
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data JSONB NOT NULL, -- Store report data as JSON
    pdf_url TEXT,
    status VARCHAR(50) DEFAULT 'generated', -- generated, sent, viewed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_period ON reports(period_start, period_end);

-- ============================================================================
-- INTEGRATIONS
-- ============================================================================

CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    integration_type VARCHAR(50) NOT NULL, -- plaid, quickbooks, stripe, etc.
    credentials JSONB, -- Encrypted credentials
    settings JSONB,
    status VARCHAR(50) DEFAULT 'active', -- active, error, disconnected
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_integrations_user_id ON integrations(user_id);

-- ============================================================================
-- ACTIVITY LOG
-- ============================================================================

CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- receipt, job, transaction, etc.
    entity_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_receipts_updated_at BEFORE UPDATE ON receipts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_compliance_items_updated_at BEFORE UPDATE ON compliance_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipt_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY users_policy ON users
    FOR ALL USING (auth.uid() = id);

CREATE POLICY receipts_policy ON receipts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY receipt_items_policy ON receipt_items
    FOR ALL USING (auth.uid() IN (SELECT user_id FROM receipts WHERE id = receipt_id));

CREATE POLICY jobs_policy ON jobs
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY transactions_policy ON transactions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY compliance_items_policy ON compliance_items
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY reports_policy ON reports
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY integrations_policy ON integrations
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY activity_log_policy ON activity_log
    FOR ALL USING (auth.uid() = user_id);

-- ============================================================================
-- SEED DATA (Optional - for testing)
-- ============================================================================

-- Insert a test user (you can remove this in production)
-- Password will be handled by Supabase Auth
-- This is just for database structure testing

COMMENT ON TABLE users IS 'Contractor business owners using the platform';
COMMENT ON TABLE receipts IS 'Uploaded receipt images and extracted data';
COMMENT ON TABLE jobs IS 'Active contractor jobs/projects for expense allocation';
COMMENT ON TABLE transactions IS 'Categorized financial transactions';
COMMENT ON TABLE compliance_items IS 'License, insurance, and regulatory requirements';
