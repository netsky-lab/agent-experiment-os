const state = { view: "experiments", data: null };

async function load() {
  const response = await fetch("/ui/bootstrap");
  if (!response.ok) throw new Error(`Bootstrap failed: ${response.status}`);
  state.data = await response.json();
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
  };
  document.getElementById("title").textContent = titles[state.view][0];
  document.getElementById("subtitle").textContent = titles[state.view][1];
  content.innerHTML = views[state.view](data);
}

const views = {
  experiments(data) {
    return `<div class="grid">${data.experiments.map(experimentCard).join("")}</div>`;
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
};

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
