const DEMO_USER_KEY = 'fynix_demo_user';
const DEMO_SESSION_DURATION = 24 * 60 * 60 * 1000; // 24 hours

export interface DemoUser {
  id: string;
  sessionId: string;
  createdAt: number;
  expiresAt: number;
  business_name?: string;
  trade?: string;
}

export function getDemoUser(): DemoUser | null {
  if (typeof window === 'undefined') return null;

  try {
    const stored = localStorage.getItem(DEMO_USER_KEY);
    if (!stored) return null;

    const user: DemoUser = JSON.parse(stored);

    // Check if expired
    if (Date.now() > user.expiresAt) {
      console.log('Demo session expired');
      localStorage.removeItem(DEMO_USER_KEY);
      return null;
    }

    return user;
  } catch (error) {
    console.error('Error reading demo user:', error);
    return null;
  }
}

export function createDemoUser(businessName?: string, trade?: string): DemoUser {
  const now = Date.now();
  const user: DemoUser = {
    id: `demo_${now}`,
    sessionId: `session_${Math.random().toString(36).substr(2, 9)}`,
    createdAt: now,
    expiresAt: now + DEMO_SESSION_DURATION,
    business_name: businessName || 'Demo Business',
    trade: trade || 'General',
  };

  localStorage.setItem(DEMO_USER_KEY, JSON.stringify(user));
  console.log('Demo session created:', user.id);
  return user;
}

export function clearDemoUser(): void {
  localStorage.removeItem(DEMO_USER_KEY);
  console.log('Demo session cleared');
}

export function updateDemoUser(updates: Partial<DemoUser>): DemoUser | null {
  const user = getDemoUser();
  if (!user) return null;

  const updatedUser = { ...user, ...updates };
  localStorage.setItem(DEMO_USER_KEY, JSON.stringify(updatedUser));
  return updatedUser;
}

export function getTimeRemaining(): string {
  const user = getDemoUser();
  if (!user) return '0 hours';

  const remaining = user.expiresAt - Date.now();
  const hours = Math.floor(remaining / (60 * 60 * 1000));
  const minutes = Math.floor((remaining % (60 * 60 * 1000)) / (60 * 1000));

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}
