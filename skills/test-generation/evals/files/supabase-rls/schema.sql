-- Supabase Multi-Tenant Schema with Row Level Security
-- Tables for a project management SaaS with team-based tenancy

-- Organizations (tenants)
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  plan TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Users belong to organizations via memberships
CREATE TABLE memberships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(user_id, org_id)
);

-- Projects belong to organizations
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  is_archived BOOLEAN NOT NULL DEFAULT false,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tasks belong to projects
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'review', 'done')),
  assignee_id UUID REFERENCES auth.users(id),
  priority INT NOT NULL DEFAULT 0 CHECK (priority BETWEEN 0 AND 3),
  due_date DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS on all tenant-scoped tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Helper function: get org IDs the current user belongs to
CREATE OR REPLACE FUNCTION user_org_ids()
RETURNS SETOF UUID AS $$
  SELECT org_id FROM memberships WHERE user_id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- Helper function: get user's role in an org
CREATE OR REPLACE FUNCTION user_role_in_org(target_org_id UUID)
RETURNS TEXT AS $$
  SELECT role FROM memberships
  WHERE user_id = auth.uid() AND org_id = target_org_id
  LIMIT 1
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- RLS Policies

-- Organizations: users can see orgs they belong to
CREATE POLICY "Users can view their organizations"
  ON organizations FOR SELECT
  USING (id IN (SELECT user_org_ids()));

-- Memberships: users can see memberships in their orgs
CREATE POLICY "Users can view memberships in their orgs"
  ON memberships FOR SELECT
  USING (org_id IN (SELECT user_org_ids()));

-- Only owners/admins can invite (insert memberships)
CREATE POLICY "Admins can add members"
  ON memberships FOR INSERT
  WITH CHECK (
    user_role_in_org(org_id) IN ('owner', 'admin')
  );

-- Only owners can remove members
CREATE POLICY "Owners can remove members"
  ON memberships FOR DELETE
  USING (user_role_in_org(org_id) = 'owner');

-- Projects: visible to org members
CREATE POLICY "Org members can view projects"
  ON projects FOR SELECT
  USING (org_id IN (SELECT user_org_ids()));

-- Only admins+ can create projects
CREATE POLICY "Admins can create projects"
  ON projects FOR INSERT
  WITH CHECK (
    user_role_in_org(org_id) IN ('owner', 'admin')
  );

-- Only admins+ can update projects
CREATE POLICY "Admins can update projects"
  ON projects FOR UPDATE
  USING (user_role_in_org(org_id) IN ('owner', 'admin'));

-- Tasks: visible if user has access to the project's org
CREATE POLICY "Org members can view tasks"
  ON tasks FOR SELECT
  USING (
    project_id IN (
      SELECT id FROM projects WHERE org_id IN (SELECT user_org_ids())
    )
  );

-- Members+ can create and update tasks
CREATE POLICY "Members can manage tasks"
  ON tasks FOR INSERT
  WITH CHECK (
    project_id IN (
      SELECT id FROM projects
      WHERE org_id IN (
        SELECT org_id FROM memberships
        WHERE user_id = auth.uid() AND role IN ('owner', 'admin', 'member')
      )
    )
  );

CREATE POLICY "Members can update tasks"
  ON tasks FOR UPDATE
  USING (
    project_id IN (
      SELECT id FROM projects
      WHERE org_id IN (
        SELECT org_id FROM memberships
        WHERE user_id = auth.uid() AND role IN ('owner', 'admin', 'member')
      )
    )
  );
