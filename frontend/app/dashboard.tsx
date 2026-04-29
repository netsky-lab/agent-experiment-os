"use client";

import {
  Activity,
  BookOpen,
  Boxes,
  Brain,
  CheckCircle2,
  FileText,
  GitBranch,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  TestTube2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  DashboardData,
  ExperimentItem,
  GraphData,
  ReviewItem,
  fetchDashboardData,
  fetchGraphData,
  fallbackData,
  fallbackGraph,
} from "../lib/api";

type ViewId = "experiments" | "runs" | "review" | "brief" | "graph" | "health";

const views: Array<{ id: ViewId; label: string; group: string; icon: React.ComponentType<{ size?: number }> }> = [
  { id: "experiments", label: "Experiments", group: "Research", icon: TestTube2 },
  { id: "runs", label: "Runs", group: "Research", icon: Activity },
  { id: "brief", label: "Agent Contract", group: "Brief", icon: BookOpen },
  { id: "review", label: "Review Queue", group: "Knowledge", icon: ShieldCheck },
  { id: "graph", label: "Knowledge Graph", group: "Knowledge", icon: GitBranch },
  { id: "health", label: "Knowledge Health", group: "Knowledge", icon: Brain },
];

export function Dashboard() {
  const [active, setActive] = useState<ViewId>("experiments");
  const [data, setData] = useState<DashboardData>(fallbackData);
  const [graph, setGraph] = useState<GraphData>(fallbackGraph);
  const [status, setStatus] = useState<"loading" | "live" | "fallback">("loading");

  async function refresh() {
    setStatus("loading");
    const [dashboardResult, graphResult] = await Promise.allSettled([
      fetchDashboardData(),
      fetchGraphData(),
    ]);
    if (dashboardResult.status === "fulfilled") {
      setData(dashboardResult.value);
      setStatus("live");
    } else {
      setData(fallbackData);
      setStatus("fallback");
    }
    if (graphResult.status === "fulfilled") {
      setGraph(graphResult.value);
    } else {
      setGraph(fallbackGraph);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  const counts = useMemo(
    () => ({
      experiments: data.experiments.length,
      runs: data.story?.latest_churn_runs.length ?? 0,
      review: data.review_queue.length,
      pages: graph.nodes.length,
      stale: data.stale_knowledge.length,
      duplicates: data.duplicate_knowledge.length,
    }),
    [data, graph],
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">E</div>
          <div>
            <strong>ExpOS</strong>
            <span>research preview</span>
          </div>
        </div>
        <nav>
          {views.map((view, index) => {
            const Icon = view.icon;
            const showGroup = index === 0 || views[index - 1].group !== view.group;
            return (
              <div key={view.id}>
                {showGroup ? <div className="nav-group">{view.group}</div> : null}
                <button
                  className={active === view.id ? "nav-item active" : "nav-item"}
                  onClick={() => setActive(view.id)}
                >
                  <Icon size={15} />
                  <span>{view.label}</span>
                  <b>{countFor(view.id, counts)}</b>
                </button>
              </div>
            );
          })}
        </nav>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <p className="crumb">Agent Experiment OS / {labelFor(active)}</p>
            <h1>{titleFor(active)}</h1>
          </div>
          <div className="top-actions">
            <div className="search">
              <Search size={14} />
              <span>Search experiments, pages, runs</span>
              <kbd>⌘K</kbd>
            </div>
            <span className={status === "live" ? "status live" : "status"}>
              {status === "live" ? "API live" : status === "loading" ? "Loading" : "Fallback data"}
            </span>
            <button className="icon-button" onClick={refresh} aria-label="Refresh dashboard">
              <RefreshCw size={15} />
            </button>
          </div>
        </header>
        <section className="screen">
          {active === "experiments" ? <ExperimentsView data={data} /> : null}
          {active === "runs" ? <RunsView data={data} /> : null}
          {active === "review" ? <ReviewView items={data.review_queue} /> : null}
          {active === "brief" ? <BriefView data={data} /> : null}
          {active === "graph" ? <GraphView graph={graph} /> : null}
          {active === "health" ? <HealthView data={data} /> : null}
        </section>
      </main>
    </div>
  );
}

function ExperimentsView({ data }: { data: DashboardData }) {
  const selected = data.experiments[0];
  return (
    <div className="split">
      <div className="pane">
        <PaneHeader title="Experiments" subtitle={`${data.experiments.length} research threads`} />
        <div className="table">
          <div className="row head">
            <span>Experiment</span>
            <span>Status</span>
            <span>Conditions</span>
            <span>Results</span>
          </div>
          {data.experiments.map((experiment) => (
            <div className="row" key={experiment.id}>
              <span>
                <b>{experiment.title}</b>
                <small>{experiment.hypothesis}</small>
              </span>
              <Pill tone={experiment.status === "running" ? "ok" : "neutral"}>{experiment.status}</Pill>
              <span className="mono">{experiment.condition_count}</span>
              <span className="mono">{experiment.result_count}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="pane">
        <PaneHeader title="Latest Story" subtitle={data.story?.experiment.id ?? selected?.id ?? "no experiment"} />
        {data.story ? (
          <div className="story">
            <h2>{data.story.experiment.title}</h2>
            <p>{data.story.experiment.hypothesis}</p>
            <div className="metric-grid">
              <Metric label="latest matrix runs" value={data.story.latest_matrix?.run_count ?? 0} />
              <Metric label="review runs" value={data.story.latest_churn_runs.length} />
              <Metric label="regression" value={data.story.latest_regression?.status ?? "n/a"} />
              <Metric label="policy categories" value={data.story.policy_candidate_categories.length} />
            </div>
          </div>
        ) : (
          <EmptyState text="Run a matrix to populate the experiment story." />
        )}
      </div>
    </div>
  );
}

function RunsView({ data }: { data: DashboardData }) {
  const runs = data.story?.latest_churn_runs ?? [];
  return (
    <div className="pane full">
      <PaneHeader title="Runs Needing Review" subtitle="red-green churn, forbidden edits, wrong-file edits" />
      <div className="table">
        <div className="row head">
          <span>Run</span>
          <span>Condition</span>
          <span>Matrix</span>
          <span>Failures</span>
        </div>
        {runs.map((run) => (
          <div className="row" key={run.run_id}>
            <span className="mono">{run.run_id}</span>
            <span>{run.condition_id}</span>
            <span className="mono">{run.matrix_id}</span>
            <Pill tone={run.review_signals.test_failure_count > 0 ? "warn" : "neutral"}>
              {run.review_signals.test_failure_count} test failure(s)
            </Pill>
          </div>
        ))}
        {runs.length === 0 ? <EmptyState text="No churn runs in the current read model." /> : null}
      </div>
    </div>
  );
}

function ReviewView({ items }: { items: ReviewItem[] }) {
  return (
    <div className="split">
      <div className="pane">
        <PaneHeader title="Review Queue" subtitle={`${items.length} pages waiting`} />
        <div className="table">
          <div className="row head">
            <span>Page</span>
            <span>Type</span>
            <span>Status</span>
          </div>
          {items.map((item) => (
            <div className="row three" key={item.id}>
              <span>
                <b>{item.title}</b>
                <small>{item.summary}</small>
              </span>
              <span>{item.type}</span>
              <Pill tone="warn">{item.status}</Pill>
            </div>
          ))}
        </div>
      </div>
      <div className="pane">
        <PaneHeader title="Review Contract" subtitle="promotion is auditable" />
        <div className="contract-list">
          <ContractItem icon={ShieldCheck} title="Evidence required" text="Policies and interventions require rationale and evidence ids before acceptance." />
          <ContractItem icon={GitBranch} title="dependsOn preserved" text="Accepted pages keep links to failures, interventions, claims, and source snapshots." />
          <ContractItem icon={CheckCircle2} title="Saturated matrices blocked" text="Policy promotion is blocked when task success is already saturated or churn is unexplained." />
        </div>
      </div>
    </div>
  );
}

function BriefView({ data }: { data: DashboardData }) {
  const contract = data.contract;
  return (
    <div className="split">
      <div className="pane">
        <PaneHeader title="Agent Contract Preview" subtitle={contract.version} />
        <div className="contract-list">
          {contract.surfaces.slice(0, 8).map((surface) => (
            <article className="contract-card" key={surface.id}>
              <span className="mono">{surface.endpoint}</span>
              <h3>{surface.id}</h3>
              <p>{surface.purpose}</p>
            </article>
          ))}
        </div>
      </div>
      <div className="pane">
        <PaneHeader title="Protocol Sequence" subtitle="what agents should do before final answer" />
        <div className="timeline">
          {["start_pre_work_protocol", "resolve_dependencies", "record_decision", "test_run", "complete_run"].map((step) => (
            <div className="timeline-row" key={step}>
              <Sparkles size={14} />
              <span>{step}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function GraphView({ graph }: { graph: GraphData }) {
  return (
    <div className="split">
      <div className="pane">
        <PaneHeader title="Wiki Pages" subtitle={`${graph.nodes.length} nodes`} />
        <div className="table compact">
          {graph.nodes.slice(0, 24).map((node) => (
            <div className="row three" key={node.id}>
              <span>
                <b>{node.title}</b>
                <small>{node.id}</small>
              </span>
              <span>{node.type}</span>
              <Pill tone={node.status === "accepted" ? "ok" : "warn"}>{node.status}</Pill>
            </div>
          ))}
        </div>
      </div>
      <div className="pane">
        <PaneHeader title="Edges" subtitle={`${graph.edges.length} relations`} />
        <div className="edge-map">
          {graph.edges.slice(0, 36).map((edge, index) => (
            <div className="edge" key={`${edge.source}-${edge.target}-${index}`}>
              <span>{edge.source}</span>
              <b>{edge.type}</b>
              <span>{edge.target}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function HealthView({ data }: { data: DashboardData }) {
  return (
    <div className="split">
      <div className="pane">
        <PaneHeader title="Stale Knowledge" subtitle={`${data.stale_knowledge.length} source-backed warnings`} />
        <div className="contract-list">
          {data.stale_knowledge.map((item) => (
            <article className="contract-card" key={item.page.id}>
              <span className="mono">{item.freshness.allowed_use ?? "evidence_only"}</span>
              <h3>{item.page.title}</h3>
              <p>{item.page.id}</p>
            </article>
          ))}
          {data.stale_knowledge.length === 0 ? <EmptyState text="No stale pages detected." /> : null}
        </div>
      </div>
      <div className="pane">
        <PaneHeader title="Duplicate Candidates" subtitle={`${data.duplicate_knowledge.length} groups`} />
        <div className="contract-list">
          {data.duplicate_knowledge.map((group) => (
            <article className="contract-card" key={group.fingerprint}>
              <span className="mono">{group.type}</span>
              <h3>{group.fingerprint}</h3>
              <p>{group.pages.map((page) => page.id).join(", ")}</p>
            </article>
          ))}
          {data.duplicate_knowledge.length === 0 ? <EmptyState text="No duplicate candidates detected." /> : null}
        </div>
      </div>
    </div>
  );
}

function PaneHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="pane-header">
      <h2>{title}</h2>
      <span>{subtitle}</span>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function Pill({ children, tone }: { children: React.ReactNode; tone: "ok" | "warn" | "neutral" }) {
  return <span className={`pill ${tone}`}>{children}</span>;
}

function EmptyState({ text }: { text: string }) {
  return <div className="empty">{text}</div>;
}

function ContractItem({
  icon: Icon,
  title,
  text,
}: {
  icon: React.ComponentType<{ size?: number }>;
  title: string;
  text: string;
}) {
  return (
    <article className="contract-card">
      <Icon size={17} />
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}

function countFor(view: ViewId, counts: Record<string, number>) {
  if (view === "experiments") return counts.experiments;
  if (view === "runs") return counts.runs;
  if (view === "review") return counts.review;
  if (view === "graph") return counts.pages;
  if (view === "health") return counts.stale + counts.duplicates;
  return "";
}

function labelFor(view: ViewId) {
  return views.find((item) => item.id === view)?.label ?? view;
}

function titleFor(view: ViewId) {
  if (view === "brief") return "Agent Contract Preview";
  if (view === "health") return "Knowledge Health";
  return labelFor(view);
}
