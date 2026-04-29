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
  story?: {
    experiment: { id: string; title: string; hypothesis: string; status: string };
    latest_matrix: { matrix_id: string; run_count: number } | null;
    latest_regression: { status: string } | null;
    latest_churn_runs: ChurnRun[];
    policy_candidate_categories: Array<{ id: string; count: number }>;
  };
};

export type GraphData = {
  nodes: Array<{ id: string; type: string; title: string; status: string }>;
  edges: Array<{ source: string; target: string; type: string }>;
};

const apiBase = process.env.NEXT_PUBLIC_EXPERIMENT_OS_API_URL;

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
