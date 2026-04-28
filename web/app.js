const state = { view: "experiments", data: null, graph: null };

async function load() {
  const response = await fetch("/ui/bootstrap");
  if (!response.ok) throw new Error(`Bootstrap failed: ${response.status}`);
  state.data = await response.json();
  const graphResponse = await fetch("/wiki/graph");
  if (graphResponse.ok) state.graph = await graphResponse.json();
  render();
}

function setView(view) {
  state.view = view;
  document.querySelectorAll(".nav").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  render();
}

function render() {
  const data = state.data;
  const content = document.getElementById("content");
  if (!data) return;
  const titles = {
    experiments: ["Experiments", "Hypotheses, matrices, and current evidence."],
    review: ["Review", "Draft policies and issue-derived knowledge waiting for evidence."],
    runs: ["Runs", "Recent churn and verification work."],
    contract: ["Agent Contract", "Backend surfaces available to the product UI and MCP agents."],
    knowledge: ["Knowledge", "Freshness, duplicates, and review boundaries for agent memory."],
    graph: ["Graph", "Wiki pages and dependsOn/provenance edges."],
  };
  document.getElementById("title").textContent = titles[state.view][0];
  document.getElementById("subtitle").textContent = titles[state.view][1];
  content.innerHTML = views[state.view](data);
}

const views = {
  experiments(data) {
    return `<div class="stack">
      ${data.story ? story(data.story) : ""}
      <div class="grid">${data.experiments.map(experimentCard).join("")}</div>
    </div>`;
  },
  review(data) {
    const rows = data.review_queue.map((item) => `
      <tr>
        <td>${escapeHtml(item.id)}</td>
        <td>${escapeHtml(item.type)}</td>
        <td>${escapeHtml(item.status)}</td>
        <td>${escapeHtml(item.summary || "")}</td>
      </tr>
    `).join("");
    return `<table class="table"><thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Summary</th></tr></thead><tbody>${rows}</tbody></table>`;
  },
  runs(data) {
    const categories = data.policy_candidate_categories.map((category) => `
      <div class="card">
        <h3>${escapeHtml(category.id)}</h3>
        <p>${category.count} candidate(s)</p>
      </div>
    `).join("");
    return `<div class="grid">${categories || empty("No policy candidates need review.")}</div>`;
  },
  contract(data) {
    return `<pre>${escapeHtml(JSON.stringify(data.contract, null, 2))}</pre>`;
  },
  knowledge(data) {
    const stale = data.stale_knowledge || [];
    const duplicates = data.duplicate_knowledge || [];
    return `<div class="split">
      <section>
        <h2 class="section-title">Stale Signals</h2>
        <div class="stack">${stale.map(staleCard).join("") || empty("No stale source-backed pages detected.")}</div>
      </section>
      <section>
        <h2 class="section-title">Duplicate Candidates</h2>
        <div class="stack">${duplicates.map(duplicateCard).join("") || empty("No duplicate knowledge candidates detected.")}</div>
      </section>
    </div>`;
  },
  graph() {
    const graph = state.graph || { nodes: [], edges: [] };
    const nodes = graph.nodes.slice(0, 80).map((node) => `
      <tr>
        <td>${escapeHtml(node.id)}</td>
        <td>${escapeHtml(node.type)}</td>
        <td>${escapeHtml(node.status)}</td>
        <td>${escapeHtml(node.title)}</td>
      </tr>
    `).join("");
    const edges = graph.edges.slice(0, 120).map((edge) => `
      <tr>
        <td>${escapeHtml(edge.source)}</td>
        <td>${escapeHtml(edge.type)}</td>
        <td>${escapeHtml(edge.target)}</td>
      </tr>
    `).join("");
    return `<div class="split">
      <section><h2 class="section-title">Pages</h2><table class="table"><thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Title</th></tr></thead><tbody>${nodes}</tbody></table></section>
      <section><h2 class="section-title">Edges</h2><table class="table"><thead><tr><th>Source</th><th>Type</th><th>Target</th></tr></thead><tbody>${edges}</tbody></table></section>
    </div>`;
  },
};

function story(item) {
  const regression = item.latest_regression;
  return `<section class="summary-band">
    <div>
      <span class="eyebrow">Latest story</span>
      <h2>${escapeHtml(item.experiment.title)}</h2>
      <p>${escapeHtml(item.experiment.hypothesis)}</p>
    </div>
    <div class="kpis">
      <div><strong>${item.latest_matrix ? item.latest_matrix.run_count : 0}</strong><span>runs</span></div>
      <div><strong>${item.latest_churn_runs.length}</strong><span>review runs</span></div>
      <div><strong>${regression ? regression.status : "n/a"}</strong><span>regression</span></div>
    </div>
  </section>`;
}

function experimentCard(item) {
  return `
    <article class="card">
      <h2>${escapeHtml(item.title)}</h2>
      <p>${escapeHtml(item.hypothesis)}</p>
      <div class="meta">
        <span class="pill good">${escapeHtml(item.status)}</span>
        <span class="pill">${item.condition_count} conditions</span>
        <span class="pill">${item.result_count} results</span>
      </div>
    </article>
  `;
}

function staleCard(item) {
  const page = item.page;
  const freshness = item.freshness;
  return `<article class="card">
    <h3>${escapeHtml(page.title)}</h3>
    <p>${escapeHtml(page.id)}</p>
    <div class="meta">
      <span class="pill warn">stale</span>
      <span class="pill">${escapeHtml(freshness.allowed_use || "unknown")}</span>
    </div>
  </article>`;
}

function duplicateCard(item) {
  return `<article class="card">
    <h3>${escapeHtml(item.fingerprint)}</h3>
    <p>${item.pages.length} page(s) share this title fingerprint.</p>
    <div class="meta">${item.pages.map((page) => `<span class="pill">${escapeHtml(page.id)}</span>`).join("")}</div>
  </article>`;
}

function empty(message) {
  return `<div class="card"><p>${escapeHtml(message)}</p></div>`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

document.querySelectorAll(".nav").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
});
document.getElementById("refresh").addEventListener("click", load);
load().catch((error) => {
  document.getElementById("content").innerHTML = `<div class="card"><h2>Load failed</h2><p>${escapeHtml(error.message)}</p></div>`;
});
