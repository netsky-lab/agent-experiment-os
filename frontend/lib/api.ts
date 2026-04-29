export type ExperimentItem = {
  id: string;
  title: string;
  hypothesis: string;
  status: string;
  condition_count: number;
  result_count: number;
};

export type ReviewItem = {
  id: string;
  type: string;
  title: string;
  status: string;
  summary: string;
};

export type WikiNode = { id: string; type: string; title: string; status: string };

export type ContractSurface = {
  id: string;
  endpoint: string;
  purpose: string;
};

export type ChurnRun = {
  matrix_id: string;
  condition_id: string;
  run_id: string;
  review_signals: {
    test_failure_count: number;
    forbidden_edit_count: number;
    wrong_file_edits: number;
  };
};

export type DashboardData = {
  contract: {
    version: string;
    surfaces: ContractSurface[];
  };
  experiments: ExperimentItem[];
  review_queue: ReviewItem[];
  policy_candidate_categories: Array<{ id: string; count: number }>;
  stale_knowledge: Array<{
    page: { id: string; title: string };
    freshness: { allowed_use?: string | null };
  }>;
  duplicate_knowledge: Array<{
    type: string;
    fingerprint: string;
    pages: Array<{ id: string }>;
  }>;
  agent_contract: {
    brief_id: string | null;
    task: string;
    repo?: string | null;
    libraries?: string[];
    must_load: string[];
    recommended: string[];
    dependsOn: Array<{ source: string; target: string; type: string }>;
    decision_rules: string[];
    recommended_checks: string[];
    evidence_pages: string[];
  };
  story?: {
    experiment: { id: string; title: string; hypothesis: string; status: string };
    latest_matrix: { matrix_id: string; run_count: number } | null;
    latest_regression: { status: string } | null;
    latest_churn_runs: ChurnRun[];
    policy_candidate_categories: Array<{ id: string; count: number }>;
  };
};

export type GraphData = {
  nodes: WikiNode[];
  edges: Array<{ source: string; target: string; type: string }>;
};

const apiBase = process.env.NEXT_PUBLIC_EXPERIMENT_OS_API_URL;
const apiKey = process.env.NEXT_PUBLIC_EXPERIMENT_OS_API_KEY;

export async function fetchDashboardData(): Promise<DashboardData> {
  if (!apiBase) throw new Error("NEXT_PUBLIC_EXPERIMENT_OS_API_URL is not configured");
  const response = await fetch(`${apiBase}/ui/bootstrap`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Dashboard bootstrap failed: ${response.status}`);
  return response.json() as Promise<DashboardData>;
}

export async function fetchGraphData(): Promise<GraphData> {
  if (!apiBase) throw new Error("NEXT_PUBLIC_EXPERIMENT_OS_API_URL is not configured");
  const response = await fetch(`${apiBase}/wiki/graph`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Wiki graph failed: ${response.status}`);
  return response.json() as Promise<GraphData>;
}

export async function updateReviewStatus(
  pageId: string,
  status: "accepted" | "rejected" | "deprecated",
  rationale: string,
  evidenceIds: string[],
) {
  if (!apiBase) throw new Error("NEXT_PUBLIC_EXPERIMENT_OS_API_URL is not configured");
  const response = await fetch(`${apiBase}/review-actions/${encodeURIComponent(pageId)}/status`, {
    method: "POST",
    headers: writeHeaders(),
    body: JSON.stringify({
      status,
      rationale,
      reviewer: "dashboard",
      evidence_ids: evidenceIds,
    }),
  });
  if (!response.ok) throw new Error(`Review update failed: ${response.status}`);
  return response.json();
}

export async function ingestIssueEvidence(repo: string, query: string, limit: number) {
  if (!apiBase) throw new Error("NEXT_PUBLIC_EXPERIMENT_OS_API_URL is not configured");
  const response = await fetch(`${apiBase}/issue-knowledge/ingest`, {
    method: "POST",
    headers: writeHeaders(),
    body: JSON.stringify({ repo, query, limit }),
  });
  if (!response.ok) throw new Error(`Issue ingestion failed: ${response.status}`);
  return response.json() as Promise<{
    repo: string;
    query: string;
    issues: number;
    pages: number;
    claims: number;
    knowledge_card: string | null;
    allowed_use: string;
  }>;
}

export async function checkVersionAlignment(pageId: string, localVersions: Record<string, string>) {
  if (!apiBase) throw new Error("NEXT_PUBLIC_EXPERIMENT_OS_API_URL is not configured");
  const response = await fetch(`${apiBase}/issue-knowledge/${encodeURIComponent(pageId)}/version-alignment`, {
    method: "POST",
    headers: writeHeaders(),
    body: JSON.stringify({ local_versions: localVersions }),
  });
  if (!response.ok) throw new Error(`Version alignment failed: ${response.status}`);
  return response.json() as Promise<{
    status: string;
    matches: Array<{ package: string; issue_version: string; local_version: string }>;
    mismatches: Array<{ package: string; issue_version: string; local_version: string }>;
    allowed_use?: string | null;
  }>;
}

