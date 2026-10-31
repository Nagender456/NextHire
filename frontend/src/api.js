const apiBaseUrl = import.meta.env.VITE_API_URL ?? "";
const REQUEST_TIMEOUT_MS = 15_000;

async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The API request timed out. Is the NextHire API running?");
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export async function getDashboard() {
  const response = await fetchWithTimeout(`${apiBaseUrl}/api/v1/dashboard`, {
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error(`Dashboard request failed with ${response.status}`);
  }
  return response.json();
}

export function getAnalytics() {
  return request("/api/v1/analytics");
}

export function getAdminOverview() {
  return request("/api/v1/admin/overview");
}

export function getAdminCompanies() {
  return request("/api/v1/admin/companies");
}

export function getAdminJobs() {
  return request("/api/v1/admin/jobs");
}

export function getAdminCrawls() {
  return request("/api/v1/admin/crawls");
}

export function getAdminActivity() {
  return request("/api/v1/admin/activity");
}

export function getAdminAudit() {
  return request("/api/v1/admin/audit");
}

export function createCompany(company) {
  return request("/api/v1/admin/companies", {
    method: "POST",
    body: JSON.stringify(company),
  });
}

export function updateCompany(companyId, changes) {
  return request(`/api/v1/admin/companies/${companyId}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export function refreshCompany(companyId) {
  return request(`/api/v1/admin/companies/${companyId}/refresh`, { method: "POST" });
}

export function refreshAllCompanies() {
  return request("/api/v1/admin/jobs/refresh", { method: "POST" });
}

export function deleteCompany(companyId) {
  return request(`/api/v1/admin/companies/${companyId}`, { method: "DELETE" });
}

export function resetPrototypeCompanies() {
  return request("/api/v1/admin/companies/reset-prototype", { method: "POST" });
}

export function getSchedulerStatus() {
  return request("/api/v1/admin/scheduler/status");
}

export function triggerScheduler() {
  return request("/api/v1/admin/scheduler/trigger", { method: "POST" });
}

export function getPrivacySettings() {
  return request("/api/v1/privacy");
}

export function updatePrivacySettings(changes) {
  return request("/api/v1/privacy", {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export function exportUserData() {
  return request("/api/v1/privacy/export");
}

export function getRetentionPolicy() {
  return request("/api/v1/admin/retention");
}

export function updateRetentionPolicy(changes) {
  return request("/api/v1/admin/retention", {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export function purgeRetention() {
  return request("/api/v1/admin/retention/purge", { method: "POST" });
}

export function getJobs() {
  return request("/api/v1/jobs");
}

export function getCompanies() {
  return request("/api/v1/companies");
}

export function seedJobs() {
  return request("/api/v1/jobs/seed", { method: "POST" });
}

async function request(path, options = {}) {
  const csrfToken = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith("nexthire_csrf="))
    ?.split("=")[1];
  const response = await fetchWithTimeout(`${apiBaseUrl}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail?.message ?? `Request failed with ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

export function getCurrentUser() {
  return request("/api/v1/auth/me");
}

export function signIn(email, password) {
  return request("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function signUp(email, password, displayName) {
  return request("/api/v1/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password, display_name: displayName }),
  });
}

export function signOut() {
  return request("/api/v1/auth/logout", { method: "POST" });
}

export function updateProfile(profile) {
  return request("/api/v1/profile", {
    method: "PATCH",
    body: JSON.stringify(profile),
  });
}

export function getProfile() {
  return request("/api/v1/profile");
}

export function requestPasswordReset(email) {
  return request("/api/v1/auth/password-reset/request", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function confirmPasswordReset(token, password) {
  return request("/api/v1/auth/password-reset/confirm", {
    method: "POST",
    body: JSON.stringify({ token, password }),
  });
}

export function listCareerEntities(type) {
  return request(`/api/v1/career/${type}`);
}

export function createCareerEntity(type, entity) {
  return request(`/api/v1/career/${type}`, {
    method: "POST",
    body: JSON.stringify(entity),
  });
}

export function updateCareerEntity(type, id, entity) {
  return request(`/api/v1/career/${type}/${id}`, {
    method: "PATCH",
    body: JSON.stringify(entity),
  });
}

export function deleteCareerEntity(type, id) {
  return request(`/api/v1/career/${type}/${id}`, { method: "DELETE" });
}

export function uploadCareerDocument(file) {
  const form = new FormData();
  form.append("file", file);
  const csrfToken = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith("nexthire_csrf="))
    ?.split("=")[1];
  return fetch(`${apiBaseUrl}/api/v1/career/documents`, {
    method: "POST",
    body: form,
    credentials: "include",
    headers: csrfToken ? { "X-CSRF-Token": csrfToken } : {},
  }).then(async (response) => {
    if (!response.ok) throw new Error(`Upload failed with ${response.status}`);
    return response.json();
  });
}

export function listCareerDocuments() {
  return request("/api/v1/career/documents");
}

export function listExtractedEntities(documentId) {
  return request(`/api/v1/career/documents/${documentId}/extracted`);
}

export function reviewExtractedEntity(documentId, entityId, confirmed) {
  return request(`/api/v1/career/documents/${documentId}/extracted/${entityId}?confirmed_by_user=${confirmed}`, {
    method: "PATCH",
  });
}

export function acceptAllExtractedEntities(documentId) {
  return request(`/api/v1/career/documents/${documentId}/accept-all`, {
    method: "POST",
  });
}

export function prepareEmbeddingChunks(documentId) {
  return request(`/api/v1/career/documents/${documentId}/chunks`, { method: "POST" });
}

export function listExternalCandidates() {
  return request("/api/v1/career/sources");
}

export function ingestGitHub(username) {
  return request("/api/v1/career/sources/github", {
    method: "POST",
    body: JSON.stringify({ username }),
  });
}

export function ingestPortfolio(url) {
  return request("/api/v1/career/sources/portfolio", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export function ingestLinkedIn(profileText) {
  return request("/api/v1/career/sources/linkedin", {
    method: "POST",
    body: JSON.stringify({ profile_text: profileText }),
  });
}

export function ingestLinkedInDocument(file) {
  const form = new FormData();
  form.append("file", file);
  const csrfToken = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith("nexthire_csrf="))
    ?.split("=")[1];
  return fetch(`${apiBaseUrl}/api/v1/career/sources/linkedin/document`, {
    method: "POST",
    body: form,
    credentials: "include",
    headers: csrfToken ? { "X-CSRF-Token": csrfToken } : {},
  }).then(async (response) => {
    if (!response.ok) throw new Error(`LinkedIn document import failed with ${response.status}`);
    return response.json();
  });
}

export function reviewExternalCandidate(candidateId, status) {
  return request(`/api/v1/career/sources/${candidateId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function searchJobs(query = "", filters = {}) {
  return request("/api/v1/search/jobs", {
    method: "POST",
    body: JSON.stringify({ query, ...filters }),
  });
}

export function reindexSearch() {
  return request("/api/v1/search/reindex", { method: "POST" });
}

export function getJobIntelligence(jobId) {
  return request(`/api/v1/jobs/${jobId}/intelligence`);
}

export function submitRecommendationFeedback(jobId, relevant) {
  return request(`/api/v1/jobs/${jobId}/feedback`, {
    method: "POST",
    body: JSON.stringify({ relevant }),
  });
}

export function generateResume(jobId) {
  return request(`/api/v1/jobs/${jobId}/resumes`, { method: "POST" });
}

export function listResumes() {
  return request("/api/v1/resumes");
}

export function updateResume(resumeId, content, status) {
  return request(`/api/v1/resumes/${resumeId}`, {
    method: "PATCH",
    body: JSON.stringify({ content, ...(status ? { status } : {}) }),
  });
}

export function exportResumeLatex(resumeId) {
  const csrfToken = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith("nexthire_csrf="))
    ?.split("=")[1];
  return fetch(`${apiBaseUrl}/api/v1/resumes/${resumeId}/latex`, {
    credentials: "include",
    headers: csrfToken ? { "X-CSRF-Token": csrfToken } : {},
  }).then(async (response) => {
    if (!response.ok) throw new Error(`LaTeX export failed with ${response.status}`);
    return response.text();
  });
}

export function listApplications() {
  return request("/api/v1/applications");
}

export function createApplication(application) {
  return request("/api/v1/applications", {
    method: "POST",
    body: JSON.stringify(application),
  });
}

export function updateApplication(applicationId, changes) {
  return request(`/api/v1/applications/${applicationId}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export function listNotifications() {
  return request("/api/v1/notifications");
}

export function markNotificationRead(notificationId, read = true) {
  return request(`/api/v1/notifications/${notificationId}`, {
    method: "PATCH",
    body: JSON.stringify({ read }),
  });
}

export function scrapeNaukriJobs(payload = {}) {
  return request("/api/v1/jobs/scrape-naukri", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

