/**
 * SaaS Dashboard Routes
 *
 * Express routes for a SaaS dashboard with role-based access control.
 * Roles: admin, member, viewer
 */

import { Router, Request, Response, NextFunction } from 'express';

export interface User {
  id: string;
  email: string;
  role: 'admin' | 'member' | 'viewer';
  orgId: string;
}

interface AuthenticatedRequest extends Request {
  user?: User;
}

// Middleware: Verify JWT and attach user
export function authenticate(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  const token = authHeader.slice(7);
  try {
    const user = verifyToken(token); // Throws on invalid/expired token
    req.user = user;
    next();
  } catch {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

// Middleware: Require specific role(s)
export function requireRole(...roles: User['role'][]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        required: roles,
        current: req.user.role,
      });
    }
    next();
  };
}

export function createRouter(): Router {
  const router = Router();

  // All routes require authentication
  router.use(authenticate);

  // Dashboard overview — all roles
  router.get('/dashboard', (req: AuthenticatedRequest, res: Response) => {
    res.json({
      user: { id: req.user!.id, role: req.user!.role },
      stats: getDashboardStats(req.user!.orgId, req.user!.role),
    });
  });

  // Team management — admin only
  router.get('/team', requireRole('admin'), (req: AuthenticatedRequest, res: Response) => {
    const members = getTeamMembers(req.user!.orgId);
    res.json({ members });
  });

  router.post('/team/invite', requireRole('admin'), (req: AuthenticatedRequest, res: Response) => {
    const { email, role } = req.body;
    if (!email || !role) {
      return res.status(400).json({ error: 'Email and role are required' });
    }
    if (!['member', 'viewer'].includes(role)) {
      return res.status(400).json({ error: 'Can only invite members or viewers' });
    }
    const invitation = inviteTeamMember(req.user!.orgId, email, role);
    res.status(201).json(invitation);
  });

  router.delete('/team/:memberId', requireRole('admin'), (req: AuthenticatedRequest, res: Response) => {
    const { memberId } = req.params;
    if (memberId === req.user!.id) {
      return res.status(400).json({ error: 'Cannot remove yourself' });
    }
    removeTeamMember(req.user!.orgId, memberId);
    res.status(204).send();
  });

  // Reports — admin and member
  router.get('/reports', requireRole('admin', 'member'), (req: AuthenticatedRequest, res: Response) => {
    const reports = getReports(req.user!.orgId);
    res.json({ reports });
  });

  router.post('/reports', requireRole('admin', 'member'), (req: AuthenticatedRequest, res: Response) => {
    const { title, type } = req.body;
    if (!title || !type) {
      return res.status(400).json({ error: 'Title and type are required' });
    }
    const report = createReport(req.user!.orgId, req.user!.id, title, type);
    res.status(201).json(report);
  });

  // Settings — admin only
  router.get('/settings', requireRole('admin'), (req: AuthenticatedRequest, res: Response) => {
    const settings = getOrgSettings(req.user!.orgId);
    res.json(settings);
  });

  router.patch('/settings', requireRole('admin'), (req: AuthenticatedRequest, res: Response) => {
    const updated = updateOrgSettings(req.user!.orgId, req.body);
    res.json(updated);
  });

  // Billing — admin only
  router.get('/billing', requireRole('admin'), (req: AuthenticatedRequest, res: Response) => {
    const billing = getBillingInfo(req.user!.orgId);
    res.json(billing);
  });

  return router;
}

// Stub implementations (would be real service calls in production)
function verifyToken(_token: string): User {
  throw new Error('Token verification not implemented');
}

function getDashboardStats(_orgId: string, _role: string) {
  return { projects: 5, tasks: 42, members: 3 };
}

function getTeamMembers(_orgId: string) {
  return [];
}

function inviteTeamMember(_orgId: string, _email: string, _role: string) {
  return { id: 'inv-1', email: _email, role: _role, status: 'pending' };
}

function removeTeamMember(_orgId: string, _memberId: string) {}

function getReports(_orgId: string) {
  return [];
}

function createReport(_orgId: string, _userId: string, _title: string, _type: string) {
  return { id: 'report-1', title: _title, type: _type };
}

function getOrgSettings(_orgId: string) {
  return { name: 'Acme Corp', plan: 'pro' };
}

function updateOrgSettings(_orgId: string, _updates: any) {
  return { ..._updates };
}

function getBillingInfo(_orgId: string) {
  return { plan: 'pro', nextBilling: '2024-02-01' };
}