export async function promoteClaim(claimId: string, kind: "knowledge" | "policy" | "intervention") {
  if (!apiBase) throw new Error("NEXT_PUBLIC_EXPERIMENT_OS_API_URL is not configured");
  const response = await fetch(`${apiBase}/claims/${encodeURIComponent(claimId)}/promote/${kind}`, {
    method: "POST",
    headers: writeHeaders(),
    body: JSON.stringify({
      title: null,
      applies_to: { evidence_type: "github_issue" },
      mitigates: ["failure.stale-api-drift"],
    }),
  });
  if (!response.ok) throw new Error(`Promotion failed: ${response.status}`);
  return response.json() as Promise<{ id: string; type: string; status: string; title: string }>;
}

export const fallbackData: DashboardData = {
  contract: {
    version: "ui_contract.v1",
    surfaces: [
      {
        id: "AgentContract",
        endpoint: "GET /briefs/{brief_id}/agent-work-context",
        purpose: "Show must-load knowledge, dependsOn edges, decision rules, and evidence boundaries.",
      },
      {
        id: "MatrixRegression",
        endpoint: "GET /experiments/{experiment_id}/matrix/regression",
        purpose: "Detect regressions in clean pass, churn, forbidden edits, and protocol compliance.",
      },
      {
        id: "KnowledgeHealth",
        endpoint: "GET /knowledge/stale and GET /knowledge/duplicates",
        purpose: "Find stale or duplicate knowledge before it becomes an agent decision rule.",
      },
    ],
  },
  experiments: [
    {
      id: "experiment.002-python-api-drift",
      title: "Python API drift with misleading issue evidence",
      hypothesis: "Issue evidence should not become action until local API shape is verified.",
      status: "interpreted",
      condition_count: 3,
      result_count: 9,
    },
    {
      id: "experiment.001-drizzle-brief",
      title: "Drizzle migration default version trap",
      hypothesis: "A source-backed brief should reduce stale issue replay and version mismatch edits.",
      status: "running",
      condition_count: 3,
      result_count: 18,
    },
  ],
  review_queue: [
    {
      id: "policy.candidate.clean-pass",
      type: "policy",
      title: "Clean pass requires explained churn",
      status: "draft",
      summary: "Final green verification is not clean evidence when earlier failures were unexplained.",
    },
  ],
  policy_candidate_categories: [{ id: "red_green_churn", count: 1 }],
  stale_knowledge: [
    {
      page: { id: "source.github-issue.openai.openai-python.2677", title: "Responses migration tool call incompatibility" },
      freshness: { allowed_use: "evidence_only" },
    },
  ],
  duplicate_knowledge: [],
  agent_contract: {
    brief_id: "brief.demo.agent-contract",
    task: "Repair a Python SDK wrapper using issue evidence without replaying stale API advice.",
    repo: "/demo/python-api-drift",
    libraries: ["example-llm-sdk"],
    must_load: [
      "policy.clean-pass-requires-failure-cause",
      "knowledge.python-api-drift-local-shim",
      "policy.candidate.issue-evidence-version-gate",
    ],
    recommended: ["failure.stale-api-drift", "intervention.local-api-surface-first"],
    dependsOn: [
      {
        source: "knowledge.python-api-drift-local-shim",
        target: "failure.stale-api-drift",
        type: "dependsOn",
      },
    ],
    decision_rules: [
      "Treat issue evidence as hypothesis until local version and API surface are verified.",
      "Do not promote final pass when recovered test failures have no recorded cause.",
    ],
    recommended_checks: [
      "Open the local API shim before editing callers.",
      "Record failed verification cause before final answer.",
    ],
    evidence_pages: ["claim.issue.example-llm-sdk.upgrade-advice"],
  },
  story: {
    experiment: {
      id: "experiment.002-python-api-drift",
      title: "Python API drift with misleading issue evidence",
      hypothesis: "Protocol compliance, clean pass, and final task success must be measured separately.",
      status: "interpreted",
    },
    latest_matrix: { matrix_id: "matrix.api-drift-misleading-issue.54194da40068", run_count: 9 },
    latest_regression: { status: "stable" },
    latest_churn_runs: [
      {
        matrix_id: "matrix.api-drift-misleading-issue.54194da40068",
        condition_id: "gated_brief",
        run_id: "run.74922b23d02c",
        review_signals: { test_failure_count: 1, forbidden_edit_count: 0, wrong_file_edits: 0 },
      },
    ],
    policy_candidate_categories: [{ id: "red_green_churn", count: 1 }],
  },
};

function writeHeaders(): Record<string, string> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (apiKey) headers["x-api-key"] = apiKey;
  return headers;
}

export const fallbackGraph: GraphData = {
  nodes: [
    { id: "policy.clean-pass-requires-failure-cause", type: "policy", title: "Clean pass requires explaining recovered verification failures", status: "accepted" },
    { id: "failure.red-green-churn", type: "failure", title: "Red-green verification churn", status: "accepted" },
    { id: "intervention.record-red-green-cause", type: "intervention", title: "Record red-green failure cause", status: "accepted" },
    { id: "source.github-issue.openai.openai-python.2677", type: "source", title: "Responses migration tool call incompatibility", status: "accepted" },
  ],
  edges: [
    { source: "policy.clean-pass-requires-failure-cause", target: "failure.red-green-churn", type: "dependsOn" },
    { source: "policy.clean-pass-requires-failure-cause", target: "intervention.record-red-green-cause", type: "dependsOn" },
  ],
};
