const API_BASE = "https://newspulse-ai-zs15.onrender.com";
// Wake up Render backend on page load
fetch(`${API_BASE}/`).catch(() => {});
async function apiRequest(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = localStorage.getItem("newspulse_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    // FastAPI sends errors as { detail: "..." }
    throw new Error(data.detail || "Something went wrong. Please try again.");
  }
  return data;
}

const api = {
  signup: (payload) => apiRequest("/auth/signup", { method: "POST", body: payload }),
  login: (payload) => apiRequest("/auth/login", { method: "POST", body: payload }),
  googleLogin: (id_token) => apiRequest("/auth/google", { method: "POST", body: { id_token } }),
  forgotPassword: (payload) => apiRequest("/auth/forgot-password", { method: "POST", body: payload }),
  resetPassword: (payload) => apiRequest("/auth/reset-password", { method: "POST", body: payload }),
  getRecommendations: () => apiRequest("/recommendations/", { auth: true }),
  getTrending: () => apiRequest("/articles/trending"),
  getArticles: (category) => apiRequest(`/articles/${category ? `?category=${category}` : ""}`),
  logInteraction: (article_id, action) =>
    apiRequest("/articles/interactions", { method: "POST", body: { article_id, action }, auth: true }),
};