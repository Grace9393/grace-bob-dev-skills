CREATE TABLE IF NOT EXISTS project (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL UNIQUE,
  profile TEXT NOT NULL,
  name TEXT NOT NULL,
  root_path TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS work_item (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  parent_work_item_id TEXT REFERENCES work_item(id) ON DELETE SET NULL,
  work_item_key TEXT NOT NULL,
  item_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  tag TEXT,
  phase TEXT,
  status TEXT NOT NULL DEFAULT 'not_started',
  validity_status TEXT NOT NULL DEFAULT 'current',
  priority INTEGER NOT NULL DEFAULT 3,
  owner TEXT,
  due_at TEXT,
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  completed_at TEXT,
  supersedes_work_item_id TEXT REFERENCES work_item(id) ON DELETE SET NULL,
  UNIQUE(project_id, label),
  UNIQUE(project_id, work_item_key),
  CHECK (status IN ('not_started','ready','in_progress','blocked','needs_review','complete','cancelled')),
  CHECK (validity_status IN ('current','needs_review','outdated','blocked_until_refreshed','superseded'))
);

CREATE TABLE IF NOT EXISTS work_dependency (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  upstream_work_item_id TEXT NOT NULL REFERENCES work_item(id) ON DELETE CASCADE,
  downstream_work_item_id TEXT NOT NULL REFERENCES work_item(id) ON DELETE CASCADE,
  invalidation_policy TEXT NOT NULL DEFAULT 'mark_needs_review',
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, upstream_work_item_id, downstream_work_item_id),
  CHECK (upstream_work_item_id != downstream_work_item_id),
  CHECK (invalidation_policy IN ('none','mark_needs_review','mark_outdated','block_until_refreshed'))
);

CREATE TABLE IF NOT EXISTS source_asset (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  asset_key TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  current_version_id TEXT,
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, label),
  UNIQUE(project_id, asset_key)
);

CREATE TABLE IF NOT EXISTS source_asset_version (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  source_asset_id TEXT NOT NULL REFERENCES source_asset(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  version_label TEXT NOT NULL,
  path TEXT NOT NULL,
  sha256 TEXT,
  change_note TEXT,
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, label),
  UNIQUE(source_asset_id, version_number),
  UNIQUE(source_asset_id, version_label)
);

CREATE TABLE IF NOT EXISTS artifact (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  artifact_key TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  title TEXT NOT NULL,
  path TEXT,
  owner_work_item_id TEXT NOT NULL REFERENCES work_item(id) ON DELETE RESTRICT,
  current_version_id TEXT,
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, label),
  UNIQUE(project_id, artifact_key)
);

CREATE TABLE IF NOT EXISTS artifact_version (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  artifact_id TEXT NOT NULL REFERENCES artifact(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  path TEXT NOT NULL,
  sha256 TEXT,
  summary TEXT,
  created_by TEXT,
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, label),
  UNIQUE(artifact_id, version_number)
);

CREATE TABLE IF NOT EXISTS artifact_source (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  artifact_version_id TEXT NOT NULL REFERENCES artifact_version(id) ON DELETE CASCADE,
  source_asset_version_id TEXT NOT NULL REFERENCES source_asset_version(id) ON DELETE CASCADE,
  relevance TEXT,
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(artifact_version_id, source_asset_version_id)
);

CREATE TABLE IF NOT EXISTS impact (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  source_asset_version_id TEXT REFERENCES source_asset_version(id) ON DELETE CASCADE,
  work_item_id TEXT REFERENCES work_item(id) ON DELETE CASCADE,
  artifact_id TEXT REFERENCES artifact(id) ON DELETE CASCADE,
  impact_type TEXT NOT NULL,
  invalidation_policy TEXT NOT NULL DEFAULT 'mark_needs_review',
  confidence TEXT NOT NULL DEFAULT 'medium',
  status TEXT NOT NULL DEFAULT 'proposed',
  rationale TEXT,
  reviewed_by TEXT,
  reviewed_at TEXT,
  review_note TEXT,
  row_version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, label),
  CHECK (work_item_id IS NOT NULL OR artifact_id IS NOT NULL),
  CHECK (confidence IN ('low','medium','high')),
  CHECK (status IN ('proposed','approved','rejected','applied')),
  CHECK (invalidation_policy IN ('none','mark_needs_review','mark_outdated','block_until_refreshed'))
);

CREATE TABLE IF NOT EXISTS work_item_claim (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  work_item_id TEXT NOT NULL REFERENCES work_item(id) ON DELETE CASCADE,
  agent_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  claimed_at TEXT NOT NULL,
  heartbeat_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  released_at TEXT,
  release_reason TEXT,
  row_version INTEGER NOT NULL DEFAULT 1,
  CHECK (status IN ('active','released','expired'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_work_item_claim_one_active
ON work_item_claim(work_item_id)
WHERE status = 'active';

CREATE TABLE IF NOT EXISTS event_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id TEXT REFERENCES project(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  agent_id TEXT,
  detail_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS render_state (
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  output_path TEXT NOT NULL,
  rendered_from_event_id INTEGER REFERENCES event_log(id),
  rendered_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  row_version INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (project_id, output_path)
);
