const api = {
  signup: (payload) => apiRequest("/api/auth/signup", { method: "POST", body: payload }),
  login: (payload) => apiRequest("/api/auth/login", { method: "POST", body: payload }),
  googleLogin: (id_token) => apiRequest("/api/auth/google", { method: "POST", body: { id_token } }),
  forgotPassword: (payload) => apiRequest("/api/auth/forgot-password", { method: "POST", body: payload }),
  resetPassword: (payload) => apiRequest("/api/auth/reset-password", { method: "POST", body: payload }),
  getRecommendations: () => apiRequest("/api/recommendations/", { auth: true }),
  getTrending: () => apiRequest("/api/articles/trending"),
  getArticles: (category) => apiRequest(`/api/articles/${category ? `?category=${category}` : ""}`),
  logInteraction: (article_id, action) => apiRequest("/api/articles/interactions", { method: "POST", body: { article_id, action }, auth: true }),
};
fetch("${API_BASE}/").catch(() => {});
async function apiRequest(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = localStorage.getItem("newspulse_token");
    if (token) headers["Authorization"] = "Bearer ${token}";
  }
  const response = await fetch("${API_BASE}${path}", {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong. Please try again.");
  }
  return data;
}
const api = {
  signup: (payload) => apiRequest("/api/auth/signup", { method: "POST", body: payload }),
  login: (payload) => apiRequest("/api/auth/login", { method: "POST", body: payload }),
  googleLogin: (id_token) => apiRequest("/api/auth/google", { method: "POST", body: { id_token } }),
  forgotPassword: (payload) => apiRequest("/api/auth/forgot-password", { method: "POST", body: payload }),
  resetPassword: (payload) => apiRequest("/api/auth/reset-password", { method: "POST", body: payload }),
  getRecommendations: () => apiRequest("/api/recommendations/", { auth: true }),
  getTrending: () => apiRequest("/api/articles/trending"),
  getArticles: (category) => apiRequest("/api/articles/${category ? "?category=${category}" : """}", { auth: true }),
  logInteraction: (article_id, action) => apiRequest("/api/articles/interactions", { method: "POST", body: { article_id, action }, auth: true }),
};
