// Auth guard - bounce to login if there's no token
const token = localStorage.getItem("newspulse_token");
if (!token) {
  window.location.href = "login.html";
}

document.addEventListener("DOMContentLoaded", () => {
  const name = localStorage.getItem("newspulse_name") || "there";
  document.getElementById("greeting").textContent = `Good to see you, ${name.split(" ")[0]}`;
  document.getElementById("today-date").textContent = new Date().toLocaleDateString(undefined, {
    weekday: "short", month: "short", day: "numeric",
  });

  loadFeed("foryou");

  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach((i) => i.classList.remove("active"));
      item.classList.add("active");
      loadFeed(item.dataset.tab);
    });
  });
});

async function loadFeed(tab) {
  const grid = document.getElementById("article-grid");
  grid.innerHTML = `<p style="padding: 20px 0;">Loading your feed…</p>`;

  try {
    let articles;
    if (tab === "foryou") {
      articles = await api.getRecommendations();
    } else if (tab === "trending") {
      articles = await api.getTrending();
    } else {
      articles = await api.getArticles(tab); // "tech" | "world"
    }
    renderArticles(articles);
  } catch (err) {
    grid.innerHTML = `<p style="padding: 20px 0;">Couldn't load articles right now. ${err.message}</p>`;
  }
}

function renderArticles(articles) {
  const grid = document.getElementById("article-grid");
  if (!articles || articles.length === 0) {
    grid.innerHTML = `<p style="padding: 20px 0;">No articles yet — check back after the next ingestion run.</p>`;
    return;
  }

  grid.innerHTML = articles
    .map((a, i) => {
      const relevance = a.score ? Math.round(a.score * 100) : null;
      const thumb = a.image_url
        ? `<img class="article-thumb" src="${a.image_url}" alt="" onerror="this.outerHTML='<div class=&quot;article-thumb-placeholder&quot;></div>'">`
        : `<div class="article-thumb-placeholder"></div>`;

      return `
        <article class="article-card" style="animation-delay: ${Math.min(i * 50, 400)}ms" onclick="handleArticleClick('${a.id}', '${a.url}')">
          <div class="relevance-bar" style="--relevance: ${relevance ?? 60}%"></div>
          ${thumb}
          <div>
            <div class="card-top-row">
              <span class="tag">${(a.category || "world").toUpperCase()}</span>
              ${relevance !== null ? `<span class="match-badge">${relevance}% match</span>` : ""}
            </div>
            <h3>${a.title}</h3>
            <p>${a.description || ""}</p>
            <div class="meta">
              <span>${a.source}</span>
              <span>${new Date(a.published_at).toLocaleDateString()}</span>
              ${a.reason ? `<span class="reason">${a.reason}</span>` : ""}
            </div>
          </div>
        </article>`;
    })
    .join("");
}

function handleArticleClick(articleId, url) {
  api.logInteraction(articleId, "click").catch(() => {});
  window.open(url, "_blank");
}