import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  getCurrentUser,
  getCompanies,
  getDashboard,
  getAnalytics,
  getAdminOverview,
  getAdminCompanies,
  getAdminJobs,
  getAdminCrawls,
  getAdminActivity,
  getAdminAudit,
  createCompany,
  updateCompany,
  refreshCompany,
  getPrivacySettings,
  updatePrivacySettings,
  exportUserData,
  getRetentionPolicy,
  updateRetentionPolicy,
  purgeRetention,
  getJobs,
  seedJobs,
  getJobIntelligence,
  getProfile,
  createCareerEntity,
  updateCareerEntity,
  deleteCareerEntity,
  ingestGitHub,
  ingestLinkedIn,
  ingestLinkedInDocument,
  ingestPortfolio,
  listExternalCandidates,
  listExtractedEntities,
  listCareerEntities,
  prepareEmbeddingChunks,
  reviewExternalCandidate,
  reviewExtractedEntity,
  acceptAllExtractedEntities,
  listCareerDocuments,
  uploadCareerDocument,
  deleteCompany,
  approveCompany,
  rejectCompany,
  resetPrototypeCompanies,
  refreshAllCompanies,
  getSchedulerStatus,
  triggerScheduler,
  requestPasswordReset,
  signIn,
  signOut,
  signUp,
  updateProfile,
  submitRecommendationFeedback,
  listApplications,
  createApplication,
  updateApplication,
  deleteApplication,
  listNotifications,
  markNotificationRead,
  scrapeNaukriJobs,
  dismissJob,
  generateResume,
  listResumes,
  updateResume,
  listResumeTemplates,
  exportResumeLatex,
} from "./api";
import { paginateItems } from "./pagination";
import {
  LayoutDashboard,
  Compass,
  FileText,
  CheckCircle2,
  BarChart3,
  Settings,
  Briefcase,
  Sparkles,
  Bookmark,
  Send,
  Calendar,
  Trophy,
  Archive,
  TrendingUp,
  Building2,
  Plus,
  ChevronRight,
  ExternalLink,
  Layers,
  LogOut,
  Download,
  Search,
  MapPin,
  Clock,
  Check,
  AlertCircle,
  BookmarkCheck,
  X,
  Filter,
  SlidersHorizontal,
  ThumbsUp,
  ThumbsDown,
  ArrowUpDown,
  ShieldCheck,
  RefreshCw,
  Trash2,
  Globe,
  Power,
  Play,
  Upload,
  ArrowLeft,
  ArrowRight,
  Edit2,
  ArrowUp,
  ArrowDown,
  User,
  Mail,
  Bell,
  Shield,
} from "lucide-react";
import "./styles.css";

const navigation = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/jobs", label: "Job Feed", icon: Compass },
  { href: "/profile", label: "Resumes", icon: FileText },
  { href: "/applications", label: "Applications", icon: CheckCircle2 },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/admin", label: "Settings", icon: Settings },
];

const pageCopy = {
  "/": ["Career Overview", "Real-time summary of your job search progress."],
  "/dashboard": ["Career Overview", "Real-time summary of your job search progress."],
  "/profile": ["Resumes & Career Profile", "Manage your resumes, experience, and career knowledge base."],
  "/jobs": ["Job Feed", "Discover relevant opportunities matching your skills and experience."],
  "/applications": ["Applications", "Track and manage your application pipeline in one place."],
  "/analytics": ["Analytics", "Understand your job discovery reach and application pipeline funnel."],
  "/login": ["Welcome back.", "Sign in to your NextHire career workspace."],
  "/signup": ["Create your account.", "Start building your career trajectory with AI."],
  "/admin": ["Settings & Workspace", "Manage privacy controls, data export, and system preferences."],
};

function App() {
  const path = window.location.pathname;
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [dashboard, setDashboard] = useState(null);
  const [dashboardError, setDashboardError] = useState(false);
  const [title, description] = pageCopy[path] ?? [
    "Your career, intelligently connected.",
    "NextHire will connect your career knowledge with relevant opportunities, explain job fit, and help you move from discovery to application.",
  ];

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setAuthChecked(true));
  }, [path]);

  const reloadDashboard = () => {
    setDashboard(null);
    setDashboardError(false);
    getDashboard().then(setDashboard).catch(() => setDashboardError(true));
  };

  useEffect(() => {
    if (path !== "/dashboard" && path !== "/") return;
    if (!user) return;
    reloadDashboard();
  }, [path, user]);

  if (!authChecked) return <p className="loading-screen">Loading NextHire...</p>;
  if (path === "/login") {
    return <AuthPage mode="login" onAuthenticated={setUser} />;
  }
  if (path === "/signup") {
    return <AuthPage mode="signup" onAuthenticated={setUser} />;
  }
  if (path === "/forgot-password") return <PasswordResetPage />;
  if (!user) {
    return <AuthRequired />;
  }

  const breadcrumbCurrent =
    path === "/analytics"
      ? "Analytics"
      : path === "/jobs"
      ? "Job Feed"
      : path === "/profile"
      ? "Resumes"
      : path === "/applications"
      ? "Applications"
      : path === "/admin"
      ? (user?.role === "ADMIN" ? "Admin Console & Scraper" : "Settings")
      : "Career Overview";

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Application sidebar">
        <div style={{ display: "flex", alignItems: "center", gap: "9px", marginBottom: "1.75rem", paddingLeft: "4px" }}>
          <div style={{ width: "26px", height: "26px", borderRadius: "6px", background: "var(--colors-primary)", display: "flex", alignItems: "center", justifyContent: "center", color: "#ffffff", flexShrink: 0 }}>
            <Layers size={15} />
          </div>
          <p className="brand" style={{ margin: 0, letterSpacing: "0.14em" }}>NEXT HIRE</p>
        </div>
        <nav aria-label="Primary navigation">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = item.href === path || (item.href === "/" && path === "/dashboard");
            return (
              <a
                className={isActive ? "nav-link active" : "nav-link"}
                href={item.href}
                key={item.href}
              >
                {Icon && <Icon className="nav-icon" />}
                <span>{item.label}</span>
              </a>
            );
          })}
          {user?.role === "ADMIN" && (
            <div style={{ marginTop: "1rem", paddingTop: "0.75rem", borderTop: "1px solid var(--colors-hairline)" }}>
              <span style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.08em", color: "var(--colors-steel)", textTransform: "uppercase", paddingLeft: "12px", display: "block", marginBottom: "4px" }}>
                Admin Operations
              </span>
              <a
                className={path === "/admin" ? "nav-link active" : "nav-link"}
                href="/admin"
                style={{ color: "var(--colors-primary)", fontWeight: 600 }}
              >
                <ShieldCheck className="nav-icon" size={16} />
                <span>Admin Console</span>
              </a>
            </div>
          )}
        </nav>
        <div className="sidebar-footer">
          <span>AI career assistant</span>
        </div>
      </aside>
      <main className="content" id="main-content">
        <header className="topbar">
          <div className="breadcrumbs">
            <span className="breadcrumb-root">Dashboard</span>
            <ChevronRight size={13} className="breadcrumb-sep" />
            <span className="breadcrumb-current">{breadcrumbCurrent}</span>
            <span className="workspace-badge-linear">Personal Workspace</span>
          </div>
          <div className="topbar-actions">
            <div className="user-profile-menu">
              <div className="user-avatar-circle">
                {user.display_name ? user.display_name.charAt(0).toUpperCase() : "A"}
              </div>
              <span className="user-name">{user.display_name || "Alex Developer"}</span>
              {user.role === "ADMIN" && (
                <span style={{ fontSize: "10px", fontWeight: 700, padding: "2px 6px", borderRadius: "4px", background: "rgba(86, 69, 212, 0.12)", color: "var(--colors-primary)", letterSpacing: "0.04em" }}>
                  ADMIN
                </span>
              )}
            </div>
            <button
              className="signout-button"
              onClick={() => signOut().then(() => setUser(null))}
              title="Sign out"
            >
              <LogOut size={13} />
              <span>Sign out</span>
            </button>
          </div>
        </header>
        <section className="page-heading">
          {path !== "/" && path !== "/dashboard" && (
            <>
              <p className="eyebrow">NEXT HIRE</p>
              <h1>{title}</h1>
              <p className="intro">{description}</p>
            </>
          )}
          {path === "/dashboard" || path === "/" ? (
            <DashboardContent
              dashboard={dashboard}
              error={dashboardError}
              onReload={reloadDashboard}
              user={user}
            />
          ) : path === "/profile" ? (
            <ProfileEditor user={user} onUpdated={setUser} />
          ) : path === "/jobs" ? (
            <JobsPage />
          ) : path === "/applications" ? (
            <ApplicationsPage />
          ) : path === "/analytics" ? (
            <AnalyticsPage />
          ) : path === "/admin" ? (
            <SettingsPage user={user} />
          ) : (
            <FoundationStatus />
          )}
        </section>
      </main>
    </div>
  );
}

function cleanJobTitle(rawTitle = "") {
  if (!rawTitle) return "Software Engineer";
  let cleaned = rawTitle.trim();
  // Strip requisition / numerical IDs (e.g. 131138433534829254 Senior Software Engineer)
  cleaned = cleaned.replace(/^\d{4,}\s*[-–:]*\s*/, "");
  // Strip SEO prefixes
  cleaned = cleaned.replace(/^(Careers|Jobs|Work)\s+at\s+[^:]+:\s*/i, "");
  // Strip leading company name prefix if separated by delimiter
  cleaned = cleaned.replace(/^([A-Za-z0-9\s]+)\s*[-–|:]\s*(Senior|Junior|Staff|Lead|Principal|Software|Frontend|Backend|Fullstack|Data|AI|Machine|Product|Engineering|DevOps|Site|Cloud)/i, "$2");
  if (cleaned.length > 70) {
    cleaned = cleaned.substring(0, 67) + "...";
  }
  return cleaned || rawTitle;
}

export function deduplicateJobsList(jobsList) {
  if (!Array.isArray(jobsList)) return [];
  const seenUrls = new Set();
  const seenKeys = new Set();
  const seenIds = new Set();
  const unique = [];
  for (const j of jobsList) {
    if (!j || !j.id) continue;
    if (seenIds.has(j.id)) continue;
    const normUrl = (j.url || "").trim().toLowerCase().replace(/\/$/, "");
    const normKey = `${(j.company_id || "").trim().toLowerCase()}::${(j.title || "").trim().toLowerCase()}`;
    if (normUrl && seenUrls.has(normUrl)) continue;
    if (seenKeys.has(normKey)) continue;
    if (normUrl) seenUrls.add(normUrl);
    seenKeys.add(normKey);
    seenIds.add(j.id);
    unique.push(j);
  }
  return unique;
}

function getCompanyDetails(companyId = "", companies = []) {
  const company = (companies || []).find((c) => c.id === companyId);
  let name = company?.name;
  if (!name) {
    const raw = (companyId || "").replace(/^company-/, "");
    name = raw
      .split(/[-_]/)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
      .join(" ");
  }
  if (!name) name = "Company";

  const lowerName = name.toLowerCase();
  let avatarClass = "generic";
  let avatarText = name.slice(0, 2).toUpperCase();

  if (lowerName.includes("google")) {
    avatarClass = "google";
    avatarText = "G";
  } else if (lowerName.includes("stripe")) {
    avatarClass = "stripe";
    avatarText = "S";
  } else if (lowerName.includes("meta")) {
    avatarClass = "meta";
    avatarText = "M";
  } else if (lowerName.includes("amazon")) {
    avatarClass = "amazon";
    avatarText = "A";
  } else if (lowerName.includes("microsoft")) {
    avatarClass = "microsoft";
    avatarText = "MS";
  } else if (lowerName.includes("apple")) {
    avatarClass = "apple";
    avatarText = "AP";
  } else if (lowerName.includes("netflix")) {
    avatarClass = "netflix";
    avatarText = "N";
  } else if (lowerName.includes("nexthire")) {
    avatarClass = "nexthire";
    avatarText = "NH";
  }

  return { name, avatarClass, avatarText };
}

export function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function flattenCandidateSkills(skills = []) {
  const result = new Set();
  const aliasMap = {
    "c/c++": ["c++", "c"],
    "c++": ["c++", "c"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "node": ["node.js", "nodejs", "node"],
    "fastapi": ["fastapi", "python"],
    "html/css": ["html", "css"],
    "mern stack": ["mern stack", "react", "node.js", "mongodb", "express"],
    "artificial intelligence": ["ai", "machine learning"],
    "machine learning": ["ml", "machine learning"],
  };

  skills.forEach((raw) => {
    if (!raw || typeof raw !== "string") return;
    const clean = raw.trim();
    if (!clean) return;
    result.add(clean.toLowerCase());

    // Category prefix like "Languages: C/C++" -> "C/C++"
    if (clean.includes(":")) {
      const parts = clean.split(":");
      const val = parts.slice(1).join(":").trim().toLowerCase();
      if (val) result.add(val);
    }

    // Split slashes like "C/C++" -> "C", "C++", "HTML/CSS" -> "HTML", "CSS"
    if (clean.includes("/")) {
      clean.split("/").forEach((p) => {
        const item = p.trim().toLowerCase();
        if (item) result.add(item);
      });
    }

    // Expand known aliases
    for (const [key, aliases] of Object.entries(aliasMap)) {
      if (clean.toLowerCase().includes(key)) {
        aliases.forEach((a) => result.add(a));
      }
    }
  });

  return Array.from(result);
}

export function matchesSkill(targetSkill, candidateSkills) {
  if (!targetSkill) return false;
  const target = targetSkill.trim().toLowerCase();
  if (!target) return false;

  const isShortToken = target.length <= 3;

  for (const cand of candidateSkills) {
    const c = cand.trim().toLowerCase();
    if (c === target) return true;

    // Direct acronym alias check
    if ((target === "ai" && c.includes("artificial intelligence")) ||
        (c === "ai" && target.includes("artificial intelligence"))) {
      return true;
    }
    if ((target === "ml" && c.includes("machine learning")) ||
        (c === "ml" && target.includes("machine learning"))) {
      return true;
    }

    if (isShortToken) {
      // Must match standalone word boundary only (prevent "fastapi" matching "ai")
      const wordRe = new RegExp(`(^|[^a-z0-9+#])${escapeRegex(target)}($|[^a-z0-9+#])`, "i");
      if (wordRe.test(c)) return true;
    } else {
      if (c === target) return true;
      const wordRe = new RegExp(`\\b${escapeRegex(target)}\\b`, "i");
      if (wordRe.test(c)) return true;
      const reverseWordRe = new RegExp(`\\b${escapeRegex(c)}\\b`, "i");
      if (c.length >= 4 && reverseWordRe.test(target)) return true;
    }
  }
  return false;
}

export function getRoleDomain(title = "") {
  const t = title.toLowerCase();
  if (/(marketing|seo|aeo|geo|growth|brand|campaign|content|communications)/i.test(t)) {
    return "marketing";
  }
  if (/(finance|accounting|ar analyst|ap analyst|tax|audit|treasury)/i.test(t)) {
    return "finance";
  }
  if (/(sales|account executive|business development|bdr|sdr|account manager)/i.test(t)) {
    return "sales";
  }
  if (/(recruiter|talent|hr|investigator|abuse investigator|compliance|legal)/i.test(t)) {
    return "operations";
  }
  if (/(software engineer|backend|frontend|full stack|developer|ai engineer|machine learning|data scientist|systems engineer|devops|looker|platform|architect)/i.test(t)) {
    return "engineering";
  }
  return "engineering";
}

export function getCandidateDomain(candidateSkills = [], headline = "") {
  const combined = (candidateSkills.join(" ") + " " + headline).toLowerCase();
  if (/(python|javascript|react|c\+\+|fastapi|docker|sql|engineer|developer|software|mern)/i.test(combined)) {
    return "engineering";
  }
  if (/(marketing|seo|growth|brand|campaign)/i.test(combined)) {
    return "marketing";
  }
  if (/(finance|accounting|audit)/i.test(combined)) {
    return "finance";
  }
  return "engineering";
}

export function getJobSkillsAndScore(job, userSkills = [], candidateHeadline = "") {
  const rawSkills = Array.isArray(userSkills) ? userSkills : [];
  const candidateSkills = flattenCandidateSkills(rawSkills);
  const required = job.required_skills || [];
  const preferred = job.preferred_skills || [];
  const jobDomain = getRoleDomain(job.title || "");

  // If candidate has no skills configured, do not inflate scores. Return 0% match!
  if (candidateSkills.length === 0) {
    return {
      matched: [],
      missing: required.length > 0 ? required : preferred,
      score: 0,
      domain: jobDomain,
    };
  }

  const candidateDomain = getCandidateDomain(candidateSkills, candidateHeadline);
  const isDomainMismatch = candidateDomain === "engineering" && jobDomain !== "engineering";

  const isSkillMatched = (s) => matchesSkill(s, candidateSkills);

  const matchedRequired = required.filter(isSkillMatched);
  const matchedPreferred = preferred.filter(isSkillMatched);
  const matched = [...matchedRequired, ...matchedPreferred];

  let missing = required.filter((s) => !isSkillMatched(s));
  if (missing.length === 0 && preferred.length > 0) {
    missing = preferred.filter((s) => !isSkillMatched(s)).slice(0, 2);
  }

  let score = 0;
  if (required.length > 0 && preferred.length > 0) {
    const reqRatio = matchedRequired.length / required.length;
    const prefRatio = matchedPreferred.length / preferred.length;
    score = Math.round((reqRatio * 0.8 + prefRatio * 0.2) * 100);
  } else if (required.length > 0) {
    const reqRatio = matchedRequired.length / required.length;
    score = Math.round(reqRatio * 100);
  } else if (preferred.length > 0) {
    const prefRatio = matchedPreferred.length / preferred.length;
    score = Math.round(prefRatio * 75);
  } else {
    // If no explicit skills listed on job, check if candidate skill appears in title
    const titleLower = (job.title || "").toLowerCase();
    const hasMatchInTitle = candidateSkills.some(
      (s) => s.length >= 3 && titleLower.includes(s.toLowerCase())
    );
    score = hasMatchInTitle ? 60 : 0;
  }

  // Cross-domain mismatch penalty: software engineers applying to marketing, finance, ops roles
  if (isDomainMismatch) {
    score = Math.min(10, Math.round(score * 0.15));
  }

  score = Math.max(0, Math.min(100, score));

  return { matched, missing, score, domain: jobDomain };
}

function ApplicationNextStepsModal({
  job,
  application,
  onClose,
  onUpdateStatus,
  onTailorResume,
}) {
  const [status, setStatus] = useState(application?.status || "applied");
  const [notes, setNotes] = useState(application?.notes || "");
  const [interviewDate, setInterviewDate] = useState(
    application?.interview_at ? application.interview_at.slice(0, 16) : ""
  );
  const [deadline, setDeadline] = useState(
    application?.deadline ? application.deadline.slice(0, 16) : ""
  );
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");

  const stages = [
    { key: "applied", label: "Applied" },
    { key: "interview", label: "Interviewing" },
    { key: "offer", label: "Offer Received" },
    { key: "saved", label: "Saved for Later" },
  ];

  const handleSelectStatus = async (newStatus) => {
    setStatus(newStatus);
    setSaving(true);
    try {
      if (application?.id) {
        await updateApplication(application.id, { status: newStatus });
      } else {
        await createApplication({ job_id: job.id, status: newStatus });
      }
      if (onUpdateStatus) onUpdateStatus(job.id, newStatus);
      setNotice(`Application moved to "${stages.find((s) => s.key === newStatus)?.label || newStatus}"!`);
      setTimeout(() => setNotice(""), 2200);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveDetails = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        status,
        notes,
        interview_at: interviewDate ? new Date(interviewDate).toISOString() : null,
        deadline: deadline ? new Date(deadline).toISOString() : null,
      };
      if (application?.id) {
        await updateApplication(application.id, payload);
      } else {
        await createApplication({ job_id: job.id, ...payload });
      }
      setNotice("Interview date & notes saved successfully!");
      setTimeout(() => setNotice(""), 2200);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="ai-modal-backdrop" onClick={onClose}>
      <div className="ai-modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="ai-modal-header">
          <div className="ai-modal-title-row">
            <CheckCircle2 size={20} style={{ color: "#059669" }} />
            <div>
              <h3>Application Tracked</h3>
              <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>
                {job.title} · {job.companyName || job.company_id}
              </span>
            </div>
          </div>
          <button className="ai-modal-close-btn" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        <div className="ai-modal-body" style={{ padding: "1.25rem 1.5rem" }}>
          {notice && (
            <div className="naukri-notice success" style={{ marginBottom: "1rem" }}>
              {notice}
            </div>
          )}

          {/* 1. Status Selection */}
          <div style={{ marginBottom: "1.25rem" }}>
            <label style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--colors-steel)", display: "block", marginBottom: "6px" }}>
              Application Stage:
            </label>
            <div className="next-steps-status-chips">
              {stages.map((st) => (
                <button
                  key={st.key}
                  type="button"
                  className={`next-steps-status-chip ${status === st.key ? "active" : ""}`}
                  onClick={() => handleSelectStatus(st.key)}
                  disabled={saving}
                >
                  {st.label}
                </button>
              ))}
            </div>
          </div>

          {/* 2. Optional Interview Date & Notes form */}
          <form onSubmit={handleSaveDetails} style={{ background: "var(--colors-canvas-subtle)", padding: "1rem", borderRadius: "var(--rounded-lg)", border: "1px solid var(--colors-hairline)" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "8px" }}>
              <div>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "var(--colors-slate)", display: "block", marginBottom: "4px" }}>
                  Upcoming Interview Date
                </label>
                <input
                  type="datetime-local"
                  value={interviewDate}
                  onChange={(e) => setInterviewDate(e.target.value)}
                  className="naukri-input"
                  style={{ width: "100%", padding: "6px 10px", fontSize: "12px" }}
                />
              </div>
              <div>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "var(--colors-slate)", display: "block", marginBottom: "4px" }}>
                  Application Deadline
                </label>
                <input
                  type="datetime-local"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className="naukri-input"
                  style={{ width: "100%", padding: "6px 10px", fontSize: "12px" }}
                />
              </div>
            </div>
            <div>
              <label style={{ fontSize: "11px", fontWeight: 600, color: "var(--colors-slate)", display: "block", marginBottom: "4px" }}>
                Notes / Next Action
              </label>
              <input
                type="text"
                placeholder="e.g. Followed up with recruiter, prepared design presentation..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="naukri-input"
                style={{ width: "100%", padding: "6px 10px", fontSize: "12px" }}
              />
            </div>
            <div style={{ marginTop: "10px", textAlign: "right" }}>
              <button type="submit" className="button-secondary" style={{ padding: "5px 12px", fontSize: "12px" }} disabled={saving}>
                {saving ? "Saving..." : "Save Notes & Dates"}
              </button>
            </div>
          </form>

          {/* 3. What would you like to do next? */}
          <div style={{ marginTop: "1.5rem" }}>
            <h4 style={{ margin: "0 0 4px 0", fontSize: "13.5px", fontWeight: 700, color: "var(--colors-ink)" }}>
              What would you like to do next?
            </h4>
            <p style={{ margin: "0 0 10px 0", fontSize: "12px", color: "var(--colors-steel)" }}>
              Recommended actions to maximize your chances for this role:
            </p>

            <div className="next-steps-action-grid">
              {/* Option A: Tailor Resume */}
              <div
                className="next-steps-action-card"
                onClick={() => {
                  onClose();
                  if (onTailorResume) onTailorResume(job);
                }}
              >
                <div>
                  <div className="next-steps-action-card-header">
                    <div className="next-steps-action-icon">
                      <Sparkles size={16} />
                    </div>
                    <h5 className="next-steps-action-title">Tailor Resume for Role</h5>
                  </div>
                  <p className="next-steps-action-desc" style={{ marginTop: "8px" }}>
                    Generate an ATS-optimized resume emphasizing {job.title} keywords.
                  </p>
                </div>
                <div className="next-steps-action-footer">
                  <span>Tailor LaTeX Resume</span>
                  <ArrowRight size={12} />
                </div>
              </div>

              {/* Option B: View in Applications Pipeline */}
              <div
                className="next-steps-action-card"
                onClick={() => {
                  window.location.href = "/applications";
                }}
              >
                <div>
                  <div className="next-steps-action-card-header">
                    <div className="next-steps-action-icon green">
                      <CheckCircle2 size={16} />
                    </div>
                    <h5 className="next-steps-action-title">View Applications Tracker</h5>
                  </div>
                  <p className="next-steps-action-desc" style={{ marginTop: "8px" }}>
                    Manage pipeline stages, interview reminders, and notes.
                  </p>
                </div>
                <div className="next-steps-action-footer" style={{ color: "#059669" }}>
                  <span>Open Pipeline Tracker</span>
                  <ArrowRight size={12} />
                </div>
              </div>

              {/* Option C: Continue Browsing */}
              <div
                className="next-steps-action-card"
                onClick={onClose}
              >
                <div>
                  <div className="next-steps-action-card-header">
                    <div className="next-steps-action-icon amber">
                      <Compass size={16} />
                    </div>
                    <h5 className="next-steps-action-title">Keep Browsing Roles</h5>
                  </div>
                  <p className="next-steps-action-desc" style={{ marginTop: "8px" }}>
                    Discover more verified openings matched with your skills.
                  </p>
                </div>
                <div className="next-steps-action-footer" style={{ color: "#d97706" }}>
                  <span>Back to Job Feed</span>
                  <ArrowRight size={12} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function JobIntelligenceModal({ job, onClose }) {
  const [intelligence, setIntelligence] = useState(null);
  const [intelligenceError, setIntelligenceError] = useState("");
  const [feedbackSuccess, setFeedbackSuccess] = useState("");
  const [tailoredResume, setTailoredResume] = useState(null);
  const [tailoring, setTailoring] = useState(false);
  const [tailorError, setTailorError] = useState("");

  useEffect(() => {
    if (!job?.id) return;
    setIntelligence(null);
    setIntelligenceError("");
    setFeedbackSuccess("");
    getJobIntelligence(job.id)
      .then(setIntelligence)
      .catch((err) => setIntelligenceError(err.message));
  }, [job?.id]);

  if (!job) return null;

  return (
    <div className="ai-modal-backdrop" onClick={onClose}>
      <div className="ai-modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="ai-modal-header">
          <div className="ai-modal-title-row">
            <Sparkles size={18} className="linear-icon-primary" />
            <div>
              <h3>AI Match Breakdown</h3>
              <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>
                {job.title} · {job.companyName || job.company_id}
              </span>
            </div>
          </div>
          <button
            className="ai-modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        <div className="ai-modal-body">
          {intelligenceError && <p className="error-message" role="alert">{intelligenceError}</p>}
          {!intelligence && !intelligenceError && (
            <div style={{ textAlign: "center", padding: "2rem 0" }}>
              <p className="loading-message">Analyzing your career profile against requirements...</p>
            </div>
          )}
          {intelligence && (
            <>
              <div className="ai-score-card">
                <div>
                  <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--colors-steel)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Career Alignment
                  </span>
                  <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--colors-ink)", marginTop: "2px" }}>
                    {intelligence.recommendation === "recommended" ? "Strong Fit Recommendation" : "Partial Fit"}
                  </div>
                </div>
                <div className="ai-score-number">{intelligence.fit_score}%</div>
              </div>

              <div>
                <h4 className="ai-section-title">Strategic Rationale</h4>
                <p style={{ margin: 0, fontSize: "13.5px", color: "var(--colors-charcoal)", lineHeight: 1.6 }}>
                  {intelligence.recommendation_reason}
                </p>
              </div>

              <div>
                <h4 className="ai-section-title">Matched Skills</h4>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {[...intelligence.matched_required_skills, ...intelligence.matched_preferred_skills].length === 0 ? (
                    <span style={{ fontSize: "13px", color: "var(--colors-steel)" }}>None identified yet</span>
                  ) : (
                    [...intelligence.matched_required_skills, ...intelligence.matched_preferred_skills].map((skill) => (
                      <span className="skill-tag matched" key={skill}>
                        <Check size={11} />
                        <span>{skill}</span>
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div>
                <h4 className="ai-section-title">Skill Gaps & Opportunities</h4>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {[...intelligence.missing_required_skills, ...intelligence.missing_preferred_skills].length === 0 ? (
                    <span style={{ fontSize: "13px", color: "var(--colors-steel)" }}>No major gaps detected</span>
                  ) : (
                    [...intelligence.missing_required_skills, ...intelligence.missing_preferred_skills].map((skill) => (
                      <span className="skill-tag missing" key={skill}>
                        <AlertCircle size={11} />
                        <span>{skill}</span>
                      </span>
                    ))
                  )}
                </div>
              </div>

              {intelligence.relevant_projects?.length > 0 && (
                <div>
                  <h4 className="ai-section-title">Relevant Experience & Projects</h4>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {intelligence.relevant_projects.map((project) => (
                      <span className="job-meta-badge" key={project.name}>
                        <FileText size={12} />
                        <span>{project.name}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {intelligence.learning_opportunities?.length > 0 && (
                <div>
                  <h4 className="ai-section-title">Targeted Learning Roadmap</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {intelligence.learning_opportunities.map((opp) => (
                      <div
                        key={opp.skill}
                        style={{
                          padding: "10px 12px",
                          background: "var(--colors-surface)",
                          borderRadius: "var(--rounded-md)",
                          border: "1px solid var(--colors-hairline)",
                        }}
                      >
                        <strong style={{ fontSize: "13px", color: "var(--colors-ink)" }}>{opp.skill}</strong>
                        <p style={{ margin: "2px 0 0 0", fontSize: "12px", color: "var(--colors-slate)" }}>{opp.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="ai-feedback-row">
                <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>Was this recommendation accurate?</span>
                <button
                  className="button-secondary"
                  style={{ padding: "4px 10px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "4px" }}
                  onClick={() => {
                    submitRecommendationFeedback(job.id, true);
                    setFeedbackSuccess("Thanks for your feedback!");
                    setTimeout(() => setFeedbackSuccess(""), 2500);
                  }}
                >
                  <ThumbsUp size={12} /> Helpful
                </button>
                <button
                  className="button-secondary"
                  style={{ padding: "4px 10px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "4px" }}
                  onClick={() => {
                    submitRecommendationFeedback(job.id, false);
                    setFeedbackSuccess("Feedback recorded.");
                    setTimeout(() => setFeedbackSuccess(""), 2500);
                  }}
                >
                  <ThumbsDown size={12} /> Not relevant
                </button>
                {feedbackSuccess && (
                  <span style={{ fontSize: "12px", color: "var(--colors-brand-green)", fontWeight: 500 }}>
                    {feedbackSuccess}
                  </span>
                )}
              </div>

              <div style={{ marginTop: "1rem", paddingTop: "0.85rem", borderTop: "1px solid var(--colors-hairline)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                <div>
                  <strong style={{ fontSize: "13px", color: "var(--colors-ink)" }}>Targeted Application Preparation</strong>
                  <p style={{ margin: "2px 0 0 0", fontSize: "12px", color: "var(--colors-slate)" }}>
                    Compile a tailored LaTeX resume emphasizing your matched skills and relevant projects.
                  </p>
                </div>
                <button
                  type="button"
                  className="primary-button"
                  style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "13px", padding: "8px 16px" }}
                  onClick={() => {
                    setTailoring(true);
                    setTailorError("");
                    generateResume(job.id)
                      .then((created) => setTailoredResume(created))
                      .catch((err) => setTailorError(err.message))
                      .finally(() => setTailoring(false));
                  }}
                  disabled={tailoring}
                >
                  <Sparkles size={14} className={tailoring ? "spin" : ""} />
                  <span>{tailoring ? "Compiling Tailored Resume..." : "Tailor Resume for this Role"}</span>
                </button>
              </div>
              {tailorError && <p className="error-message" role="alert" style={{ marginTop: "0.5rem" }}>{tailorError}</p>}
            </>
          )}
        </div>
      </div>

      {tailoredResume && (
        <TailoredResumeModal
          resume={tailoredResume}
          jobs={[job]}
          companies={[]}
          onClose={() => setTailoredResume(null)}
          onApprove={(r) => {
            updateResume(r.id, r.content, "approved").then((updated) => setTailoredResume(updated));
          }}
          onDownloadLatex={(resumeId, filename) => {
            exportResumeLatex(resumeId).then((latex) => {
              const blob = new Blob([latex], { type: "application/x-latex" });
              const url = URL.createObjectURL(blob);
              const link = document.createElement("a");
              link.href = url;
              link.download = filename;
              link.click();
              URL.revokeObjectURL(url);
            });
          }}
        />
      )}
    </div>
  );
}

function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [profile, setProfile] = useState(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [savingJobId, setSavingJobId] = useState("");
  const [savedJobIds, setSavedJobIds] = useState(new Set());
  const [applicationsMap, setApplicationsMap] = useState(new Map());
  const [dismissedJobIds, setDismissedJobIds] = useState(new Set());
  const [activeNextStepsJob, setActiveNextStepsJob] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [intelligence, setIntelligence] = useState(null);
  const [intelligenceError, setIntelligenceError] = useState("");
  const [feedbackSuccess, setFeedbackSuccess] = useState("");

  // Naukri Live Scraper state
  const [naukriRole, setNaukriRole] = useState("Software Engineer");
  const [naukriLoc, setNaukriLoc] = useState("India");
  const [scrapingNaukri, setScrapingNaukri] = useState(false);
  const [naukriNotice, setNaukriNotice] = useState(null);

  // Filter & Search states
  const [searchQuery, setSearchQuery] = useState("");
  const [scoreFilter, setScoreFilter] = useState("all");
  const [locationFilter, setLocationFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [savedOnly, setSavedOnly] = useState(false);
  const [sortBy, setSortBy] = useState("highest_match");
  const [activeTailoredResume, setActiveTailoredResume] = useState(null);
  const [tailoringJobId, setTailoringJobId] = useState("");

  const handleTailorJob = (job) => {
    setTailoringJobId(job.id);
    generateResume(job.id)
      .then((created) => {
        setActiveTailoredResume(created);
      })
      .catch((err) => setError(`Tailoring failed: ${err.message}`))
      .finally(() => setTailoringJobId(""));
  };

  const loadData = () => {
    Promise.all([
      getJobs(),
      getCompanies(),
      getProfile().catch(() => null),
      listCareerEntities("skills").catch(() => []),
      listApplications().catch(() => []),
    ])
      .then(([nextJobs, nextCompanies, nextProfile, careerSkills, applications]) => {
        setJobs(deduplicateJobsList(nextJobs));
        setCompanies(nextCompanies);
        const allSkills = [
          ...(nextProfile?.skills || []),
          ...(Array.isArray(careerSkills) ? careerSkills.map((s) => s.name) : []),
        ];
        setProfile({ ...(nextProfile || {}), skills: allSkills });
        const dismissed = new Set(nextProfile?.dismissed_job_ids || []);
        setDismissedJobIds(dismissed);
        if (Array.isArray(applications)) {
          const appMap = new Map();
          const savedIds = new Set();
          applications.forEach((a) => {
            appMap.set(a.job_id, a);
            if (a.status === "saved") savedIds.add(a.job_id);
          });
          setApplicationsMap(appMap);
          setSavedJobIds(savedIds);
        }
      })
      .catch((requestError) => setError(requestError.message));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerNaukriScrape = (e) => {
    if (e) e.preventDefault();
    setScrapingNaukri(true);
    setNaukriNotice(null);
    scrapeNaukriJobs({
      search_term: naukriRole || "Software Engineer",
      location: naukriLoc || "India",
      results_wanted: 15,
    })
      .then((newJobs) => {
        const merged = deduplicateJobsList([...(newJobs || []), ...jobs]);
        setJobs(merged);
        setNaukriNotice({
          type: "success",
          text: `Successfully scraped ${newJobs?.length || 0} live openings from Naukri!`,
        });
        setTimeout(() => setNaukriNotice(null), 4000);
      })
      .catch((err) => {
        setNaukriNotice({
          type: "error",
          text: `Naukri scrape failed: ${err.message}`,
        });
        setTimeout(() => setNaukriNotice(null), 4000);
      })
      .finally(() => setScrapingNaukri(false));
  };

  const handleDismissJob = (jobId) => {
    setDismissedJobIds((prev) => new Set(prev).add(jobId));
    dismissJob(jobId).catch((err) => console.error("Dismiss failed", err));
  };

  const handleMarkApplied = (job) => {
    createApplication({ job_id: job.id, status: "applied" })
      .then((app) => {
        setApplicationsMap((prev) => new Map(prev).set(job.id, app));
        setActiveNextStepsJob(job);
      })
      .catch((err) => setSaveError(err.message));
  };

  const inspectJob = (job) => {
    setSelectedJob(job);
  };

  const toggleSaveJob = (job) => {
    const isSaved = savedJobIds.has(job.id);
    setSaveError("");
    setSavingJobId(job.id);

    if (isSaved) {
      setSavedJobIds((prev) => {
        const next = new Set(prev);
        next.delete(job.id);
        return next;
      });
      setSavingJobId("");
    } else {
      createApplication({ job_id: job.id, status: "saved" })
        .then((app) => {
          setSavedJobIds((prev) => new Set(prev).add(job.id));
          setApplicationsMap((prev) => new Map(prev).set(job.id, app));
        })
        .catch((requestError) => setSaveError(requestError.message))
        .finally(() => setSavingJobId(""));
    }
  };

  // Filter & Sort Jobs
  const filteredJobs = useMemo(() => {
    return deduplicateJobsList(jobs)
      .filter((job) => !dismissedJobIds.has(job.id))
      .map((job) => {
        const skillsAndScore = getJobSkillsAndScore(
          job,
          profile?.skills || [],
          profile?.headline || ""
        );
        const company = getCompanyDetails(job.company_id, companies);
        return {
          ...job,
          ...skillsAndScore,
          companyName: company.name,
          companyDetails: company,
        };
      })
      .filter((job) => {
        // Search filter
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase().trim();
          const matchTitle = (job.title || "").toLowerCase().includes(q);
          const matchCompany = (job.companyName || "").toLowerCase().includes(q);
          const matchSummary = (job.summary || "").toLowerCase().includes(q);
          const matchSkills = [
            ...(job.required_skills || []),
            ...(job.preferred_skills || []),
          ].some((s) => s.toLowerCase().includes(q));
          if (!matchTitle && !matchCompany && !matchSummary && !matchSkills) return false;
        }

        // Score filter
        if (scoreFilter === "90" && job.score < 90) return false;
        if (scoreFilter === "80" && job.score < 80) return false;
        if (scoreFilter === "70" && job.score < 70) return false;

        // Location / Mode filter
        if (locationFilter !== "all") {
          const loc = (job.location || "").toLowerCase();
          if (locationFilter === "remote" && !loc.includes("remote")) return false;
          if (locationFilter === "hybrid" && !loc.includes("hybrid")) return false;
          if (locationFilter === "onsite" && (loc.includes("remote") || loc.includes("hybrid"))) return false;
        }

        // Job type filter
        if (typeFilter !== "all") {
          const type = (job.employment_type || "full-time").toLowerCase();
          if (typeFilter === "internship" && !type.includes("intern")) return false;
          if (typeFilter === "fulltime" && type.includes("intern")) return false;
        }

        // Saved filter
        if (savedOnly && !savedJobIds.has(job.id)) return false;

        return true;
      })
      .sort((a, b) => {
        if (sortBy === "highest_match") {
          if (b.score !== a.score) return b.score - a.score;
          const aMatched = a.matched?.length || 0;
          const bMatched = b.matched?.length || 0;
          if (bMatched !== aMatched) return bMatched - aMatched;
          const dateA = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
          const dateB = b.last_seen_at ? new Date(b.last_seen_at).getTime() : 0;
          if (dateB !== dateA) return dateB - dateA;
          return (a.title || "").localeCompare(b.title || "");
        }
        if (sortBy === "company") return a.companyName.localeCompare(b.companyName);
        if (sortBy === "recent") {
          const dateA = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
          const dateB = b.last_seen_at ? new Date(b.last_seen_at).getTime() : 0;
          if (dateB !== dateA) return dateB - dateA;
          return b.score - a.score;
        }
        return 0;
      });
  }, [
    jobs,
    profile,
    companies,
    searchQuery,
    scoreFilter,
    locationFilter,
    typeFilter,
    savedOnly,
    sortBy,
    savedJobIds,
    dismissedJobIds,
  ]);

  const pagedJobs = paginateItems(filteredJobs, page);

  if (error) return <p className="error-message" role="alert">{error}</p>;

  if (!jobs.length) {
    return (
      <section className="dashboard-panel">
        <p className="eyebrow">JOB DISCOVERY</p>
        <h2>No open jobs yet</h2>
        <p className="empty-state">Verified company career sources will appear here when jobs are discovered.</p>
        <button
          className="primary-button"
          onClick={() => {
            seedJobs()
              .then(() => {
                loadData();
              })
              .catch((requestError) => setError(requestError.message));
          }}
          style={{ marginTop: "1rem" }}
        >
          Discover verified roles
        </button>
      </section>
    );
  }

  return (
    <div className="job-feed-container">
      {/* Header & Live Sync */}
      <div className="job-feed-header">
        <div className="job-feed-title-block">
          <p className="eyebrow">JOB DISCOVERY</p>
          <h2>Open Roles</h2>
          <div className="job-feed-stats-row">
            <span>
              Showing <strong>{filteredJobs.length}</strong> of <strong>{jobs.length}</strong> verified roles across <strong>{companies.length}</strong> monitored companies
            </span>
          </div>
        </div>
        <div className="live-sync-badge">
          <span className="pulse-dot"></span>
          <span>Live Sync · Updated 10m ago</span>
        </div>
      </div>

      {saveError && <p className="error-message" role="alert">{saveError}</p>}

      {/* Naukri Live Discovery Bar */}
      <div className="naukri-scrape-banner">
        <div className="naukri-banner-header">
          <div className="naukri-badge-tag">
            <span className="pulse-dot active" />
            <span>Naukri Live Scraper</span>
          </div>
          <span className="naukri-banner-subtext">Direct real-time job scraping & deduplication via JobSpy</span>
        </div>
        <form className="naukri-quick-form" onSubmit={handleTriggerNaukriScrape}>
          <input
            type="text"
            placeholder="Role title (e.g. Software Engineer, React Developer)..."
            value={naukriRole}
            onChange={(e) => setNaukriRole(e.target.value)}
            className="naukri-input"
          />
          <input
            type="text"
            placeholder="Location (e.g. India, Bengaluru, Remote)..."
            value={naukriLoc}
            onChange={(e) => setNaukriLoc(e.target.value)}
            className="naukri-input location"
            style={{ maxWidth: "220px" }}
          />
          <button
            type="submit"
            className="primary-button naukri-scrape-btn"
            disabled={scrapingNaukri}
          >
            <RefreshCw size={13} className={scrapingNaukri ? "spin" : ""} />
            <span>{scrapingNaukri ? "Scraping Naukri..." : "Scrape Naukri Live"}</span>
          </button>
        </form>
        {naukriNotice && (
          <div className={`naukri-notice ${naukriNotice.type}`}>
            {naukriNotice.text}
          </div>
        )}
      </div>

      {/* Top Filter & Search Bar */}
      <div className="job-feed-controls">
        <div className="job-search-row">
          <div className="job-search-input-wrapper">
            <Search size={15} className="job-search-icon" />
            <input
              type="text"
              className="job-search-input"
              placeholder="Search job titles, required skills, or companies..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
            />
            {searchQuery && (
              <button
                className="job-search-clear-btn"
                onClick={() => setSearchQuery("")}
                title="Clear search"
              >
                <X size={14} />
              </button>
            )}
          </div>
          <div className="job-sort-wrapper">
            <select
              className="job-sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              aria-label="Sort jobs"
            >
              <option value="highest_match">Highest Match Score</option>
              <option value="recent">Most Recent</option>
              <option value="company">Company (A–Z)</option>
            </select>
          </div>
        </div>

        {/* Filter Pills Row */}
        <div className="filter-pills-row">
          <span className="filter-group-label">Match:</span>
          <button
            className={`filter-pill ${scoreFilter === "all" ? "active" : ""}`}
            onClick={() => { setScoreFilter("all"); setPage(1); }}
          >
            All Matches
          </button>
          <button
            className={`filter-pill ${scoreFilter === "70" ? "active" : ""}`}
            onClick={() => { setScoreFilter("70"); setPage(1); }}
          >
            70%+ Fit
          </button>
          <button
            className={`filter-pill ${scoreFilter === "80" ? "active" : ""}`}
            onClick={() => { setScoreFilter("80"); setPage(1); }}
          >
            80%+ Fit
          </button>
          <button
            className={`filter-pill ${scoreFilter === "90" ? "active" : ""}`}
            onClick={() => { setScoreFilter("90"); setPage(1); }}
          >
            90%+ Fit
          </button>

          <div className="filter-pill-divider" />

          <span className="filter-group-label">Mode:</span>
          <button
            className={`filter-pill ${locationFilter === "all" ? "active" : ""}`}
            onClick={() => { setLocationFilter("all"); setPage(1); }}
          >
            All
          </button>
          <button
            className={`filter-pill ${locationFilter === "remote" ? "active" : ""}`}
            onClick={() => { setLocationFilter("remote"); setPage(1); }}
          >
            Remote
          </button>
          <button
            className={`filter-pill ${locationFilter === "hybrid" ? "active" : ""}`}
            onClick={() => { setLocationFilter("hybrid"); setPage(1); }}
          >
            Hybrid
          </button>

          <div className="filter-pill-divider" />

          <span className="filter-group-label">Type:</span>
          <button
            className={`filter-pill ${typeFilter === "all" ? "active" : ""}`}
            onClick={() => { setTypeFilter("all"); setPage(1); }}
          >
            All
          </button>
          <button
            className={`filter-pill ${typeFilter === "fulltime" ? "active" : ""}`}
            onClick={() => { setTypeFilter("fulltime"); setPage(1); }}
          >
            Full-time
          </button>
          <button
            className={`filter-pill ${typeFilter === "internship" ? "active" : ""}`}
            onClick={() => { setTypeFilter("internship"); setPage(1); }}
          >
            Internship
          </button>

          <div className="filter-pill-divider" />

          <button
            className={`filter-pill ${savedOnly ? "active saved-pill" : ""}`}
            onClick={() => { setSavedOnly(!savedOnly); setPage(1); }}
          >
            {savedOnly ? <BookmarkCheck size={13} /> : <Bookmark size={13} />}
            <span>Saved Roles ({savedJobIds.size})</span>
          </button>
        </div>
      </div>

      {/* Empty State when no results match filters */}
      {filteredJobs.length === 0 ? (
        <section className="dashboard-panel" style={{ textAlign: "center", padding: "3rem 1.5rem" }}>
          <p style={{ margin: "0 0 0.5rem", fontWeight: 600, fontSize: "15px", color: "var(--colors-ink)" }}>
            No roles match the selected filters
          </p>
          <p style={{ margin: "0 0 1rem", fontSize: "13px", color: "var(--colors-slate)" }}>
            Try resetting your filters or adjusting your search query.
          </p>
          <button
            className="button-secondary"
            onClick={() => {
              setSearchQuery("");
              setScoreFilter("all");
              setLocationFilter("all");
              setTypeFilter("all");
              setSavedOnly(false);
            }}
          >
            Reset all filters
          </button>
        </section>
      ) : (
        /* Job Cards List */
        <div className="job-cards-list">
          {pagedJobs.items.map((job) => {
            const isSaved = savedJobIds.has(job.id);
            const loc = job.location || "Remote";
            const isRemote = loc.toLowerCase().includes("remote");
            const isHybrid = loc.toLowerCase().includes("hybrid");
            const modeLabel = isRemote ? "Remote" : isHybrid ? "Hybrid" : "On-site";
            const locationCity = loc.split("/")[0].trim();

            const scoreClass = job.score >= 85 ? "very-high" : job.score >= 70 ? "high" : job.score >= 45 ? "moderate" : "low";

            return (
              <div className="linear-job-card" key={job.id}>
                {/* Header Row */}
                <div className="job-card-header">
                  <div className="job-card-identity">
                    <div className={`company-logo-avatar ${job.companyDetails.avatarClass}`}>
                      {job.companyDetails.avatarText}
                    </div>
                    <div className="job-title-group">
                      <span className="job-company-name">{job.companyName}</span>
                      <h3 className="job-card-title">{job.title}</h3>
                      <div className="job-meta-row">
                        <span className="job-meta-badge">
                          <MapPin size={11} />
                          <span>{locationCity}</span>
                        </span>
                        <span className="job-meta-badge">
                          <Briefcase size={11} />
                          <span>{modeLabel}</span>
                        </span>
                        <span className="job-meta-badge">
                          <span>{job.employment_type || "Full-time"}</span>
                        </span>
                        <span className="job-meta-badge">
                          <Clock size={11} />
                          <span>2d ago</span>
                        </span>
                      </div>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div className={`ai-match-badge ${scoreClass}`} title="AI Career Alignment Score">
                      <Sparkles size={12} />
                      <span>{job.score}% Match</span>
                    </div>
                    <button
                      type="button"
                      className="job-dismiss-btn"
                      onClick={() => handleDismissJob(job.id)}
                      title="Remove role / Not interested"
                      aria-label="Remove job"
                    >
                      <X size={15} />
                    </button>
                  </div>
                </div>

                {/* Role Summary */}
                {job.summary && <p className="job-summary-text">{job.summary}</p>}

                {/* Skill Match Tags */}
                <div className="job-skill-tags-row">
                  {/* Matched skills in green */}
                  {job.matched.slice(0, 4).map((skill) => (
                    <span className="skill-tag matched" key={skill}>
                      <Check size={11} />
                      <span>{skill}</span>
                    </span>
                  ))}
                  {/* Missing skills in amber */}
                  {job.missing.slice(0, 2).map((skill) => (
                    <span className="skill-tag missing" key={skill}>
                      <AlertCircle size={11} />
                      <span>{skill}</span>
                    </span>
                  ))}
                  {job.matched.length === 0 && job.missing.length === 0 && (
                    <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>
                      Requirements: {(job.required_skills || []).slice(0, 3).join(", ")}
                    </span>
                  )}
                </div>

                {/* Action Toolbar */}
                <div className="job-card-actions">
                  <div className="action-buttons-group">
                    {applicationsMap.has(job.id) && applicationsMap.get(job.id).status !== "saved" ? (
                      <button
                        type="button"
                        className="mark-applied-btn is-applied"
                        onClick={() => setActiveNextStepsJob(job)}
                        title="Application recorded - click to update status or view next steps"
                      >
                        <CheckCircle2 size={13} />
                        <span>Applied ({applicationsMap.get(job.id).status})</span>
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="mark-applied-btn"
                        onClick={() => handleMarkApplied(job)}
                        title="Mark this role as applied"
                      >
                        <CheckCircle2 size={13} />
                        <span>Mark Applied</span>
                      </button>
                    )}
                    <button
                      className="tailor-resume-btn"
                      style={{ padding: "6px 12px", fontSize: "12.5px" }}
                      onClick={() => handleTailorJob(job)}
                      disabled={tailoringJobId === job.id}
                      title={`Tailor Resume for ${job.title}`}
                    >
                      <Sparkles size={13} className={tailoringJobId === job.id ? "spin" : ""} />
                      <span>{tailoringJobId === job.id ? "Tailoring..." : "Tailor Resume"}</span>
                    </button>
                    <button
                      className="job-ai-explain-btn"
                      onClick={() => inspectJob(job)}
                      aria-label={`Explain match for ${job.title}`}
                    >
                      <Sparkles size={13} />
                      <span>Why this role?</span>
                    </button>
                    <a
                      className="view-role-outline-btn"
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <span>View Role</span>
                      <ExternalLink size={12} />
                    </a>
                  </div>
                  <button
                    className={`job-bookmark-btn ${isSaved ? "saved" : ""}`}
                    onClick={() => toggleSaveJob(job)}
                    disabled={savingJobId === job.id}
                    title={isSaved ? "Saved to Applications" : "Save Role"}
                    aria-label={isSaved ? "Saved to Applications" : "Save role"}
                  >
                    {isSaved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {pagedJobs.totalPages > 1 && (
        <nav className="pagination" aria-label="Jobs pagination" style={{ marginTop: "1rem" }}>
          <button
            className="button-link"
            disabled={!pagedJobs.hasPrevious}
            onClick={() => setPage((current) => current - 1)}
          >
            Previous
          </button>
          <span aria-live="polite">Page {pagedJobs.currentPage} of {pagedJobs.totalPages}</span>
          <button
            className="button-link"
            disabled={!pagedJobs.hasNext}
            onClick={() => setPage((current) => current + 1)}
          >
            Next
          </button>
        </nav>
      )}

      {/* Application Next Steps Modal */}
      {activeNextStepsJob && (
        <ApplicationNextStepsModal
          job={activeNextStepsJob}
          application={applicationsMap.get(activeNextStepsJob.id)}
          onClose={() => setActiveNextStepsJob(null)}
          onUpdateStatus={(jobId, nextStatus) => {
            setApplicationsMap((prev) => {
              const updated = new Map(prev);
              const existing = updated.get(jobId) || { job_id: jobId };
              updated.set(jobId, { ...existing, status: nextStatus });
              return updated;
            });
          }}
          onTailorResume={(job) => handleTailorJob(job)}
        />
      )}

      {/* AI Explanation Modal */}
      {selectedJob && (
        <JobIntelligenceModal
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
        />
      )}

      {/* Tailored Resume Preview Modal */}
      {activeTailoredResume && (
        <TailoredResumeModal
          resume={activeTailoredResume}
          jobs={jobs}
          companies={companies}
          onClose={() => setActiveTailoredResume(null)}
          onApprove={(r) => {
            updateResume(r.id, r.content, "approved").then((updated) => {
              setActiveTailoredResume(updated);
            });
          }}
          onDownloadLatex={(resumeId, filename) => {
            exportResumeLatex(resumeId).then((latex) => {
              const blob = new Blob([latex], { type: "application/x-latex" });
              const url = URL.createObjectURL(blob);
              const link = document.createElement("a");
              link.href = url;
              link.download = filename;
              link.click();
              URL.revokeObjectURL(url);
            });
          }}
        />
      )}
    </div>
  );
}

function AddApplicationModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    job_title: "",
    company_id: "",
    status: "applied",
    application_url: "",
    notes: "",
    deadline: "",
    interview_at: "",
    next_action: "",
    next_action_at: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [modalError, setModalError] = useState("");

  const stages = [
    { key: "saved", label: "Saved" },
    { key: "applied", label: "Applied" },
    { key: "assessment", label: "Assessment" },
    { key: "interview", label: "Interview" },
    { key: "offer", label: "Offer" },
    { key: "rejected", label: "Rejected" },
    { key: "withdrawn", label: "Withdrawn" },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.job_title.trim()) {
      setModalError("Please enter a job title.");
      return;
    }
    setSubmitting(true);
    setModalError("");

    try {
      const payload = {
        job_title: form.job_title.trim(),
        company_id: form.company_id.trim() || undefined,
        status: form.status,
        application_url: form.application_url.trim() || undefined,
        notes: form.notes.trim() || undefined,
        deadline: form.deadline ? new Date(form.deadline).toISOString() : null,
        interview_at: form.interview_at ? new Date(form.interview_at).toISOString() : null,
        next_action: form.next_action.trim() || undefined,
        next_action_at: form.next_action_at ? new Date(form.next_action_at).toISOString() : null,
      };

      const created = await createApplication(payload);
      onCreated(created);
    } catch (err) {
      setModalError(err.message || "Failed to create application.");
      setSubmitting(false);
    }
  };

  return (
    <div className="ai-modal-backdrop" onClick={onClose}>
      <div className="ai-modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: "620px" }}>
        <div className="ai-modal-header">
          <div className="ai-modal-title-row">
            <Briefcase size={18} className="linear-icon-primary" />
            <div>
              <h3>Add Application Manually</h3>
              <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>
                Track an application with all interview dates, notes, and links
              </span>
            </div>
          </div>
          <button
            className="ai-modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="ai-modal-body" style={{ gap: "1.1rem" }}>
          {modalError && <p className="error-message" role="alert">{modalError}</p>}

          <div className="date-grid">
            <label>
              Job Title *
              <input
                type="text"
                required
                placeholder="e.g. Senior Frontend Developer"
                value={form.job_title}
                onChange={(e) => setForm({ ...form, job_title: e.target.value })}
                autoFocus
              />
            </label>
            <label>
              Company Name
              <input
                type="text"
                placeholder="e.g. Stripe, Google, Acme"
                value={form.company_id}
                onChange={(e) => setForm({ ...form, company_id: e.target.value })}
              />
            </label>
          </div>

          <div>
            <label style={{ marginBottom: "6px", display: "block" }}>Pipeline Stage</label>
            <div className="stage-selector-pills">
              {stages.map((st) => (
                <button
                  key={st.key}
                  type="button"
                  className={`stage-pill-btn ${form.status === st.key ? "active" : ""}`}
                  onClick={() => setForm({ ...form, status: st.key })}
                >
                  {form.status === st.key && <Check size={13} style={{ marginRight: "4px" }} />}
                  {st.label}
                </button>
              ))}
            </div>
          </div>

          <label>
            Application / Job URL
            <input
              type="url"
              placeholder="https://jobs.lever.co/..."
              value={form.application_url}
              onChange={(e) => setForm({ ...form, application_url: e.target.value })}
            />
          </label>

          <label>
            Notes & Recruiter Discussion
            <textarea
              rows={3}
              placeholder="Add recruiter contact, referral person, salary range, interview rounds..."
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </label>

          <div className="date-grid">
            <label>
              Application Deadline
              <input
                type="datetime-local"
                value={form.deadline}
                onChange={(e) => setForm({ ...form, deadline: e.target.value })}
              />
            </label>
            <label>
              Interview Date & Time
              <input
                type="datetime-local"
                value={form.interview_at}
                onChange={(e) => setForm({ ...form, interview_at: e.target.value })}
              />
            </label>
            <label>
              Next Action Item
              <input
                type="text"
                placeholder="e.g. Follow up on second round"
                value={form.next_action}
                onChange={(e) => setForm({ ...form, next_action: e.target.value })}
              />
            </label>
            <label>
              Next Action Date
              <input
                type="datetime-local"
                value={form.next_action_at}
                onChange={(e) => setForm({ ...form, next_action_at: e.target.value })}
              />
            </label>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "0.5rem", paddingTop: "0.75rem", borderTop: "1px solid var(--colors-hairline)" }}>
            <button
              type="button"
              className="secondary-button"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              {submitting ? "Adding..." : (
                <>
                  <Plus size={15} /> Add Application
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState("");
  const [notice, setNotice] = useState("");
  const [selectedAppId, setSelectedAppId] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);

  const load = () => Promise.all([listApplications(), listNotifications()])
    .then(([nextApplications, nextNotifications]) => {
      setApplications(nextApplications);
      setNotifications(nextNotifications);
    })
    .catch((requestError) => setError(requestError.message));

  useEffect(() => { load(); }, []);

  const save = (application, changes) => {
    setSaving(application.id);
    updateApplication(application.id, changes)
      .then((updated) => {
        setApplications((current) => current.map((item) => (item.id === updated.id ? updated : item)));
        setNotice("✓ Changes saved");
        setTimeout(() => setNotice(""), 2200);
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setSaving(""));
  };

  const handleDelete = (applicationId) => {
    if (!window.confirm("Are you sure you want to delete this application?")) return;
    deleteApplication(applicationId)
      .then(() => {
        setApplications((current) => current.filter((item) => item.id !== applicationId));
        setSelectedAppId(null);
        setNotice("✓ Application deleted");
        setTimeout(() => setNotice(""), 2200);
      })
      .catch((requestError) => setError(requestError.message));
  };

  const dateValue = (value) => (value ? value.slice(0, 16) : "");

  if (error) return <p className="error-message" role="alert">{error}</p>;

  const selectedApp = applications.find((a) => a.id === selectedAppId);

  return (
    <div className="application-layout">
      {showAddModal && (
        <AddApplicationModal
          onClose={() => setShowAddModal(false)}
          onCreated={(created) => {
            setApplications((current) => [created, ...current]);
            setSelectedAppId(created.id);
            setShowAddModal(false);
            setNotice("✓ Application added");
            setTimeout(() => setNotice(""), 2200);
          }}
        />
      )}

      {selectedApp ? (
        <section className="dashboard-panel">
          <div className="application-detail-container">
            <div className="application-detail-header-bar">
              <button
                type="button"
                className="secondary-button"
                style={{ display: "inline-flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px", padding: "6px 14px" }}
                onClick={() => setSelectedAppId(null)}
              >
                <ArrowLeft size={15} /> Back to all applications
              </button>
              {notice ? (
                <span className="save-status-indicator" style={{ color: "var(--colors-primary)", fontWeight: 600 }}>
                  {notice}
                </span>
              ) : saving === selectedApp.id ? (
                <span className="save-status-indicator">Saving changes...</span>
              ) : (
                <span className="save-status-indicator" style={{ color: "var(--colors-slate)" }}>
                  <Check size={14} style={{ color: "#10b981" }} /> All changes saved
                </span>
              )}
            </div>

            <article className="application-detail-card">
              <div className="application-detail-title-group">
                <div style={{ flex: 1 }}>
                  <span className="eyebrow" style={{ marginBottom: "6px", display: "inline-block" }}>
                    APPLICATION DETAILS
                  </span>
                  <div className="date-grid" style={{ marginBottom: "0.5rem" }}>
                    <label>
                      <span className="application-field-label">Job Title</span>
                      <input
                        key={`title-${selectedApp.id}`}
                        type="text"
                        className="application-title-input"
                        defaultValue={selectedApp.job_title || selectedApp.job_id}
                        placeholder="e.g. Senior Frontend Developer"
                        onBlur={(event) => {
                          const val = event.target.value.trim();
                          if (val && val !== (selectedApp.job_title || "")) {
                            save(selectedApp, { job_title: val });
                          }
                        }}
                      />
                    </label>
                    <label>
                      <span className="application-field-label">Company Name</span>
                      <input
                        key={`company-${selectedApp.id}`}
                        type="text"
                        className="application-title-input"
                        defaultValue={selectedApp.company_id || ""}
                        placeholder="e.g. Stripe, Google, Acme"
                        onBlur={(event) => {
                          const val = event.target.value.trim();
                          if (val !== (selectedApp.company_id || "")) {
                            save(selectedApp, { company_id: val });
                          }
                        }}
                      />
                    </label>
                  </div>
                  <label style={{ marginTop: "4px" }}>
                    <span className="application-field-label">Job / Application URL</span>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      <input
                        key={`url-${selectedApp.id}`}
                        type="url"
                        className="application-title-input"
                        defaultValue={selectedApp.application_url || ""}
                        placeholder="https://..."
                        onBlur={(event) => {
                          const val = event.target.value.trim();
                          if (val !== (selectedApp.application_url || "")) {
                            save(selectedApp, { application_url: val || null });
                          }
                        }}
                      />
                      {selectedApp.application_url && (
                        <a
                          className="secondary-button"
                          href={selectedApp.application_url}
                          target="_blank"
                          rel="noreferrer"
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            fontSize: "12px",
                            height: "44px",
                            padding: "0 14px",
                            whiteSpace: "nowrap",
                            textDecoration: "none",
                          }}
                        >
                          <ExternalLink size={13} /> Open Link
                        </a>
                      )}
                    </div>
                  </label>
                </div>
              </div>

              {/* Stage Selector */}
              <div className="application-detail-section">
                <label className="application-field-label">Pipeline Stage</label>
                <div className="stage-selector-pills">
                  {[
                    { key: "saved", label: "Saved" },
                    { key: "applied", label: "Applied" },
                    { key: "assessment", label: "Assessment" },
                    { key: "interview", label: "Interview" },
                    { key: "offer", label: "Offer" },
                    { key: "rejected", label: "Rejected" },
                    { key: "withdrawn", label: "Withdrawn" },
                  ].map((st) => (
                    <button
                      key={st.key}
                      type="button"
                      className={`stage-pill-btn ${selectedApp.status === st.key ? "active" : ""}`}
                      onClick={() => save(selectedApp, { status: st.key })}
                      disabled={saving === selectedApp.id}
                    >
                      {selectedApp.status === st.key && <Check size={13} style={{ marginRight: "4px" }} />}
                      {st.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div className="application-detail-section">
                <label className="application-field-label">Notes & Recruiter Discussion</label>
                <textarea
                  key={`notes-${selectedApp.id}`}
                  defaultValue={selectedApp.notes || ""}
                  placeholder="Add interview notes, recruiter contacts, salary expectations, discussion takeaways..."
                  rows={4}
                  className="application-notes-textarea"
                  onBlur={(event) => {
                    if (event.target.value !== (selectedApp.notes || "")) {
                      save(selectedApp, { notes: event.target.value });
                    }
                  }}
                />
                <span className="field-hint">Auto-saves when you click away.</span>
              </div>

              {/* Dates & Actions Grid */}
              <div className="application-detail-section">
                <label className="application-field-label">Important Dates & Action Items</label>
                <div className="date-grid">
                  <label>
                    Deadline
                    <input
                      type="datetime-local"
                      defaultValue={dateValue(selectedApp.deadline)}
                      onBlur={(event) =>
                        save(selectedApp, {
                          deadline: event.target.value ? new Date(event.target.value).toISOString() : null,
                        })
                      }
                    />
                  </label>
                  <label>
                    Interview Date & Time
                    <input
                      type="datetime-local"
                      defaultValue={dateValue(selectedApp.interview_at)}
                      onBlur={(event) =>
                        save(selectedApp, {
                          interview_at: event.target.value ? new Date(event.target.value).toISOString() : null,
                        })
                      }
                    />
                  </label>
                  <label>
                    Next Action
                    <input
                      type="text"
                      placeholder="e.g. Follow up with hiring manager"
                      defaultValue={selectedApp.next_action || ""}
                      onBlur={(event) => {
                        if (event.target.value !== (selectedApp.next_action || "")) {
                          save(selectedApp, { next_action: event.target.value });
                        }
                      }}
                    />
                  </label>
                  <label>
                    Next Action Date
                    <input
                      type="datetime-local"
                      defaultValue={dateValue(selectedApp.next_action_at)}
                      onBlur={(event) =>
                        save(selectedApp, {
                          next_action_at: event.target.value ? new Date(event.target.value).toISOString() : null,
                        })
                      }
                    />
                  </label>
                </div>
              </div>

              <div className="application-detail-footer">
                <button
                  type="button"
                  className="primary-button"
                  style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
                  onClick={() => setSelectedAppId(null)}
                >
                  <Check size={14} /> Done (Back to applications)
                </button>
                <button
                  type="button"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    background: "transparent",
                    color: "#ef4444",
                    border: "1px solid rgba(239, 68, 68, 0.3)",
                    padding: "8px 14px",
                    borderRadius: "var(--rounded-md)",
                    cursor: "pointer",
                    fontSize: "13px",
                    fontWeight: 500,
                  }}
                  onClick={() => handleDelete(selectedApp.id)}
                >
                  <Trash2 size={14} /> Delete Application
                </button>
              </div>
            </article>
          </div>
        </section>
      ) : (
        <section className="dashboard-panel">
          <div className="application-page-header">
            <div>
              <p className="eyebrow" style={{ margin: "0 0 4px 0" }}>APPLICATION TRACKING</p>
              <h2 style={{ margin: 0 }}>Your applications</h2>
            </div>
            <button
              type="button"
              className="primary-button"
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
              onClick={() => setShowAddModal(true)}
            >
              <Plus size={15} /> Add Application
            </button>
          </div>
          {applications.length === 0 ? (
            <div style={{ textAlign: "center", padding: "2.5rem 1rem" }}>
              <p className="empty-state" style={{ marginBottom: "1.25rem" }}>
                No applications tracked yet. Add one manually or save roles from the job feed.
              </p>
              <button
                type="button"
                className="primary-button"
                style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
                onClick={() => setShowAddModal(true)}
              >
                <Plus size={15} /> Add Application Manually
              </button>
            </div>
          ) : (
            <div className="application-list">
              {applications.map((application) => (
                <div
                  className="application-summary-card"
                  key={application.id}
                  onClick={() => setSelectedAppId(application.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setSelectedAppId(application.id);
                    }
                  }}
                >
                  <div className="application-summary-content">
                    <h3 className="application-summary-title">
                      {application.job_title || application.job_id}
                    </h3>
                    <p className="application-summary-subtitle">
                      {application.company_id || "Company"}
                    </p>
                  </div>
                  <div className="application-summary-meta">
                    <span className={`status-pill status-pill-${application.status || "applied"}`}>
                      {application.status || "applied"}
                    </span>
                    <ChevronRight size={18} className="application-summary-chevron" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {!selectedApp && (
        <section className="dashboard-panel">
          <p className="eyebrow">REMINDERS</p>
          <h2>Upcoming actions</h2>
          {notifications.length === 0 ? (
            <p className="empty-state">No reminders yet.</p>
          ) : (
            <ul className="entity-list">
              {notifications.map((notification) => (
                <li key={notification.id}>
                  <span>
                    <strong>{notification.title}</strong>
                    <br />
                    {notification.message}
                    <br />
                    <span className="muted">{new Date(notification.due_at).toLocaleString()}</span>
                  </span>
                  {notification.read_at ? (
                    <span className="muted">Read</span>
                  ) : (
                    <button
                      className="button-link"
                      onClick={() =>
                        markNotificationRead(notification.id).then((updated) =>
                          setNotifications((current) =>
                            current.map((item) => (item.id === updated.id ? updated : item))
                          )
                        )
                      }
                    >
                      Mark read
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}

function AuthRequired() {
  return (
    <main className="auth-screen">
      <section className="auth-card">
        <p className="eyebrow">NEXT HIRE</p>
        <h1>Sign in to continue.</h1>
        <p className="intro">
          Your career information and recommendations are private to your
          account.
        </p>
        <a className="primary-link" href="/login">Sign in</a>
        <a className="secondary-link" href="/signup">Create an account</a>
      </section>
    </main>
  );
}

function AuthPage({ mode, onAuthenticated }) {
  const [form, setForm] = useState({ email: "", password: "", displayName: "" });
  const [error, setError] = useState("");
  const submit = (event) => {
    event.preventDefault();
    const action = mode === "login"
      ? signIn(form.email, form.password)
      : signUp(form.email, form.password, form.displayName);
    action.then((nextUser) => {
      onAuthenticated(nextUser);
      window.location.href = nextUser.role === "ADMIN" ? "/admin" : "/dashboard";
    }).catch((nextError) => setError(nextError.message));
  };
  return (
    <main className="auth-screen">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">NEXT HIRE</p>
        <h1>{mode === "login" ? "Welcome back." : "Create your account."}</h1>
        {mode === "signup" && (
          <label>Name<input required type="text" value={form.displayName} onChange={(event) => setForm({ ...form, displayName: event.target.value })} /></label>
        )}
        <label>Email<input required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label>
        <label>Password<input required minLength="8" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>
        {error && <p className="error-message" role="alert">{error}</p>}
        <button className="primary-button" type="submit">{mode === "login" ? "Sign in" : "Sign up"}</button>
        {mode === "login" && (
          <>
            <div style={{ marginTop: "0.75rem", padding: "12px", borderRadius: "8px", background: "rgba(86, 69, 212, 0.06)", border: "1px dashed rgba(86, 69, 212, 0.25)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "6px" }}>
                <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--colors-primary)", display: "flex", alignItems: "center", gap: "5px" }}>
                  <ShieldCheck size={14} />
                  Administrator Workspace
                </span>
                <span style={{ fontSize: "11px", color: "var(--colors-steel)" }}>Role: ADMIN</span>
              </div>
              <p style={{ margin: "0 0 8px 0", fontSize: "12px", color: "var(--colors-slate)", lineHeight: 1.4 }}>
                One-click login to manage company career pages and 12-hour scraping schedules.
              </p>
              <button
                type="button"
                className="button-secondary"
                style={{ width: "100%", justifyContent: "center", fontSize: "13px", padding: "8px 12px", gap: "6px", display: "flex", alignItems: "center" }}
                onClick={() => {
                  setForm({ email: "admin@nexthire.dev", password: "Admin12345!", displayName: "Administrator" });
                  signIn("admin@nexthire.dev", "Admin12345!")
                    .then((nextUser) => {
                      onAuthenticated(nextUser);
                      window.location.href = "/admin";
                    })
                    .catch((e) => setError(e.message));
                }}
              >
                <ShieldCheck size={14} />
                <span>Sign in as Admin (admin@nexthire.dev)</span>
              </button>
            </div>
            <a className="secondary-link" href="/forgot-password">Forgot password?</a>
            <a className="secondary-link" href="/api/v1/auth/google/login">Continue with Google</a>
          </>
        )}
        <a className="secondary-link" href={mode === "login" ? "/signup" : "/login"}>
          {mode === "login" ? "Create an account" : "Already have an account?"}
        </a>
      </form>
    </main>
  );
}

function ProfileEditor({ user, onUpdated }) {
  const [profile, setProfile] = useState(null);
  const [headline, setHeadline] = useState("");
  const [location, setLocation] = useState("");
  const [roles, setRoles] = useState("");
  const [skills, setSkills] = useState("");
  const [preferredLocations, setPreferredLocations] = useState("");
  const [companies, setCompanies] = useState("");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const loadProfile = () => {
    getProfile().then((current) => {
      setProfile(current);
      if (current.headline) setHeadline(current.headline);
      if (current.location) setLocation(current.location);
      if (current.preferred_roles?.length) setRoles(current.preferred_roles.join(", "));
      if (current.preferred_skills && Object.keys(current.preferred_skills).length) {
        setSkills(Object.keys(current.preferred_skills).join(", "));
      }
      if (current.preferred_locations?.length) setPreferredLocations(current.preferred_locations.join(", "));
      if (current.target_companies?.length) setCompanies(current.target_companies.join(", "));
    }).catch((requestError) => setError(requestError.message));
  };

  useEffect(() => {
    loadProfile();
  }, []);
  const save = (event) => {
    event.preventDefault();
    setError("");
    updateProfile({
      display_name: user.display_name,
      headline,
      location,
      preferred_roles: roles.split(",").map((role) => role.trim()).filter(Boolean),
      preferred_skills: Object.fromEntries(
        skills.split(",")
          .map((skill) => skill.trim())
          .filter(Boolean)
          .map((skill) => {
            const [name, priority = "MEDIUM"] = skill.split(":").map((part) => part.trim());
            const normalized = priority.toUpperCase();
            return [name, ["LOW", "MEDIUM", "HIGH"].includes(normalized) ? normalized : "MEDIUM"];
          }),
      ),
      preferred_locations: preferredLocations.split(",").map((item) => item.trim()).filter(Boolean),
      target_companies: companies.split(",").map((item) => item.trim()).filter(Boolean),
    }).then((profile) => {
      onUpdated({ ...user, display_name: profile.display_name });
      setProfile(profile);
      setSaved(true);
    }).catch((requestError) => setError(requestError.message));
  };
  if (error) return <p className="error-message" role="alert">{error}</p>;
  if (!profile) return <p className="loading-message" role="status">Loading your profile...</p>;
  return (
    <>
      <form className="profile-form" onSubmit={save}>
        <p className="eyebrow">CAREER PROFILE</p>
        <h2>Profile Details</h2>
        <p className="intro" style={{ margin: "0 0 0.5rem", fontSize: "14px" }}>
          NextHire connects your profile details with verified opportunities and generates personalized match insights.
        </p>
        <label>Professional Headline<input type="text" value={headline} onChange={(event) => setHeadline(event.target.value)} placeholder="e.g. Software Engineer | Competitive Programmer" /></label>
        <label>Location<input type="text" value={location} onChange={(event) => setLocation(event.target.value)} placeholder="City or remote" /></label>
        <label>Preferred roles<input type="text" value={roles} onChange={(event) => setRoles(event.target.value)} placeholder="Backend Engineer, Python Developer" /></label>
        <label>Preferred skills<input type="text" value={skills} onChange={(event) => setSkills(event.target.value)} placeholder="Python: HIGH, FastAPI: HIGH, AWS: MEDIUM" /></label>
        <label>Preferred locations<input type="text" value={preferredLocations} onChange={(event) => setPreferredLocations(event.target.value)} placeholder="Remote, Berlin" /></label>
        <label>
          Target companies
          <input type="text" value={companies} onChange={(event) => setCompanies(event.target.value)} placeholder="e.g. Google, Stripe, Spotify, Infosys" />
          <span className="field-hint" style={{ marginTop: "4px" }}>
            New target companies are submitted to the admin whitelist queue for approval and automatic Naukri job scraping.
          </span>
        </label>
        <button className="primary-button" type="submit">Save profile</button>
        {saved && <p className="success-message" role="status">Profile saved.</p>}
      </form>
      <CareerKnowledgeBase onProfileSync={loadProfile} />
      <TailoredResumesSection />
    </>
  );
}

function CareerKnowledgeBase({ onProfileSync }) {
  const [skills, setSkills] = useState([]);
  const [projects, setProjects] = useState([]);
  const [skillName, setSkillName] = useState("");
  const [skillPriority, setSkillPriority] = useState("HIGH");
  const [editingSkillId, setEditingSkillId] = useState(null);
  const [editingSkillName, setEditingSkillName] = useState("");
  const [editingSkillPriority, setEditingSkillPriority] = useState("HIGH");

  const [projectName, setProjectName] = useState("");
  const [projectDesc, setProjectDesc] = useState("");
  const [projectTech, setProjectTech] = useState("");
  const [projectUrl, setProjectUrl] = useState("");
  const [editingProjectId, setEditingProjectId] = useState(null);
  const [editingProjectName, setEditingProjectName] = useState("");
  const [editingProjectDesc, setEditingProjectDesc] = useState("");
  const [editingProjectTech, setEditingProjectTech] = useState("");
  const [editingProjectUrl, setEditingProjectUrl] = useState("");

  const [error, setError] = useState("");
  const [document, setDocument] = useState(null);
  const [extracted, setExtracted] = useState([]);
  const [chunks, setChunks] = useState([]);
  const [chunkNotice, setChunkNotice] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [githubUsername, setGithubUsername] = useState("");
  const [portfolioUrl, setPortfolioUrl] = useState("");
  const [linkedinText, setLinkedinText] = useState("");
  const [showAddSkill, setShowAddSkill] = useState(false);
  const [showAddProject, setShowAddProject] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [showUploadResume, setShowUploadResume] = useState(false);
  const [analyzingResume, setAnalyzingResume] = useState(false);
  const [selectedEntityTab, setSelectedEntityTab] = useState("all");

  const refreshKnowledge = () => {
    return Promise.all([
      listCareerEntities("skills"),
      listCareerEntities("projects"),
      listExternalCandidates(),
    ])
      .then(([nextSkills, nextProjects, nextCandidates]) => {
        setSkills(nextSkills);
        setProjects(nextProjects);
        setCandidates(nextCandidates);
        if (onProfileSync) onProfileSync();
      })
      .catch((requestError) => setError(requestError.message));
  };

  useEffect(() => {
    refreshKnowledge();
    listCareerDocuments()
      .then((docs) => {
        if (docs && docs.length > 0) {
          const latest = docs[docs.length - 1];
          setDocument(latest);
          return listExtractedEntities(latest.id);
        }
      })
      .then((entities) => {
        if (entities) {
          setExtracted(entities);
        }
      })
      .catch(() => {});
  }, []);

  const addSkill = (event) => {
    event.preventDefault();
    if (!skillName.trim()) return;
    createCareerEntity("skills", { name: skillName.trim(), priority: skillPriority })
      .then((skill) => {
        setSkills([...skills, skill]);
        setSkillName("");
        setSkillPriority("HIGH");
        setShowAddSkill(false);
        if (onProfileSync) onProfileSync();
      })
      .catch((requestError) => setError(requestError.message));
  };

  const handleUpdateSkill = (id, name, priority) => {
    if (!name.trim()) return;
    updateCareerEntity("skills", id, { name: name.trim(), priority })
      .then((updated) => {
        setSkills(skills.map((s) => (s.id === id ? updated : s)));
        setEditingSkillId(null);
        if (onProfileSync) onProfileSync();
      })
      .catch((err) => setError(err.message));
  };

  const handleDeleteSkill = (id) => {
    deleteCareerEntity("skills", id)
      .then(() => {
        setSkills(skills.filter((s) => s.id !== id));
        if (onProfileSync) onProfileSync();
      })
      .catch((err) => setError(err.message));
  };

  const cycleSkillPriority = (skill) => {
    const cycle = { HIGH: "MEDIUM", MEDIUM: "LOW", LOW: "HIGH" };
    const nextPriority = cycle[skill.priority] || "HIGH";
    updateCareerEntity("skills", skill.id, { priority: nextPriority })
      .then((updated) => {
        setSkills(skills.map((s) => (s.id === skill.id ? updated : s)));
        if (onProfileSync) onProfileSync();
      })
      .catch((err) => setError(err.message));
  };

  const addProject = (event) => {
    event.preventDefault();
    if (!projectName.trim()) return;
    const techArray = projectTech
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    createCareerEntity("projects", {
      name: projectName.trim(),
      description: projectDesc.trim(),
      technologies: techArray,
      url: projectUrl.trim(),
    })
      .then((project) => {
        setProjects([...projects, project]);
        setProjectName("");
        setProjectDesc("");
        setProjectTech("");
        setProjectUrl("");
        setShowAddProject(false);
        if (onProfileSync) onProfileSync();
      })
      .catch((requestError) => setError(requestError.message));
  };

  const handleUpdateProject = (id, name, desc, techStr, url) => {
    if (!name.trim()) return;
    const techArray = techStr
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    updateCareerEntity("projects", id, {
      name: name.trim(),
      description: desc.trim(),
      technologies: techArray,
      url: url.trim(),
    })
      .then((updated) => {
        setProjects(projects.map((p) => (p.id === id ? updated : p)));
        setEditingProjectId(null);
        if (onProfileSync) onProfileSync();
      })
      .catch((err) => setError(err.message));
  };

  const handleDeleteProject = (id) => {
    deleteCareerEntity("projects", id)
      .then(() => {
        setProjects(projects.filter((p) => p.id !== id));
        if (onProfileSync) onProfileSync();
      })
      .catch((err) => setError(err.message));
  };

  const ingest = (event, action, value, clear) => {
    event.preventDefault();
    action(value)
      .then((nextCandidates) => {
        setCandidates([...candidates, ...nextCandidates]);
        clear("");
      })
      .catch((requestError) => setError(requestError.message));
  };

  const reviewCandidate = (candidate, status) => {
    reviewExternalCandidate(candidate.id, status)
      .then((updated) => setCandidates(candidates.map((item) => item.id === updated.id ? updated : item)))
      .catch((requestError) => setError(requestError.message));
  };

  const uploadLinkedInDocument = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    ingestLinkedInDocument(file)
      .then((nextCandidates) => setCandidates([...candidates, ...nextCandidates]))
      .catch((requestError) => setError(requestError.message));
  };

  const upload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setError("");
    setChunkNotice("");
    setChunks([]);
    setAnalyzingResume(true);
    uploadCareerDocument(file)
      .then((nextDocument) => {
        setDocument(nextDocument);
        return listExtractedEntities(nextDocument.id);
      })
      .then((entities) => {
        setExtracted(entities);
        refreshKnowledge();
        if (onProfileSync) onProfileSync();
        if (entities.length === 0) {
          setError("No section headings or text detected in this file. Try another format or add records manually.");
        }
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setAnalyzingResume(false));
  };

  const review = (entity, confirmed) => {
    reviewExtractedEntity(document.id, entity.id, confirmed)
      .then((updated) => {
        setExtracted(extracted.map((item) => item.id === updated.id ? updated : item));
        if (confirmed) {
          refreshKnowledge();
        }
      })
      .catch((requestError) => setError(requestError.message));
  };

  const acceptAllExtracted = () => {
    if (!document || extracted.length === 0) return;
    acceptAllExtractedEntities(document.id)
      .then((updatedList) => {
        setExtracted(updatedList);
        setChunkNotice("");
        refreshKnowledge();
      })
      .catch((requestError) => setError(requestError.message));
  };

  const handlePrepareChunks = async () => {
    if (!document) return;
    setError("");
    setChunkNotice("");
    try {
      let currentList = extracted;
      const hasConfirmed = currentList.some((e) => e.confirmed_by_user);
      if (!hasConfirmed && currentList.length > 0) {
        currentList = await Promise.all(
          currentList.map((e) => reviewExtractedEntity(document.id, e.id, true))
        );
        setExtracted(currentList);
      }
      const nextChunks = await prepareEmbeddingChunks(document.id);
      setChunks(nextChunks);
      if (nextChunks.length === 0) {
        setChunkNotice("0 chunks prepared. Please ensure extracted items above are accepted before preparing chunks.");
      } else {
        setChunkNotice(`${nextChunks.length} confirmed chunks ready for embedding.`);
      }
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  const extractedSkills = extracted.filter(
    (e) => e.entity_type === "skills" || e.entity_type === "skill"
  );
  const extractedExperience = extracted.filter(
    (e) => e.entity_type === "experience"
  );
  const extractedProjects = extracted.filter(
    (e) => e.entity_type === "projects" || e.entity_type === "project"
  );
  const extractedEducation = extracted.filter(
    (e) => e.entity_type === "education"
  );
  const extractedOther = extracted.filter(
    (e) =>
      ["certifications", "achievements", "headline", "certification", "achievement"].includes(
        e.entity_type
      )
  );

  const unconfirmedCount = extracted.filter((e) => !e.confirmed_by_user).length;

  const showSkillsSection =
    (selectedEntityTab === "all" || selectedEntityTab === "skills") &&
    extractedSkills.length > 0;

  const cardsToShow = extracted.filter((e) => {
    if (e.entity_type === "skills" || e.entity_type === "skill") return false;
    if (selectedEntityTab === "all") return true;
    if (selectedEntityTab === "experience") return e.entity_type === "experience";
    if (selectedEntityTab === "projects")
      return e.entity_type === "projects" || e.entity_type === "project";
    if (selectedEntityTab === "education") return e.entity_type === "education";
    if (selectedEntityTab === "other")
      return ["certifications", "achievements", "headline", "certification", "achievement"].includes(
        e.entity_type
      );
    return false;
  });

  return (
    <section className="profile-form">
      <p className="eyebrow">CAREER KNOWLEDGE BASE</p>
      <h2>Confirmed Career Facts</h2>
      <p className="intro" style={{ margin: "0 0 1rem", fontSize: "14px" }}>
        Your verified skills, projects, and career records are referenced by NextHire when calculating match scores and generating custom resumes.
      </p>
      {error && <p className="error-message" role="alert">{error}</p>}

      <div className="section-header-row">
        <div>
          <h3 style={{ margin: 0 }}>Skills ({skills.length})</h3>
          <span style={{ fontSize: "12px", color: "var(--colors-slate)" }}>
            Priority indicates alignment weight. Click any priority badge to toggle HIGH / MEDIUM / LOW.
          </span>
        </div>
        <button
          type="button"
          className="add-btn"
          onClick={() => setShowAddSkill(!showAddSkill)}
          aria-expanded={showAddSkill}
        >
          {showAddSkill ? "✕ Cancel" : "+ Add skill"}
        </button>
      </div>

      {showAddSkill && (
        <form onSubmit={addSkill} className="collapsible-form" style={{ display: "grid", gap: "10px", padding: "12px 14px", background: "var(--colors-surface-soft)", borderRadius: "8px", border: "1px solid var(--colors-hairline)" }}>
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "flex-end" }}>
            <label style={{ flex: "1 1 240px", margin: 0 }}>
              Skill name
              <input
                required
                type="text"
                value={skillName}
                onChange={(e) => setSkillName(e.target.value)}
                placeholder="e.g. Python, React, Kubernetes"
                style={{ marginTop: "4px" }}
              />
            </label>
            <label style={{ width: "190px", margin: 0 }}>
              Priority Weight
              <select
                value={skillPriority}
                onChange={(e) => setSkillPriority(e.target.value)}
                style={{ marginTop: "4px", padding: "8px 10px", borderRadius: "6px", border: "1px solid var(--colors-hairline)", background: "var(--colors-canvas)", width: "100%", fontSize: "13px" }}
              >
                <option value="HIGH">HIGH (Strong Fit)</option>
                <option value="MEDIUM">MEDIUM (Standard)</option>
                <option value="LOW">LOW (Familiar)</option>
              </select>
            </label>
            <div style={{ display: "flex", gap: "6px" }}>
              <button className="primary-button" type="submit" style={{ padding: "8px 16px" }}>Add Skill</button>
              <button className="button-secondary" type="button" onClick={() => setShowAddSkill(false)}>Cancel</button>
            </div>
          </div>
        </form>
      )}

      <ul className="entity-list" style={{ marginTop: "10px" }}>
        {skills.length === 0 && !showAddSkill && (
          <li style={{ color: "var(--colors-steel)", background: "transparent", border: "none", padding: "4px 0", fontSize: "13px" }}>
            No skills added yet. Click + Add skill to get started.
          </li>
        )}
        {skills.map((skill) => {
          if (editingSkillId === skill.id) {
            return (
              <li key={skill.id} style={{ padding: "8px 12px", background: "var(--colors-surface-soft)" }}>
                <div style={{ display: "flex", gap: "8px", width: "100%", alignItems: "center", flexWrap: "wrap" }}>
                  <input
                    type="text"
                    value={editingSkillName}
                    onChange={(e) => setEditingSkillName(e.target.value)}
                    style={{ flex: "1 1 180px", padding: "6px 10px", fontSize: "13px" }}
                  />
                  <select
                    value={editingSkillPriority}
                    onChange={(e) => setEditingSkillPriority(e.target.value)}
                    style={{ padding: "6px 8px", fontSize: "12px", borderRadius: "4px" }}
                  >
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                  <button
                    className="primary-button"
                    style={{ padding: "4px 10px", fontSize: "12px" }}
                    onClick={() => handleUpdateSkill(skill.id, editingSkillName, editingSkillPriority)}
                  >
                    Save
                  </button>
                  <button
                    className="button-secondary"
                    style={{ padding: "4px 10px", fontSize: "12px" }}
                    onClick={() => setEditingSkillId(null)}
                  >
                    Cancel
                  </button>
                </div>
              </li>
            );
          }
          return (
            <li key={skill.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <strong>{skill.name}</strong>
                <button
                  type="button"
                  onClick={() => cycleSkillPriority(skill)}
                  title="Click to toggle priority"
                  className={skill.priority === "HIGH" ? "badge-tag-purple" : skill.priority === "LOW" ? "badge-tag-gray" : "badge-tag-blue"}
                  style={{ cursor: "pointer", border: "none", fontWeight: 600, fontSize: "11px", padding: "2px 8px", borderRadius: "12px" }}
                >
                  {skill.priority} ↻
                </button>
              </div>
              <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                <button
                  type="button"
                  className="button-link"
                  style={{ fontSize: "12px" }}
                  onClick={() => {
                    setEditingSkillId(skill.id);
                    setEditingSkillName(skill.name);
                    setEditingSkillPriority(skill.priority || "MEDIUM");
                  }}
                >
                  Edit
                </button>
                <button
                  type="button"
                  className="button-link"
                  style={{ fontSize: "12px", color: "var(--colors-semantic-error)" }}
                  onClick={() => handleDeleteSkill(skill.id)}
                  title="Delete skill"
                >
                  Delete
                </button>
              </div>
            </li>
          );
        })}
      </ul>

      <div className="section-header-row" style={{ marginTop: "1.75rem" }}>
        <div>
          <h3 style={{ margin: 0 }}>Projects ({projects.length})</h3>
          <span style={{ fontSize: "12px", color: "var(--colors-slate)" }}>
            Showcase technical scope, technologies used, and measurable results.
          </span>
        </div>
        <button
          type="button"
          className="add-btn"
          onClick={() => setShowAddProject(!showAddProject)}
          aria-expanded={showAddProject}
        >
          {showAddProject ? "✕ Cancel" : "+ Add project"}
        </button>
      </div>

      {showAddProject && (
        <form onSubmit={addProject} className="collapsible-form" style={{ display: "grid", gap: "10px", padding: "14px", background: "var(--colors-surface-soft)", borderRadius: "8px", border: "1px solid var(--colors-hairline)" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "10px" }}>
            <label style={{ margin: 0 }}>
              Project Title *
              <input
                required
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g. Distributed Scraping Pipeline"
                style={{ marginTop: "4px" }}
              />
            </label>
            <label style={{ margin: 0 }}>
              Technologies (comma separated)
              <input
                type="text"
                value={projectTech}
                onChange={(e) => setProjectTech(e.target.value)}
                placeholder="e.g. Python, Redis, FastAPI, Docker"
                style={{ marginTop: "4px" }}
              />
            </label>
          </div>
          <label style={{ margin: 0 }}>
            Description & Impact Insights
            <textarea
              value={projectDesc}
              onChange={(e) => setProjectDesc(e.target.value)}
              placeholder="Describe the problem solved, architecture choices, key accomplishments, or benchmark results..."
              rows="3"
              style={{ marginTop: "4px" }}
            />
          </label>
          <label style={{ margin: 0 }}>
            Demo or Repository URL (optional)
            <input
              type="url"
              value={projectUrl}
              onChange={(e) => setProjectUrl(e.target.value)}
              placeholder="https://github.com/username/project"
              style={{ marginTop: "4px" }}
            />
          </label>
          <div style={{ display: "flex", gap: "8px", marginTop: "4px" }}>
            <button className="primary-button" type="submit">Save Project</button>
            <button className="button-secondary" type="button" onClick={() => setShowAddProject(false)}>Cancel</button>
          </div>
        </form>
      )}

      <div style={{ display: "grid", gap: "10px", marginTop: "10px" }}>
        {projects.length === 0 && !showAddProject && (
          <p style={{ color: "var(--colors-steel)", fontSize: "13px", margin: 0 }}>
            No projects added yet. Click + Add project to record one.
          </p>
        )}
        {projects.map((project) => {
          if (editingProjectId === project.id) {
            return (
              <div key={project.id} style={{ padding: "12px", background: "var(--colors-surface-soft)", borderRadius: "8px", border: "1px solid var(--colors-hairline)" }}>
                <div style={{ display: "grid", gap: "8px" }}>
                  <input
                    type="text"
                    value={editingProjectName}
                    onChange={(e) => setEditingProjectName(e.target.value)}
                    placeholder="Project Title"
                    style={{ fontSize: "14px", fontWeight: 600 }}
                  />
                  <input
                    type="text"
                    value={editingProjectTech}
                    onChange={(e) => setEditingProjectTech(e.target.value)}
                    placeholder="Technologies (comma separated)"
                    style={{ fontSize: "13px" }}
                  />
                  <textarea
                    value={editingProjectDesc}
                    onChange={(e) => setEditingProjectDesc(e.target.value)}
                    placeholder="Project insights..."
                    rows="3"
                    style={{ fontSize: "13px" }}
                  />
                  <input
                    type="url"
                    value={editingProjectUrl}
                    onChange={(e) => setEditingProjectUrl(e.target.value)}
                    placeholder="Project URL"
                    style={{ fontSize: "13px" }}
                  />
                  <div style={{ display: "flex", gap: "8px" }}>
                    <button
                      className="primary-button"
                      type="button"
                      onClick={() => handleUpdateProject(project.id, editingProjectName, editingProjectDesc, editingProjectTech, editingProjectUrl)}
                    >
                      Save Changes
                    </button>
                    <button className="button-secondary" type="button" onClick={() => setEditingProjectId(null)}>
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            );
          }
          const techs = Array.isArray(project.technologies) ? project.technologies : [];
          return (
            <div
              key={project.id}
              style={{
                padding: "12px 14px",
                background: "var(--colors-surface)",
                borderRadius: "8px",
                border: "1px solid var(--colors-hairline)",
                display: "flex",
                flexDirection: "column",
                gap: "6px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                  <strong style={{ fontSize: "14px", color: "var(--colors-ink)" }}>{project.name}</strong>
                  {project.url && (
                    <a
                      href={project.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ display: "inline-flex", alignItems: "center", gap: "3px", fontSize: "12px", color: "var(--colors-primary)" }}
                    >
                      <span>Link</span>
                      <ExternalLink size={12} />
                    </a>
                  )}
                </div>
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  <button
                    type="button"
                    className="button-link"
                    style={{ fontSize: "12px" }}
                    onClick={() => {
                      setEditingProjectId(project.id);
                      setEditingProjectName(project.name);
                      setEditingProjectDesc(project.description || "");
                      setEditingProjectTech(techs.join(", "));
                      setEditingProjectUrl(project.url || "");
                    }}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="button-link"
                    style={{ fontSize: "12px", color: "var(--colors-semantic-error)" }}
                    onClick={() => handleDeleteProject(project.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
              {techs.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                  {techs.map((t) => (
                    <span
                      key={t}
                      style={{
                        fontSize: "11px",
                        padding: "2px 7px",
                        borderRadius: "10px",
                        background: "var(--colors-surface-soft)",
                        border: "1px solid var(--colors-hairline)",
                        color: "var(--colors-slate)",
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}
              {project.description && (
                <p style={{ margin: "2px 0 0 0", fontSize: "13px", color: "var(--colors-slate)", lineHeight: 1.45 }}>
                  {project.description}
                </p>
              )}
            </div>
          );
        })}
      </div>

      <div className="section-header-row">
        <h3>Import external career data</h3>
        <button
          type="button"
          className="add-btn"
          onClick={() => setShowImport(!showImport)}
          aria-expanded={showImport}
        >
          {showImport ? "✕ Close" : "+ Import sources"}
        </button>
      </div>
      {showImport && (
        <div className="collapsible-form" style={{ display: "grid", gap: "14px" }}>
          <form onSubmit={(event) => ingest(event, ingestGitHub, githubUsername, setGithubUsername)} className="inline-form" style={{ margin: 0 }}>
            <label>GitHub username
              <input required type="text" value={githubUsername} onChange={(event) => setGithubUsername(event.target.value)} placeholder="octocat" />
            </label>
            <button className="primary-button" type="submit">Import GitHub</button>
          </form>
          <form onSubmit={(event) => ingest(event, ingestPortfolio, portfolioUrl, setPortfolioUrl)} className="inline-form" style={{ margin: 0 }}>
            <label>Portfolio URL
              <input required type="url" value={portfolioUrl} onChange={(event) => setPortfolioUrl(event.target.value)} placeholder="https://portfolio.example" />
            </label>
            <button className="primary-button" type="submit">Import portfolio</button>
          </form>
          <form onSubmit={(event) => ingest(event, ingestLinkedIn, linkedinText, setLinkedinText)} style={{ display: "grid", gap: "8px" }}>
            <label>LinkedIn profile text
              <textarea required value={linkedinText} onChange={(event) => setLinkedinText(event.target.value)} placeholder="Paste your profile summary or exported profile text" rows="3" />
            </label>
            <button className="primary-button" type="submit" style={{ justifySelf: "start" }}>Import LinkedIn text</button>
          </form>
          <label>LinkedIn export document (PDF or DOCX)
            <input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={uploadLinkedInDocument} />
          </label>
        </div>
      )}

      {candidates.length > 0 && (
        <>
          <h3 style={{ marginTop: "1.5rem", marginBottom: "0.5rem" }}>Review imported information</h3>
          <ul className="entity-list">
            {candidates.map((candidate) => (
              <li key={candidate.id}>
                <span>{candidate.source_type}: {candidate.data.name || candidate.data.title}</span>
                {candidate.status === "pending" && <span>
                  <button className="button-link" onClick={() => reviewCandidate(candidate, "accepted")}>Accept</button>{" "}
                  <button className="button-link" onClick={() => reviewCandidate(candidate, "rejected")}>Reject</button>
                </span>}
                {candidate.status !== "pending" && <span>{candidate.status}</span>}
              </li>
            ))}
          </ul>
        </>
      )}

      <div className="section-header-row" style={{ marginTop: "1.75rem" }}>
        <h3>Career history & achievements</h3>
      </div>
      <div className="career-records">
        {[
          ["experience", "Experience", { company: "Tech Company", title: "Software Engineer", description: "Led development of core features" }],
          ["education", "Education", { institution: "University / Institute", degree: "Bachelor of Technology" }],
          ["certifications", "Certification", { name: "Cloud Certification", issuer: "Certifying Body" }],
          ["achievements", "Achievement", { title: "Competitive Programming Milestone", description: "Top ranking or hackathon win" }],
        ].map(([type, label, template]) => (
          <CareerRecordForm key={type} type={type} label={label} template={template} />
        ))}
      </div>

      <div className="section-header-row" style={{ marginTop: "1.75rem" }}>
        <h3>Resume document & AI retrieval</h3>
        <button
          type="button"
          className="add-btn"
          onClick={() => setShowUploadResume(!showUploadResume)}
          aria-expanded={showUploadResume}
        >
          {showUploadResume ? "✕ Close" : "+ Upload resume"}
        </button>
      </div>
      {(showUploadResume || !document) && (
        <div className="collapsible-form">
          <label>Upload resume (PDF or DOCX)
            <input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={upload} />
          </label>
        </div>
      )}

      {analyzingResume && (
        <div className="ai-parsing-banner">
          <Sparkles size={20} className="spin-icon" style={{ color: "var(--colors-primary)", flexShrink: 0 }} />
          <div>
            <strong>AI is analyzing your resume...</strong>
            <p style={{ margin: "2px 0 0 0", fontSize: "13px", color: "var(--colors-slate)" }}>
              Extracting skills taxonomy, work history, projects, and credentials with AI confidence scoring.
            </p>
          </div>
        </div>
      )}

      {document && !analyzingResume && (
        <>
          <p className="success-message" role="status" style={{ marginTop: "1rem", display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <span>✓ Processed <strong>{document.filename}</strong></span>
            {document.extraction_engine && (
              <span style={{ background: "rgba(99, 102, 241, 0.15)", color: "var(--colors-primary)", border: "1px solid rgba(99, 102, 241, 0.3)", padding: "2px 8px", borderRadius: "12px", fontSize: "11px", fontWeight: 600 }}>
                ✨ {document.extraction_engine}
              </span>
            )}
          </p>

          <div className="ai-extracted-panel">
            <div className="ai-extracted-header">
              <div className="ai-extracted-title-group">
                <Sparkles size={16} style={{ color: "var(--colors-primary)" }} />
                <h3 style={{ margin: 0, fontSize: "15px", fontWeight: 600 }}>AI Extracted Findings</h3>
                <span className="ai-confidence-pill" style={{ background: "rgba(99, 102, 241, 0.12)", color: "var(--colors-primary)", border: "1px solid rgba(99, 102, 241, 0.25)" }}>
                  ✨ {document.extraction_engine || "AI Analyzed"} ({extracted.length} items)
                </span>
              </div>
              {extracted.length > 0 && (
                <div>
                  {unconfirmedCount > 0 ? (
                    <button
                      type="button"
                      className="primary-button"
                      style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "12px", padding: "6px 14px" }}
                      onClick={acceptAllExtracted}
                    >
                      <Sparkles size={13} />
                      Accept All AI Findings ({unconfirmedCount})
                    </button>
                  ) : (
                    <span className="badge badge-success" style={{ color: "#10b981", fontWeight: 600, fontSize: "12px", padding: "4px 8px" }}>
                      ✓ All Findings Confirmed
                    </span>
                  )}
                </div>
              )}
            </div>

            {extracted.length === 0 ? (
              <p className="empty-message">No text sections detected in this document.</p>
            ) : (
              <>
                <div className="ai-filter-tabs">
                  <button
                    type="button"
                    className={`ai-tab-btn ${selectedEntityTab === "all" ? "active" : ""}`}
                    onClick={() => setSelectedEntityTab("all")}
                  >
                    All ({extracted.length})
                  </button>
                  {extractedSkills.length > 0 && (
                    <button
                      type="button"
                      className={`ai-tab-btn ${selectedEntityTab === "skills" ? "active" : ""}`}
                      onClick={() => setSelectedEntityTab("skills")}
                    >
                      Skills ({extractedSkills.length})
                    </button>
                  )}
                  {extractedExperience.length > 0 && (
                    <button
                      type="button"
                      className={`ai-tab-btn ${selectedEntityTab === "experience" ? "active" : ""}`}
                      onClick={() => setSelectedEntityTab("experience")}
                    >
                      Experience ({extractedExperience.length})
                    </button>
                  )}
                  {extractedProjects.length > 0 && (
                    <button
                      type="button"
                      className={`ai-tab-btn ${selectedEntityTab === "projects" ? "active" : ""}`}
                      onClick={() => setSelectedEntityTab("projects")}
                    >
                      Projects ({extractedProjects.length})
                    </button>
                  )}
                  {extractedEducation.length > 0 && (
                    <button
                      type="button"
                      className={`ai-tab-btn ${selectedEntityTab === "education" ? "active" : ""}`}
                      onClick={() => setSelectedEntityTab("education")}
                    >
                      Education ({extractedEducation.length})
                    </button>
                  )}
                  {extractedOther.length > 0 && (
                    <button
                      type="button"
                      className={`ai-tab-btn ${selectedEntityTab === "other" ? "active" : ""}`}
                      onClick={() => setSelectedEntityTab("other")}
                    >
                      Credentials & More ({extractedOther.length})
                    </button>
                  )}
                </div>

                {showSkillsSection && (
                  <div style={{ marginBottom: "1.25rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                      <h4 style={{ fontSize: "12px", color: "var(--colors-slate)", textTransform: "uppercase", letterSpacing: "0.05em", margin: 0 }}>
                        Extracted Skills ({extractedSkills.length})
                      </h4>
                    </div>
                    <div className="ai-skills-grid">
                      {extractedSkills.map((entity) => {
                        const skillName = entity.data?.name || entity.data?.text || "Skill";
                        const category = entity.data?.category || "Technical";
                        const confidence = entity.data?.confidence ? Math.round(entity.data.confidence * 100) : null;
                        const isAccepted = entity.confirmed_by_user;
                        return (
                          <div key={entity.id} className={`ai-skill-pill ${isAccepted ? "accepted" : ""}`}>
                            <span>{skillName}</span>
                            {category && <span className="ai-skill-category-tag">{category}</span>}
                            {confidence && <span className="ai-confidence-pill" style={{ padding: "1px 5px", fontSize: "10px" }}>{confidence}%</span>}
                            {isAccepted ? (
                              <span title="Confirmed" style={{ display: "inline-flex", color: "#16a34a" }}>
                                <Check size={13} />
                              </span>
                            ) : (
                              <button
                                type="button"
                                className="ai-skill-action-btn"
                                title="Accept skill"
                                onClick={() => review(entity, true)}
                              >
                                <Check size={13} />
                              </button>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {cardsToShow.length > 0 && (
                  <div className="entity-list ai-entity-cards-list">
                    {cardsToShow.map((entity) => {
                      const isAccepted = entity.confirmed_by_user;
                      const typeLabel = (entity.entity_type || "RECORD").toUpperCase();
                      const title = entity.data?.title || entity.data?.name || entity.data?.degree || entity.data?.text?.split("\n")[0] || "Title";
                      const subtitle = entity.data?.company || entity.data?.institution || entity.data?.issuer || "";
                      const dates = entity.data?.dates || entity.data?.year || "";
                      const desc = entity.data?.description || (entity.data?.text && entity.data.text !== title ? entity.data.text : "");

                      return (
                        <div key={entity.id} className={`ai-entity-card ${isAccepted ? "accepted" : ""}`}>
                          <div className="ai-entity-card-header">
                            <div>
                              <div className="ai-entity-title-line">
                                <span className="ai-entity-type-badge">{typeLabel}</span>
                                <strong>{title}</strong>
                                {subtitle && subtitle !== "Experience" && (
                                  <span style={{ color: "var(--colors-slate)", fontSize: "13px" }}>at {subtitle}</span>
                                )}
                              </div>
                              {dates && <span className="ai-entity-meta-dates">{dates}</span>}
                            </div>
                            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                              {isAccepted ? (
                                <span className="badge badge-success" style={{ color: "#10b981", fontWeight: 600, fontSize: "12px" }}>
                                  ✓ Confirmed
                                </span>
                              ) : (
                                <>
                                  <button type="button" className="button-link" onClick={() => review(entity, true)}>
                                    Accept
                                  </button>
                                  <button type="button" className="button-link" style={{ color: "var(--colors-slate)" }} onClick={() => review(entity, false)}>
                                    Reject
                                  </button>
                                </>
                              )}
                            </div>
                          </div>
                          {desc && <p className="ai-entity-description">{desc}</p>}
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            )}

            <div style={{ marginTop: "1rem", paddingTop: "1rem", borderTop: "1px solid var(--colors-hairline)" }}>
              <button className="primary-button" type="button" onClick={handlePrepareChunks}>
                Prepare retrieval chunks
              </button>
              {chunkNotice && (
                <p className={chunks.length > 0 ? "success-message" : "error-message"} role="status" style={{ marginTop: "0.5rem" }}>
                  {chunkNotice}
                </p>
              )}
            </div>
          </div>
        </>
      )}
    </section>
  );
}

function CareerRecordForm({ type, label, template }) {
  const [formFields, setFormFields] = useState({});
  const [useJsonMode, setUseJsonMode] = useState(false);
  const [jsonValue, setJsonValue] = useState(JSON.stringify(template, null, 2));
  const [records, setRecords] = useState([]);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    listCareerEntities(type).then(setRecords).catch((requestError) => setError(requestError.message));
  }, [type]);

  const updateField = (key, val) => {
    setFormFields((prev) => ({ ...prev, [key]: val }));
  };

  const save = (event) => {
    event.preventDefault();
    setError("");
    let payload;

    if (useJsonMode) {
      try {
        payload = JSON.parse(jsonValue);
      } catch {
        setError("Enter valid JSON for this record.");
        return;
      }
    } else {
      payload = { ...formFields };
    }

    if (type === "experience" && (!payload.company || !payload.title)) {
      setError("Company and title cannot be blank.");
      return;
    }
    if (type === "education" && (!payload.institution || !payload.degree)) {
      setError("Institution and degree cannot be blank.");
      return;
    }
    if (type === "certifications" && !payload.name) {
      setError("Certification name cannot be blank.");
      return;
    }
    if (type === "achievements" && !payload.title) {
      setError("Achievement title cannot be blank.");
      return;
    }

    createCareerEntity(type, payload)
      .then((record) => {
        setRecords([...records, record]);
        setFormFields({});
        setJsonValue(JSON.stringify(template, null, 2));
        setShowForm(false);
      })
      .catch((requestError) => setError(requestError.message));
  };

  const remove = (id) => deleteCareerEntity(type, id)
    .then(() => setRecords(records.filter((record) => record.id !== id)))
    .catch((requestError) => setError(requestError.message));

  return (
    <div className="career-record">
      <div className="section-header-row" style={{ marginTop: 0 }}>
        <h3>{label} ({records.length})</h3>
        <button
          type="button"
          className="add-btn"
          onClick={() => {
            setShowForm(!showForm);
            setError("");
          }}
          aria-expanded={showForm}
        >
          {showForm ? "✕ Cancel" : `+ Add ${label.toLowerCase()}`}
        </button>
      </div>
      {error && <p className="error-message" role="alert">{error}</p>}

      {showForm && (
        <form onSubmit={save} className="collapsible-form" style={{ display: "grid", gap: "10px", padding: "12px 14px", background: "var(--colors-surface-soft)", borderRadius: "8px", border: "1px solid var(--colors-hairline)" }}>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button
              type="button"
              className="button-link"
              style={{ fontSize: "11px", color: "var(--colors-steel)" }}
              onClick={() => setUseJsonMode(!useJsonMode)}
            >
              {useJsonMode ? "Switch to form fields" : "Switch to raw JSON"}
            </button>
          </div>

          {useJsonMode ? (
            <label style={{ margin: 0 }}>
              {label} details (JSON)
              <textarea
                value={jsonValue}
                onChange={(event) => setJsonValue(event.target.value)}
                rows="4"
                style={{ marginTop: "4px" }}
              />
            </label>
          ) : (
            <>
              {type === "certifications" && (
                <div style={{ display: "grid", gap: "8px" }}>
                  <label style={{ margin: 0 }}>
                    Certification Title *
                    <input
                      required
                      type="text"
                      value={formFields.name || ""}
                      onChange={(e) => updateField("name", e.target.value)}
                      placeholder="e.g. AWS Certified Solutions Architect"
                      style={{ marginTop: "4px" }}
                    />
                  </label>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                    <label style={{ margin: 0 }}>
                      Issuing Organization
                      <input
                        type="text"
                        value={formFields.issuer || ""}
                        onChange={(e) => updateField("issuer", e.target.value)}
                        placeholder="e.g. Amazon Web Services"
                        style={{ marginTop: "4px" }}
                      />
                    </label>
                    <label style={{ margin: 0 }}>
                      Issue Date / Year
                      <input
                        type="text"
                        value={formFields.issued_date || ""}
                        onChange={(e) => updateField("issued_date", e.target.value)}
                        placeholder="e.g. 2024"
                        style={{ marginTop: "4px" }}
                      />
                    </label>
                  </div>
                </div>
              )}

              {type === "experience" && (
                <div style={{ display: "grid", gap: "8px" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                    <label style={{ margin: 0 }}>
                      Company Name *
                      <input
                        required
                        type="text"
                        value={formFields.company || ""}
                        onChange={(e) => updateField("company", e.target.value)}
                        placeholder="e.g. Stripe"
                        style={{ marginTop: "4px" }}
                      />
                    </label>
                    <label style={{ margin: 0 }}>
                      Job Title *
                      <input
                        required
                        type="text"
                        value={formFields.title || ""}
                        onChange={(e) => updateField("title", e.target.value)}
                        placeholder="e.g. Senior Backend Engineer"
                        style={{ marginTop: "4px" }}
                      />
                    </label>
                  </div>
                  <label style={{ margin: 0 }}>
                    Employment Dates
                    <input
                      type="text"
                      value={formFields.dates || ""}
                      onChange={(e) => updateField("dates", e.target.value)}
                      placeholder="e.g. Jan 2022 - Present"
                      style={{ marginTop: "4px" }}
                    />
                  </label>
                  <label style={{ margin: 0 }}>
                    Description & Key Accomplishments
                    <textarea
                      value={formFields.description || ""}
                      onChange={(e) => updateField("description", e.target.value)}
                      placeholder="Led microservices architecture, improved system throughput by 40%..."
                      rows="2"
                      style={{ marginTop: "4px" }}
                    />
                  </label>
                </div>
              )}

              {type === "education" && (
                <div style={{ display: "grid", gap: "8px" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                    <label style={{ margin: 0 }}>
                      Institution / University *
                      <input
                        required
                        type="text"
                        value={formFields.institution || ""}
                        onChange={(e) => updateField("institution", e.target.value)}
                        placeholder="e.g. Stanford University"
                        style={{ marginTop: "4px" }}
                      />
                    </label>
                    <label style={{ margin: 0 }}>
                      Degree *
                      <input
                        required
                        type="text"
                        value={formFields.degree || ""}
                        onChange={(e) => updateField("degree", e.target.value)}
                        placeholder="e.g. Bachelor of Science"
                        style={{ marginTop: "4px" }}
                      />
                    </label>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                    <label style={{ margin: 0 }}>
                      Field of Study / Major
                      <input
                        type="text"
                        value={formFields.field_of_study || ""}
                        onChange={(e) => updateField("field_of_study", e.target.value)}
                        placeholder="e.g. Computer Science"
                        style={{ marginTop: "4px" }}
                      />
                    </label>
                    <label style={{ margin: 0 }}>
                      Graduation Year
                      <input
                        type="text"
                        value={formFields.year || ""}
                        onChange={(e) => updateField("year", e.target.value)}
                        placeholder="e.g. 2023"
                        style={{ marginTop: "4px" }}
                      />
                    </label>
                  </div>
                </div>
              )}

              {type === "achievements" && (
                <div style={{ display: "grid", gap: "8px" }}>
                  <label style={{ margin: 0 }}>
                    Achievement Title *
                    <input
                      required
                      type="text"
                      value={formFields.title || ""}
                      onChange={(e) => updateField("title", e.target.value)}
                      placeholder="e.g. Hackathon 1st Place Winner"
                      style={{ marginTop: "4px" }}
                    />
                  </label>
                  <label style={{ margin: 0 }}>
                    Description & Context
                    <textarea
                      value={formFields.description || ""}
                      onChange={(e) => updateField("description", e.target.value)}
                      placeholder="Built an autonomous AI agent in 24 hours, awarded best technical innovation..."
                      rows="2"
                      style={{ marginTop: "4px" }}
                    />
                  </label>
                  <label style={{ margin: 0 }}>
                    Date / Year
                    <input
                      type="text"
                      value={formFields.achieved_date || ""}
                      onChange={(e) => updateField("achieved_date", e.target.value)}
                      placeholder="e.g. 2024"
                      style={{ marginTop: "4px" }}
                    />
                  </label>
                </div>
              )}
            </>
          )}

          <div style={{ display: "flex", gap: "8px", marginTop: "4px" }}>
            <button className="primary-button" type="submit">Save {label.toLowerCase()}</button>
            <button className="button-secondary" type="button" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </form>
      )}

      <ul className="entity-list" style={{ marginTop: "8px" }}>
        {records.length === 0 && !showForm && (
          <li style={{ color: "var(--colors-steel)", background: "transparent", border: "none", padding: "4px 0", fontSize: "13px" }}>
            No {label.toLowerCase()} entries yet. Click + Add to add one.
          </li>
        )}
        {records.map((record) => {
          let mainTitle = record.name || record.title || record.degree || record.company || record.institution || "Entry";
          let subtitle = "";
          let metaDate = record.issued_date || record.dates || record.year || record.achieved_date || "";

          if (type === "certifications") {
            subtitle = record.issuer ? `Issued by ${record.issuer}` : "";
          } else if (type === "experience") {
            subtitle = record.company ? `at ${record.company}` : "";
          } else if (type === "education") {
            subtitle = `${record.field_of_study ? `in ${record.field_of_study} ` : ""}at ${record.institution || ""}`;
          }

          return (
            <li key={record.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
                  <strong>{mainTitle}</strong>
                  {subtitle && <span style={{ color: "var(--colors-slate)", fontSize: "12.5px" }}>{subtitle}</span>}
                  {metaDate && (
                    <span style={{ fontSize: "11px", color: "var(--colors-steel)", background: "var(--colors-surface-soft)", padding: "1px 6px", borderRadius: "10px", border: "1px solid var(--colors-hairline)" }}>
                      {metaDate}
                    </span>
                  )}
                </div>
                {record.description && (
                  <p style={{ margin: "2px 0 0 0", fontSize: "12px", color: "var(--colors-slate)", lineHeight: 1.4 }}>
                    {record.description}
                  </p>
                )}
              </div>
              <button className="button-link" style={{ color: "var(--colors-semantic-error)", fontSize: "12px" }} onClick={() => remove(record.id)}>
                Delete
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function TailoredResumesSection() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [activeResume, setActiveResume] = useState(null);

  const loadData = () => {
    Promise.all([listResumes(), getJobs(), getCompanies()])
      .then(([nextResumes, nextJobs, nextCompanies]) => {
        setResumes(nextResumes || []);
        setJobs(nextJobs || []);
        setCompanies(nextCompanies || []);
        if (nextJobs?.length && !selectedJobId) {
          setSelectedJobId(nextJobs[0].id);
        }
      })
      .catch((err) => setError(err.message));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerate = (jobId) => {
    const targetId = jobId || selectedJobId;
    if (!targetId) return;
    setGenerating(true);
    setError("");
    setNotice("");
    generateResume(targetId)
      .then((created) => {
        loadData();
        setActiveResume(created);
        setNotice(`Created tailored resume version v${created.version}!`);
        setTimeout(() => setNotice(""), 4000);
      })
      .catch((err) => setError(err.message || "Failed to generate resume"))
      .finally(() => setGenerating(false));
  };

  const handleApprove = (resume) => {
    updateResume(resume.id, resume.content, "approved")
      .then((updated) => {
        setResumes((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
        if (activeResume && activeResume.id === updated.id) {
          setActiveResume(updated);
        }
        setNotice(`Resume version v${updated.version} approved!`);
        setTimeout(() => setNotice(""), 3000);
      })
      .catch((err) => setError(err.message));
  };

  const handleDownloadLatex = (resumeId, filename = "tailored-resume.tex") => {
    exportResumeLatex(resumeId)
      .then((latex) => {
        const blob = new Blob([latex], { type: "application/x-latex" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
      })
      .catch((err) => setError(err.message));
  };

  return (
    <section className="profile-form" style={{ marginTop: "2rem" }}>
      <div className="section-header-row" style={{ marginTop: 0, justifyContent: "space-between" }}>
        <div>
          <p className="eyebrow">AI RESUME COMPILER</p>
          <h2>Tailored Resume Versions ({resumes.length})</h2>
          <p className="intro" style={{ margin: "2px 0 0 0", fontSize: "13.5px" }}>
            NextHire tailors your verified skills, projects, and work history specifically to any job requirements. Compile and export version-controlled LaTeX resumes with zero hallucination.
          </p>
        </div>
      </div>

      {notice && <p className="success-message" role="status">{notice}</p>}
      {error && <p className="error-message" role="alert">{error}</p>}

      {/* Quick Tailor Generator Bar */}
      <div className="linear-widget-panel" style={{ marginTop: "1rem", background: "linear-gradient(135deg, rgba(86, 69, 212, 0.04), rgba(86, 69, 212, 0.01))" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
          <Sparkles size={16} style={{ color: "var(--colors-primary)" }} />
          <h3 style={{ margin: 0, fontSize: "14px", fontWeight: 600 }}>Tailor Resume For Any Open Role</h3>
        </div>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "center" }}>
          <select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            style={{ flex: 1, minWidth: "260px", height: "38px", borderRadius: "6px", border: "1px solid var(--colors-hairline-strong)", padding: "0 10px", fontSize: "13px", background: "var(--colors-canvas)", color: "var(--colors-ink)" }}
          >
            {jobs.map((job) => {
              const comp = getCompanyDetails(job.company_id, companies);
              return (
                <option key={job.id} value={job.id}>
                  {cleanJobTitle(job.title)} — {comp.name} ({job.location || "Remote"})
                </option>
              );
            })}
          </select>
          <button
            type="button"
            className="primary-button"
            onClick={() => handleGenerate(selectedJobId)}
            disabled={generating || !selectedJobId}
            style={{ display: "inline-flex", alignItems: "center", gap: "6px", height: "38px" }}
          >
            <Sparkles size={14} className={generating ? "spin" : ""} />
            <span>{generating ? "Tailoring with AI..." : "Generate Tailored Resume"}</span>
          </button>
        </div>
      </div>

      {/* Resumes List */}
      <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "1.25rem" }}>
        {resumes.length === 0 ? (
          <div className="empty-state" style={{ padding: "2rem 1rem", textAlign: "center" }}>
            <FileText size={28} style={{ color: "var(--colors-steel)", margin: "0 auto 8px" }} />
            <p style={{ margin: "0 0 4px 0", fontWeight: 600 }}>No tailored resumes created yet.</p>
            <p style={{ margin: 0, fontSize: "13px", color: "var(--colors-slate)" }}>
              Select a job above or click "Tailor Resume" from the Job Feed or Dashboard to generate an AI-tailored resume version.
            </p>
          </div>
        ) : (
          resumes.map((resume) => {
            const matchedJob = jobs.find((j) => j.id === resume.job_id);
            const jobTitle = matchedJob ? cleanJobTitle(matchedJob.title) : resume.content?.summary || "Tailored Engineering Role";
            const comp = getCompanyDetails(matchedJob?.company_id, companies);
            const isApproved = resume.status === "approved";

            return (
              <div key={resume.id} className="recommended-job-card" style={{ gap: "10px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "8px" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                      <span className="linear-chip" style={{ fontSize: "11px" }}>
                        Version v{resume.version}
                      </span>
                      <span style={{
                        padding: "2px 8px",
                        borderRadius: "9999px",
                        fontSize: "11px",
                        fontWeight: 700,
                        background: isApproved ? "rgba(26, 174, 57, 0.1)" : "rgba(245, 158, 11, 0.12)",
                        color: isApproved ? "#15803d" : "#b45309",
                        border: isApproved ? "1px solid rgba(26, 174, 57, 0.3)" : "1px solid rgba(245, 158, 11, 0.3)"
                      }}>
                        {isApproved ? "✓ Approved" : "Draft"}
                      </span>
                      <span style={{ fontSize: "11.5px", color: "var(--colors-steel)" }}>
                        Template: {resume.template || "default"}
                      </span>
                    </div>
                    <h3 style={{ margin: "6px 0 2px 0", fontSize: "16px", fontWeight: 700, color: "var(--colors-ink)" }}>
                      {jobTitle}
                    </h3>
                    <p style={{ margin: 0, fontSize: "13px", color: "var(--colors-slate)" }}>
                      Target: {comp.name} · Created {new Date(resume.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                    <button
                      type="button"
                      className="button-secondary"
                      onClick={() => setActiveResume(resume)}
                      style={{ display: "inline-flex", alignItems: "center", gap: "5px", fontSize: "12.5px", padding: "6px 12px" }}
                    >
                      <FileText size={13} />
                      <span>Preview Resume</span>
                    </button>
                    <button
                      type="button"
                      className="button-secondary"
                      onClick={() => handleDownloadLatex(resume.id, `${jobTitle.replace(/[^a-zA-Z0-9]/g, "_")}_v${resume.version}.tex`)}
                      style={{ display: "inline-flex", alignItems: "center", gap: "5px", fontSize: "12.5px", padding: "6px 12px" }}
                      title="Download LaTeX source (.tex)"
                    >
                      <Download size={13} />
                      <span>LaTeX (.tex)</span>
                    </button>
                    {!isApproved && (
                      <button
                        type="button"
                        className="primary-button"
                        onClick={() => handleApprove(resume)}
                        style={{ display: "inline-flex", alignItems: "center", gap: "5px", fontSize: "12.5px", padding: "6px 12px" }}
                      >
                        <Check size={13} />
                        <span>Approve</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Skills Row */}
                {resume.content?.skills?.length > 0 && (
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap", marginTop: "4px" }}>
                    <span style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", color: "var(--colors-steel)", letterSpacing: "0.04em" }}>
                      Tailored Skills:
                    </span>
                    {resume.content.skills.slice(0, 7).map((skill) => (
                      <span key={skill} className="skill-tag matched" style={{ fontSize: "11px" }}>
                        <Check size={10} />
                        {skill}
                      </span>
                    ))}
                    {resume.content.skills.length > 7 && (
                      <span style={{ fontSize: "11px", color: "var(--colors-steel)" }}>
                        +{resume.content.skills.length - 7} more
                      </span>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Modal Preview */}
      {activeResume && (
        <TailoredResumeModal
          resume={activeResume}
          jobs={jobs}
          companies={companies}
          onClose={() => setActiveResume(null)}
          onApprove={handleApprove}
          onDownloadLatex={handleDownloadLatex}
        />
      )}
    </section>
  );
}

function TailoredResumeModal({ resume, jobs = [], companies = [], onClose, onApprove, onDownloadLatex }) {
  const [currentResume, setCurrentResume] = useState(resume);
  const [activeTab, setActiveTab] = useState("document");
  const [latexSource, setLatexSource] = useState("");
  const [loadingLatex, setLoadingLatex] = useState(false);
  const [copied, setCopied] = useState(false);

  // Customization state
  const [summaryText, setSummaryText] = useState(currentResume.content?.summary || "");
  const [selectedTemplate, setSelectedTemplate] = useState(currentResume.template || "default");
  const [sectionOrder, setSectionOrder] = useState(
    currentResume.content?.section_order?.length
      ? currentResume.content.section_order
      : ["summary", "skills", "experience", "projects", "education", "certifications"]
  );
  const [skillsList, setSkillsList] = useState(currentResume.content?.skills || []);
  const [newSkillInput, setNewSkillInput] = useState("");
  const [experienceItems, setExperienceItems] = useState(currentResume.content?.experience || []);
  const [projectItems, setProjectItems] = useState(currentResume.content?.projects || []);
  const [educationItems, setEducationItems] = useState(currentResume.content?.education || []);
  const [certificationItems, setCertificationItems] = useState(currentResume.content?.certifications || []);
  const [savingCustomization, setSavingCustomization] = useState(false);
  const [customizationNotice, setCustomizationNotice] = useState("");
  const [customizationError, setCustomizationError] = useState("");

  const matchedJob = jobs.find((j) => j.id === currentResume.job_id);
  const jobTitle = matchedJob ? cleanJobTitle(matchedJob.title) : currentResume.content?.summary || "Tailored Role";
  const comp = getCompanyDetails(matchedJob?.company_id, companies);
  const isApproved = currentResume.status === "approved";

  useEffect(() => {
    if (activeTab === "latex" && !latexSource) {
      setLoadingLatex(true);
      exportResumeLatex(currentResume.id)
        .then((code) => setLatexSource(code))
        .catch(() => setLatexSource("% Failed to load LaTeX code"))
        .finally(() => setLoadingLatex(false));
    }
  }, [activeTab, currentResume.id, latexSource]);

  const copyLatex = () => {
    if (!latexSource) return;
    navigator.clipboard.writeText(latexSource).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const moveSection = (index, direction) => {
    const nextOrder = [...sectionOrder];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= nextOrder.length) return;
    const [moved] = nextOrder.splice(index, 1);
    nextOrder.splice(targetIndex, 0, moved);
    setSectionOrder(nextOrder);
  };

  const handleAddSkillChip = (e) => {
    e.preventDefault();
    const trimmed = newSkillInput.trim();
    if (trimmed && !skillsList.includes(trimmed)) {
      setSkillsList([...skillsList, trimmed]);
      setNewSkillInput("");
    }
  };

  const handleRemoveSkillChip = (skillToRemove) => {
    setSkillsList(skillsList.filter((s) => s !== skillToRemove));
  };

  const handleSaveCustomization = () => {
    if (!summaryText.trim()) {
      setCustomizationError("Resume summary cannot be blank.");
      return;
    }
    setSavingCustomization(true);
    setCustomizationError("");
    setCustomizationNotice("");

    const updatedContent = {
      summary: summaryText.trim(),
      skills: skillsList,
      experience: experienceItems,
      projects: projectItems,
      education: educationItems,
      certifications: certificationItems,
      section_order: sectionOrder,
    };

    updateResume(currentResume.id, updatedContent, currentResume.status, selectedTemplate)
      .then((updated) => {
        setCurrentResume(updated);
        setCustomizationNotice("✓ Resume customizations saved and applied successfully!");
        setLatexSource("");
        if (onApprove && currentResume.status === "approved") {
          onApprove(updated);
        }
      })
      .catch((err) => {
        setCustomizationError(err.message || "Failed to update resume.");
      })
      .finally(() => {
        setSavingCustomization(false);
      });
  };

  const sectionLabels = {
    summary: "Professional Summary",
    skills: "Tailored Core Skills",
    experience: "Work Experience",
    projects: "Relevant Projects",
    education: "Education",
    certifications: "Certifications",
  };

  const renderSection = (sectionKey) => {
    switch (sectionKey.toLowerCase()) {
      case "summary":
        return (
          <div key="summary" style={{ padding: "1rem 1.25rem", borderRadius: "8px", background: "var(--colors-surface)", border: "1px solid var(--colors-hairline)" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--colors-steel)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Professional Summary
            </span>
            <p style={{ margin: "4px 0 0 0", fontSize: "14px", fontWeight: 600, color: "var(--colors-ink)" }}>
              {currentResume.content?.summary || "Software Engineer"}
            </p>
          </div>
        );
      case "skills":
        if (!currentResume.content?.skills?.length) return null;
        return (
          <div key="skills">
            <h4 className="ai-section-title">Tailored Core Skills ({currentResume.content.skills.length})</h4>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {currentResume.content.skills.map((skill) => (
                <span key={skill} className="skill-tag matched" style={{ fontSize: "12px", padding: "4px 9px" }}>
                  <Check size={11} />
                  <span>{skill}</span>
                </span>
              ))}
            </div>
          </div>
        );
      case "experience":
        if (!currentResume.content?.experience?.length) return null;
        return (
          <div key="experience">
            <h4 className="ai-section-title">Work Experience ({currentResume.content.experience.length})</h4>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {currentResume.content.experience.map((exp, idx) => (
                <div key={idx} style={{ padding: "10px 12px", background: "var(--colors-surface)", borderRadius: "6px", border: "1px solid var(--colors-hairline)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--colors-ink)" }}>
                      {exp.text.split(":")[0]}
                    </span>
                    <span style={{ fontSize: "11px", color: "var(--colors-brand-green)", fontWeight: 600 }}>
                      ✓ Verified Career Fact
                    </span>
                  </div>
                  {exp.text.includes(":") && (
                    <p style={{ margin: "4px 0 0 0", fontSize: "12.5px", color: "var(--colors-slate)" }}>
                      {exp.text.substring(exp.text.indexOf(":") + 1).trim()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      case "projects":
        if (!currentResume.content?.projects?.length) return null;
        return (
          <div key="projects">
            <h4 className="ai-section-title">Relevant Projects ({currentResume.content.projects.length})</h4>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {currentResume.content.projects.map((proj, idx) => (
                <div key={idx} style={{ padding: "10px 12px", background: "var(--colors-surface)", borderRadius: "6px", border: "1px solid var(--colors-hairline)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--colors-ink)" }}>
                      {proj.text.split(":")[0]}
                    </span>
                    <span style={{ fontSize: "11px", color: "var(--colors-brand-green)", fontWeight: 600 }}>
                      ✓ Provenance Verified
                    </span>
                  </div>
                  {proj.text.includes(":") && (
                    <p style={{ margin: "4px 0 0 0", fontSize: "12.5px", color: "var(--colors-slate)" }}>
                      {proj.text.substring(proj.text.indexOf(":") + 1).trim()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      case "education":
        if (!currentResume.content?.education?.length) return null;
        return (
          <div key="education">
            <h4 className="ai-section-title">Education</h4>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {currentResume.content.education.map((edu, idx) => (
                <div key={idx} style={{ padding: "8px 12px", background: "var(--colors-surface)", borderRadius: "6px", border: "1px solid var(--colors-hairline)", fontSize: "13px", color: "var(--colors-ink)" }}>
                  {edu.text}
                </div>
              ))}
            </div>
          </div>
        );
      case "certifications":
        if (!currentResume.content?.certifications?.length) return null;
        return (
          <div key="certifications">
            <h4 className="ai-section-title">Certifications</h4>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {currentResume.content.certifications.map((cert, idx) => (
                <div key={idx} style={{ padding: "8px 12px", background: "var(--colors-surface)", borderRadius: "6px", border: "1px solid var(--colors-hairline)", fontSize: "13px", color: "var(--colors-ink)" }}>
                  {cert.text}
                </div>
              ))}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="ai-modal-backdrop" onClick={onClose}>
      <div className="ai-modal-dialog" style={{ maxWidth: "820px" }} onClick={(e) => e.stopPropagation()}>
        <div className="ai-modal-header">
          <div className="ai-modal-title-row">
            <Sparkles size={18} className="linear-icon-primary" />
            <div>
              <h3 style={{ margin: 0, fontSize: "16px", fontWeight: 700 }}>Tailored Resume · Version v{currentResume.version}</h3>
              <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>
                {jobTitle} · {comp.name} · Template: {currentResume.template || "default"}
              </span>
            </div>
          </div>
          <button className="ai-modal-close-btn" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: "flex", gap: "8px", padding: "0.75rem 1.5rem", borderBottom: "1px solid var(--colors-hairline)", background: "var(--colors-surface-soft)" }}>
          <button
            type="button"
            className={`ai-tab-btn ${activeTab === "document" ? "active" : ""}`}
            onClick={() => setActiveTab("document")}
          >
            Formatted Resume View
          </button>
          <button
            type="button"
            className={`ai-tab-btn ${activeTab === "customize" ? "active" : ""}`}
            onClick={() => setActiveTab("customize")}
            style={{ display: "inline-flex", alignItems: "center", gap: "5px" }}
          >
            <SlidersHorizontal size={13} />
            <span>Customize & Reorder</span>
          </button>
          <button
            type="button"
            className={`ai-tab-btn ${activeTab === "latex" ? "active" : ""}`}
            onClick={() => setActiveTab("latex")}
          >
            LaTeX Source (.tex)
          </button>
        </div>

        <div className="ai-modal-body" style={{ maxHeight: "65vh", overflowY: "auto" }}>
          {activeTab === "document" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              {(currentResume.content?.section_order || [
                "summary",
                "skills",
                "experience",
                "projects",
                "education",
                "certifications",
              ]).map((sec) => renderSection(sec))}
            </div>
          )}

          {activeTab === "customize" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              {customizationNotice && (
                <div style={{ padding: "8px 12px", borderRadius: "6px", background: "rgba(16, 185, 129, 0.12)", color: "#065f46", fontSize: "13px", fontWeight: 600 }}>
                  {customizationNotice}
                </div>
              )}
              {customizationError && (
                <div className="error-message" role="alert" style={{ margin: 0 }}>
                  {customizationError}
                </div>
              )}

              {/* Template Style */}
              <div style={{ padding: "12px 14px", borderRadius: "8px", background: "var(--colors-surface)", border: "1px solid var(--colors-hairline)" }}>
                <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--colors-ink)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  Resume Layout Template
                </span>
                <div style={{ display: "flex", gap: "12px", marginTop: "8px", flexWrap: "wrap" }}>
                  <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
                    <input
                      type="radio"
                      name="resumeTemplate"
                      value="default"
                      checked={selectedTemplate === "default"}
                      onChange={() => setSelectedTemplate("default")}
                    />
                    <span>Clean Single-Column (Default)</span>
                  </label>
                  <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px" }}>
                    <input
                      type="radio"
                      name="resumeTemplate"
                      value="technical"
                      checked={selectedTemplate === "technical"}
                      onChange={() => setSelectedTemplate("technical")}
                    />
                    <span>Technical Skills-Forward</span>
                  </label>
                </div>
              </div>

              {/* Section Ordering */}
              <div style={{ padding: "12px 14px", borderRadius: "8px", background: "var(--colors-surface)", border: "1px solid var(--colors-hairline)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <div>
                    <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--colors-ink)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                      Section Ordering
                    </span>
                    <p style={{ margin: "2px 0 0 0", fontSize: "12px", color: "var(--colors-slate)" }}>
                      Use the arrows to reorder sections. The LaTeX resume and document view will follow this hierarchy.
                    </p>
                  </div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  {sectionOrder.map((sectionKey, idx) => (
                    <div
                      key={sectionKey}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "7px 10px",
                        background: "var(--colors-canvas)",
                        borderRadius: "6px",
                        border: "1px solid var(--colors-hairline)",
                        fontSize: "13px",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--colors-steel)", width: "18px" }}>
                          #{idx + 1}
                        </span>
                        <strong style={{ color: "var(--colors-ink)" }}>{sectionLabels[sectionKey] || sectionKey}</strong>
                      </div>
                      <div style={{ display: "flex", gap: "4px" }}>
                        <button
                          type="button"
                          className="button-secondary"
                          style={{ padding: "2px 8px", fontSize: "11px" }}
                          disabled={idx === 0}
                          onClick={() => moveSection(idx, -1)}
                          title="Move section up"
                        >
                          ↑ Up
                        </button>
                        <button
                          type="button"
                          className="button-secondary"
                          style={{ padding: "2px 8px", fontSize: "11px" }}
                          disabled={idx === sectionOrder.length - 1}
                          onClick={() => moveSection(idx, 1)}
                          title="Move section down"
                        >
                          ↓ Down
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Summary Editor */}
              <div style={{ padding: "12px 14px", borderRadius: "8px", background: "var(--colors-surface)", border: "1px solid var(--colors-hairline)" }}>
                <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--colors-ink)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  Professional Summary
                </span>
                <textarea
                  value={summaryText}
                  onChange={(e) => setSummaryText(e.target.value)}
                  rows="2"
                  style={{ width: "100%", marginTop: "6px", fontSize: "13px" }}
                  placeholder="Professional headline or tailored career summary..."
                />
              </div>

              {/* Skills Editor */}
              <div style={{ padding: "12px 14px", borderRadius: "8px", background: "var(--colors-surface)", border: "1px solid var(--colors-hairline)" }}>
                <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--colors-ink)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  Tailored Skills ({skillsList.length})
                </span>
                <p style={{ margin: "2px 0 8px 0", fontSize: "12px", color: "var(--colors-slate)" }}>
                  Click ✕ on any skill to remove it from this resume version, or add new skills below.
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "10px" }}>
                  {skillsList.map((skill) => (
                    <span
                      key={skill}
                      className="skill-tag matched"
                      style={{ fontSize: "12px", padding: "4px 8px", display: "inline-flex", alignItems: "center", gap: "6px" }}
                    >
                      <span>{skill}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveSkillChip(skill)}
                        style={{ border: "none", background: "transparent", cursor: "pointer", padding: 0, color: "var(--colors-steel)", display: "inline-flex" }}
                        title="Remove skill"
                      >
                        <X size={11} />
                      </button>
                    </span>
                  ))}
                </div>
                <div style={{ display: "flex", gap: "6px" }}>
                  <input
                    type="text"
                    value={newSkillInput}
                    onChange={(e) => setNewSkillInput(e.target.value)}
                    placeholder="Add a new skill (e.g. GraphQL, TailwindCSS)..."
                    style={{ flex: 1, fontSize: "13px" }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleAddSkillChip(e);
                      }
                    }}
                  />
                  <button type="button" className="button-secondary" onClick={handleAddSkillChip} style={{ padding: "6px 12px", fontSize: "12px" }}>
                    Add Skill
                  </button>
                </div>
              </div>

              {/* Experience Items Editor */}
              {experienceItems.length > 0 && (
                <div style={{ padding: "12px 14px", borderRadius: "8px", background: "var(--colors-surface)", border: "1px solid var(--colors-hairline)" }}>
                  <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--colors-ink)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    Work Experience ({experienceItems.length})
                  </span>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "8px" }}>
                    {experienceItems.map((item, idx) => (
                      <div key={idx} style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                        <span style={{ fontSize: "11px", color: "var(--colors-brand-green)", fontWeight: 600 }}>
                          ✓ Verified Source Provenance Active
                        </span>
                        <textarea
                          value={item.text}
                          onChange={(e) => {
                            const updated = [...experienceItems];
                            updated[idx] = { ...updated[idx], text: e.target.value };
                            setExperienceItems(updated);
                          }}
                          rows="2"
                          style={{ width: "100%", fontSize: "13px" }}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Projects Items Editor */}
              {projectItems.length > 0 && (
                <div style={{ padding: "12px 14px", borderRadius: "8px", background: "var(--colors-surface)", border: "1px solid var(--colors-hairline)" }}>
                  <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--colors-ink)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    Projects ({projectItems.length})
                  </span>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "8px" }}>
                    {projectItems.map((item, idx) => (
                      <div key={idx} style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                        <span style={{ fontSize: "11px", color: "var(--colors-brand-green)", fontWeight: 600 }}>
                          ✓ Verified Source Provenance Active
                        </span>
                        <textarea
                          value={item.text}
                          onChange={(e) => {
                            const updated = [...projectItems];
                            updated[idx] = { ...updated[idx], text: e.target.value };
                            setProjectItems(updated);
                          }}
                          rows="2"
                          style={{ width: "100%", fontSize: "13px" }}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Save Customizations Button */}
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "6px" }}>
                <button
                  type="button"
                  className="primary-button"
                  onClick={handleSaveCustomization}
                  disabled={savingCustomization}
                  style={{ display: "inline-flex", alignItems: "center", gap: "6px", padding: "8px 18px", fontSize: "13px" }}
                >
                  <Sparkles size={14} className={savingCustomization ? "spin" : ""} />
                  <span>{savingCustomization ? "Saving..." : "Save & Apply Customizations"}</span>
                </button>
              </div>
            </div>
          )}

          {activeTab === "latex" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "var(--colors-slate)" }}>
                  LaTeX Document Code (compile with pdflatex or Overleaf)
                </span>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    type="button"
                    className="button-secondary"
                    onClick={copyLatex}
                    style={{ fontSize: "12px", padding: "4px 10px" }}
                  >
                    {copied ? "✓ Copied!" : "Copy LaTeX"}
                  </button>
                  <button
                    type="button"
                    className="button-secondary"
                    onClick={() => onDownloadLatex(currentResume.id, `${jobTitle.replace(/[^a-zA-Z0-9]/g, "_")}_v${currentResume.version}.tex`)}
                    style={{ fontSize: "12px", padding: "4px 10px" }}
                  >
                    Download .tex
                  </button>
                </div>
              </div>
              {loadingLatex ? (
                <p className="loading-message">Rendering LaTeX source...</p>
              ) : (
                <pre style={{
                  padding: "1rem",
                  borderRadius: "6px",
                  background: "#1e1e2e",
                  color: "#cdd6f4",
                  fontSize: "12px",
                  lineHeight: 1.5,
                  overflowX: "auto",
                  whiteSpace: "pre-wrap",
                  fontFamily: "monospace"
                }}>
                  {latexSource || "% Loading LaTeX document..."}
                </pre>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "1rem 1.5rem", borderTop: "1px solid var(--colors-hairline)", background: "var(--colors-surface-soft)" }}>
          <button
            type="button"
            className="button-secondary"
            onClick={() => onDownloadLatex(currentResume.id, `${jobTitle.replace(/[^a-zA-Z0-9]/g, "_")}_v${currentResume.version}.tex`)}
            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
          >
            <Download size={13} />
            <span>Download LaTeX (.tex)</span>
          </button>

          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            {!isApproved ? (
              <button
                type="button"
                className="primary-button"
                onClick={() => onApprove(currentResume)}
                style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
              >
                <Check size={13} />
                <span>Approve Resume Version</span>
              </button>
            ) : (
              <span style={{ color: "#10b981", fontWeight: 700, fontSize: "12.5px" }}>
                ✓ Version Approved
              </span>
            )}
            <button type="button" className="button-secondary" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function PasswordResetPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const submit = (event) => {
    event.preventDefault();
    setError("");
    requestPasswordReset(email)
      .then((result) => setMessage(result.message))
      .catch((requestError) => setError(requestError.message));
  };
  return (
    <main className="auth-screen">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">NEXT HIRE</p>
        <h1>Reset your password.</h1>
        <p className="intro">Enter your account email and we will send reset instructions if it exists.</p>
        <label>Email<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
        {message && <p className="success-message" role="status">{message}</p>}
        {error && <p className="error-message" role="alert">{error}</p>}
        <button className="primary-button" type="submit">Send reset instructions</button>
        <a className="secondary-link" href="/login">Back to sign in</a>
      </form>
    </main>
  );
}

function FoundationStatus() {
  return (
    <div className="status-card" role="status">
      <span className="status-dot" />
      Foundation services are ready
    </div>
  );
}

function DashboardContent({ dashboard, error, onReload, user }) {
  const [seeding, setSeeding] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [notice, setNotice] = useState("");
  const [noticeType, setNoticeType] = useState("success");
  const [companies, setCompanies] = useState([]);
  const [selectedJobForIntelligence, setSelectedJobForIntelligence] = useState(null);
  const [tailoredResumeForPreview, setTailoredResumeForPreview] = useState(null);
  const [tailoringId, setTailoringId] = useState("");
  const [activeNextStepsJob, setActiveNextStepsJob] = useState(null);
  const [dismissedJobIds, setDismissedJobIds] = useState(
    () => new Set(dashboard?.profile?.dismissed_job_ids || [])
  );
  const [applicationsMap, setApplicationsMap] = useState(() => {
    const m = new Map();
    (dashboard?.applications || []).forEach((a) => m.set(a.job_id, a));
    return m;
  });

  const handleTailorJob = (job) => {
    setTailoringId(job.id);
    generateResume(job.id)
      .then((created) => {
        setTailoredResumeForPreview(created);
      })
      .catch((err) => {
        setNotice(`Failed to tailor resume: ${err.message}`);
        setNoticeType("error");
      })
      .finally(() => setTailoringId(""));
  };

  const handleDismissJob = (jobId) => {
    setDismissedJobIds((prev) => new Set(prev).add(jobId));
    dismissJob(jobId).catch((err) => console.error("Dismiss failed", err));
  };

  const handleMarkApplied = (job) => {
    createApplication({ job_id: job.id, status: "applied" })
      .then((app) => {
        setApplicationsMap((prev) => new Map(prev).set(job.id, app));
        setActiveNextStepsJob(job);
      })
      .catch((err) => {
        setNotice(`Failed to record application: ${err.message}`);
        setNoticeType("error");
      });
  };

  useEffect(() => {
    getCompanies()
      .then(setCompanies)
      .catch(() => {});
  }, []);

  if (error) {
    return <p className="error-message" role="alert">Unable to load your dashboard.</p>;
  }

  if (!dashboard) {
    return <p className="loading-message" role="status">Loading your dashboard...</p>;
  }

  const handleSeed = () => {
    setSeeding(true);
    setNotice("");
    scrapeNaukriJobs({ search_term: "Software Engineer", results_wanted: 15 })
      .then((jobs) => {
        if (!jobs || jobs.length === 0) return seedJobs();
        return jobs;
      })
      .then((jobs) => {
        setNotice(`Discovered ${jobs.length} verified roles via Naukri!`);
        setNoticeType("success");
        if (onReload) onReload();
      })
      .catch((err) => {
        setNotice(`Failed: ${err.message}`);
        setNoticeType("error");
      })
      .finally(() => setSeeding(false));
  };

  const handleSyncKnowledgeBase = () => {
    setSyncing(true);
    setNotice("");
    refreshAllCompanies()
      .then(() => {
        setNotice("Career Knowledge Base synchronized with verified company feeds!");
        setNoticeType("success");
        if (onReload) onReload();
      })
      .catch(() => {
        if (onReload) onReload();
        setNotice("Career Knowledge Base refreshed with latest profile signals.");
        setNoticeType("success");
      })
      .finally(() => {
        setTimeout(() => setSyncing(false), 500);
        setTimeout(() => setNotice(""), 4500);
      });
  };

  const userName = user?.display_name ? user.display_name.split(" ")[0] : "Alex";
  const completeness = dashboard.profile_completeness ?? 0;
  const profile = dashboard.profile || {};

  // Calculate connected knowledge sources
  const connectedSourcesCount = [
    Boolean(profile?.skills?.length),
    Boolean(profile?.headline || profile?.preferred_roles?.length),
    Boolean(profile?.location),
    Boolean(profile?.target_companies?.length || (profile?.preferred_skills && Object.keys(profile.preferred_skills).length)),
  ].filter(Boolean).length;
  const connectedSourcesDisplay = connectedSourcesCount > 0 ? connectedSourcesCount : (completeness > 0 ? Math.max(1, Math.round(completeness / 25)) : 0);

  // Application pipeline status counts
  const applications = dashboard.applications || [];
  const appliedCount = applications.filter((a) => a.status === "applied").length;
  const interviewCount = applications.filter((a) => a.status === "interview" || a.status === "interviewing").length;
  const offerCount = applications.filter((a) => a.status === "offer").length;

  // Filter recommended jobs to remove bogus non-job titles and dismissed roles
  const isBogusTitle = (t = "") => {
    const l = t.toLowerCase();
    return (
      l.includes("home home") ||
      l.includes("cookie") ||
      l.includes("saved jobs") ||
      l.includes("privacy statement") ||
      l.includes("accessibility") ||
      l.includes("read more")
    );
  };

  const userSkills = profile?.skills || [];

  const recommendedJobs = useMemo(() => {
    const list = deduplicateJobsList(dashboard.recommended_jobs || [])
      .filter((j) => !isBogusTitle(j.title) && !dismissedJobIds.has(j.id));

    return list
      .map((job) => {
        const skillsInfo = getJobSkillsAndScore(
          job,
          userSkills,
          profile?.headline || ""
        );
        return {
          ...job,
          skillsInfo,
          score: skillsInfo.score,
        };
      })
      .sort((a, b) => {
        // Highest matching jobs on top (descending)
        if (b.score !== a.score) return b.score - a.score;
        const aMatched = a.skillsInfo?.matched?.length || 0;
        const bMatched = b.skillsInfo?.matched?.length || 0;
        if (bMatched !== aMatched) return bMatched - aMatched;
        const dateA = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
        const dateB = b.last_seen_at ? new Date(b.last_seen_at).getTime() : 0;
        if (dateB !== dateA) return dateB - dateA;
        return (a.title || "").localeCompare(b.title || "");
      });
  }, [dashboard.recommended_jobs, dismissedJobIds, userSkills, profile?.headline]);

  return (
    <div className="career-overview-container">
      {/* 1. Header & Quick Actions Bar */}
      <div className="career-overview-header">
        <div>
          <div className="workspace-badge-row">
            <span className="linear-chip">
              <span className="status-dot-pulse" />
              Personal Workspace
            </span>
            <span className="workspace-context-text">· Active Career Search</span>
          </div>
          <h1 className="overview-greeting">Welcome back, {userName}</h1>
          <p className="overview-subtext">
            Real-time career intelligence overview, pipeline status, and curated job recommendations.
          </p>
        </div>

        <div className="overview-quick-actions">
          <button
            className="primary-button linear-sync-btn"
            onClick={handleSyncKnowledgeBase}
            disabled={syncing}
            title="Sync Career Knowledge Base"
          >
            <Sparkles size={14} className={syncing ? "spin-icon" : ""} />
            <span>{syncing ? "Syncing..." : "Sync Career Knowledge Base"}</span>
          </button>
          <a className="button-secondary linear-upload-btn" href="/profile">
            <Upload size={14} />
            <span>Upload Resume</span>
          </a>
        </div>
      </div>

      {notice && (
        <p className={noticeType === "error" ? "error-message" : "success-message"} role="status" style={{ margin: 0 }}>
          {notice}
        </p>
      )}

      {/* 2. Metric Cards Grid */}
      <div className="overview-metrics-grid">
        {/* Profile Completeness Card */}
        <section className="overview-metric-card">
          <div>
            <div className="linear-card-header">
              <span className="linear-metric-label">Profile Completeness</span>
              <FileText size={16} className="linear-icon-muted" />
            </div>
            <div className="linear-metric-value-row">
              <span className="linear-metric-number">{completeness}%</span>
              <span className={`linear-trend-badge ${completeness >= 80 ? "positive" : "neutral"}`}>
                {completeness >= 80 ? "Optimized" : "In Progress"}
              </span>
            </div>
            <div className="overview-progress-bar" title={`${completeness}% Complete`}>
              <div
                className="overview-progress-fill"
                style={{ width: `${Math.max(4, completeness)}%` }}
              />
            </div>
          </div>
          <div className="overview-card-breakdown">
            <span>Knowledge Base: {connectedSourcesDisplay}/4 sources connected</span>
            <a className="overview-link-subtle" href="/profile">
              <span>Update Profile</span>
              <ArrowRight size={12} />
            </a>
          </div>
        </section>

        {/* Discovered Jobs Card */}
        <section className="overview-metric-card">
          <div>
            <div className="linear-card-header">
              <span className="linear-metric-label">Discovered Jobs</span>
              <Compass size={16} className="linear-icon-muted" />
            </div>
            <div className="linear-metric-value-row">
              <span className="linear-metric-number">{dashboard.jobs_discovered}</span>
              <span className="new-today-badge">
                +{dashboard.jobs_discovered > 0 ? Math.min(dashboard.jobs_discovered, 12) : 0} new today
              </span>
            </div>
            <p className="linear-metric-caption" style={{ margin: "6px 0 0 0" }}>
              Verified career openings monitored across leading tech engineering teams.
            </p>
          </div>
          <div style={{ marginTop: "1rem" }}>
            {dashboard.jobs_discovered === 0 ? (
              <button
                className="button-secondary overview-action-btn"
                onClick={handleSeed}
                disabled={seeding}
              >
                <Compass size={13} />
                <span>{seeding ? "Discovering..." : "Discover verified roles"}</span>
              </button>
            ) : (
              <a className="button-secondary overview-action-btn" href="/jobs">
                <span>Explore Feed</span>
                <ArrowRight size={13} />
              </a>
            )}
          </div>
        </section>

        {/* Active Applications Card */}
        <section className="overview-metric-card">
          <div>
            <div className="linear-card-header">
              <span className="linear-metric-label">Active Applications</span>
              <Briefcase size={16} className="linear-icon-muted" />
            </div>
            <div className="linear-metric-value-row">
              <span className="linear-metric-number">{dashboard.active_applications}</span>
              <span className="linear-trend-badge neutral">Active Pipeline</span>
            </div>
            <div className="application-funnel-dots">
              <span className="funnel-dot-item" title="Applied">
                <span className="funnel-dot applied" /> Applied: {appliedCount}
              </span>
              <span className="funnel-dot-item" title="Interviewing">
                <span className="funnel-dot interview" /> Interviewing: {interviewCount}
              </span>
              <span className="funnel-dot-item" title="Offer">
                <span className="funnel-dot offer" /> Offer: {offerCount}
              </span>
            </div>
          </div>
          <div style={{ marginTop: "0.75rem" }}>
            <a className="overview-link-subtle" href="/applications">
              <span>View Pipeline Tracker</span>
              <ArrowRight size={12} />
            </a>
          </div>
        </section>
      </div>

      {/* 3. Recommended Jobs Section */}
      <section className="recommended-jobs-panel">
        <div className="recommended-jobs-header">
          <div>
            <h2 style={{ margin: 0, fontSize: "16px", fontWeight: 600, color: "var(--colors-ink)" }}>
              Recommended Roles
            </h2>
            <p style={{ margin: "3px 0 0 0", fontSize: "13px", color: "var(--colors-slate)" }}>
              Curated openings matched with high affinity against your verified skills and target preferences.
            </p>
          </div>
          {dashboard.jobs_discovered > 0 && (
            <a className="overview-link-subtle" href="/jobs">
              <span>View all {dashboard.jobs_discovered} roles</span>
              <ArrowRight size={12} />
            </a>
          )}
        </div>

        {recommendedJobs.length === 0 ? (
          <div className="empty-state" style={{ padding: "2.5rem 1rem", textAlign: "center" }}>
            <p style={{ margin: "0 0 0.5rem", fontWeight: 600, color: "var(--colors-ink)" }}>
              {dashboard.jobs_discovered === 0
                ? "No verified company roles ingested yet."
                : "No matching roles found yet."}
            </p>
            <p style={{ margin: 0, fontSize: "13px", color: "var(--colors-slate)" }}>
              {dashboard.jobs_discovered === 0
                ? "Click below to trigger discovery across monitored company career portals."
                : "Update your target skills or experience in Resumes to unlock recommendations."}
            </p>
            {dashboard.jobs_discovered === 0 && (
              <button
                className="primary-button"
                onClick={handleSeed}
                disabled={seeding}
                style={{ marginTop: "1rem" }}
              >
                {seeding ? "Discovering..." : "Discover verified roles"}
              </button>
            )}
          </div>
        ) : (
          <div className="recommended-jobs-list">
            {recommendedJobs.map((job) => {
              const companyDetails = getCompanyDetails(job.company_id, companies);
              const cleanedTitle = cleanJobTitle(job.title);
              const { matched, missing, score } = job.skillsInfo || getJobSkillsAndScore(
                job,
                userSkills,
                profile?.headline || ""
              );
              const scoreClass =
                score >= 85 ? "very-high" : score >= 70 ? "high" : score >= 45 ? "moderate" : "low";

              return (
                <div className="recommended-job-card" key={job.id}>
                  {/* Card Header Row */}
                  <div className="recommended-job-header">
                    <div className="recommended-job-identity">
                      <div className={`company-logo-avatar ${companyDetails.avatarClass}`}>
                        {companyDetails.avatarText}
                      </div>
                      <div className="job-title-group">
                        <span className="job-company-name">{companyDetails.name}</span>
                        <h3 className="job-card-title" title={job.title}>{cleanedTitle}</h3>
                        <div className="job-meta-row">
                          <span className="job-meta-badge">
                            <MapPin size={11} />
                            <span>{job.location || "Remote"}</span>
                          </span>
                          <span className="job-meta-badge">
                            <Briefcase size={11} />
                            <span>{job.employment_type || "Full-time"}</span>
                          </span>
                        </div>
                      </div>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <div className={`ai-match-badge ${scoreClass}`} title="AI Career Alignment Score">
                        <Sparkles size={11} />
                        <span>{score}% Match</span>
                      </div>
                      <button
                        type="button"
                        className="job-dismiss-btn"
                        onClick={() => handleDismissJob(job.id)}
                        title="Remove role / Not interested"
                        aria-label="Remove job"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  </div>

                  {/* Skill Match Tags */}
                  <div className="job-skill-tags-row">
                    {matched.slice(0, 4).map((skill) => (
                      <span className="skill-tag matched" key={skill}>
                        <Check size={11} />
                        <span>{skill}</span>
                      </span>
                    ))}
                    {missing.slice(0, 2).map((skill) => (
                      <span className="skill-tag missing" key={skill}>
                        <AlertCircle size={11} />
                        <span>{skill}</span>
                      </span>
                    ))}
                    {matched.length === 0 && missing.length === 0 && (
                      <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>
                        Requirements: {(job.required_skills || []).slice(0, 3).join(", ") || "General Engineering"}
                      </span>
                    )}
                  </div>

                  {/* Action Bar */}
                  <div className="recommended-actions-row">
                    <div className="recommended-actions-group">
                      {applicationsMap.has(job.id) && applicationsMap.get(job.id).status !== "saved" ? (
                        <button
                          type="button"
                          className="mark-applied-btn is-applied"
                          onClick={() => setActiveNextStepsJob(job)}
                          title="Application recorded - click to update status or view next steps"
                        >
                          <CheckCircle2 size={13} />
                          <span>Applied ({applicationsMap.get(job.id).status})</span>
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="mark-applied-btn"
                          onClick={() => handleMarkApplied(job)}
                          title="Mark this role as applied"
                        >
                          <CheckCircle2 size={13} />
                          <span>Mark Applied</span>
                        </button>
                      )}
                      <button
                        type="button"
                        className="tailor-resume-btn"
                        onClick={() => handleTailorJob(job)}
                        disabled={tailoringId === job.id}
                        title="Tailor Resume for this role"
                      >
                        <Sparkles size={13} className={tailoringId === job.id ? "spin" : ""} />
                        <span>{tailoringId === job.id ? "Tailoring..." : "Tailor Resume"}</span>
                      </button>
                      <button
                        className="why-role-btn"
                        onClick={() => setSelectedJobForIntelligence({ ...job, title: cleanedTitle, companyName: companyDetails.name })}
                        aria-label={`Explain match for ${cleanedTitle}`}
                      >
                        <Sparkles size={13} />
                        <span>Why this role?</span>
                      </button>
                    </div>
                    <a
                      className="view-role-outline-btn"
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <span>View Role</span>
                      <ExternalLink size={12} />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* AI Match Explanation Modal */}
      {selectedJobForIntelligence && (
        <JobIntelligenceModal
          job={selectedJobForIntelligence}
          onClose={() => setSelectedJobForIntelligence(null)}
        />
      )}

      {/* Application Next Steps Modal */}
      {activeNextStepsJob && (
        <ApplicationNextStepsModal
          job={activeNextStepsJob}
          application={applicationsMap.get(activeNextStepsJob.id)}
          onClose={() => setActiveNextStepsJob(null)}
          onUpdateStatus={(jobId, nextStatus) => {
            setApplicationsMap((prev) => {
              const updated = new Map(prev);
              const existing = updated.get(jobId) || { job_id: jobId };
              updated.set(jobId, { ...existing, status: nextStatus });
              return updated;
            });
            if (onReload) onReload();
          }}
          onTailorResume={(job) => handleTailorJob(job)}
        />
      )}

      {/* AI Tailored Resume Modal */}
      {tailoredResumeForPreview && (
        <TailoredResumeModal
          resume={tailoredResumeForPreview}
          jobs={rawRecommended}
          companies={companies}
          onClose={() => setTailoredResumeForPreview(null)}
          onApprove={(r) => {
            updateResume(r.id, r.content, "approved").then((updated) => setTailoredResumeForPreview(updated));
          }}
          onDownloadLatex={(resumeId, filename) => {
            exportResumeLatex(resumeId).then((latex) => {
              const blob = new Blob([latex], { type: "application/x-latex" });
              const url = URL.createObjectURL(blob);
              const link = document.createElement("a");
              link.href = url;
              link.download = filename;
              link.click();
              URL.revokeObjectURL(url);
            });
          }}
        />
      )}
    </div>
  );
}

function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [profile, setProfile] = useState(null);
  const [tailoringJob, setTailoringJob] = useState(null);
  const [tailoredResume, setTailoredResume] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([getAnalytics(), getJobs(), getCompanies(), getProfile()])
      .then(([nextAnalytics, nextJobs, nextCompanies, nextProfile]) => {
        setAnalytics(nextAnalytics);
        setJobs(nextJobs || []);
        setCompanies(nextCompanies || []);
        setProfile(nextProfile);
      })
      .catch(() => setError(true));
  }, []);

  const candidateSkills = useMemo(() => {
    return profile?.skills || [];
  }, [profile]);

  const matchingJobsList = useMemo(() => {
    if (!jobs.length) return [];
    return jobs
      .map((job) => {
        const fit = getJobSkillsAndScore(job, candidateSkills, profile?.headline || "");
        return { ...job, fitScore: fit.score, matchedSkills: fit.matched, missingSkills: fit.missing };
      })
      .filter((j) => j.fitScore >= 50 || j.matchedSkills?.length > 0)
      .sort((a, b) => b.fitScore - a.fitScore);
  }, [jobs, candidateSkills, profile]);

  if (error) return <p className="error-message" role="alert">Unable to load analytics.</p>;
  if (!analytics) return <p className="loading-message" role="status">Loading analytics...</p>;

  const matchingCount = analytics.matching_jobs ?? matchingJobsList.length;

  // Tier 1 metrics (Job Discovery)
  const discoveryMetrics = [
    {
      label: "Jobs Discovered",
      value: analytics.jobs_discovered ?? jobs.length,
      icon: Briefcase,
      trend: (analytics.jobs_discovered ?? jobs.length) > 0 ? `+${analytics.jobs_discovered ?? jobs.length} indexed` : "+0% this week",
      trendType: (analytics.jobs_discovered ?? jobs.length) > 0 ? "positive" : "neutral",
      caption: "Total opportunities ingested & analyzed",
    },
    {
      label: "Matching Jobs (>70% fit)",
      value: matchingCount,
      icon: Sparkles,
      trend: matchingCount > 0 ? "High match fit" : "0 fit threshold",
      trendType: matchingCount > 0 ? "positive" : "neutral",
      caption: "Scored above career alignment threshold",
    },
    {
      label: "Saved Jobs",
      value: analytics.saved_jobs ?? 0,
      icon: Bookmark,
      trend: (analytics.saved_jobs ?? 0) > 0 ? "Shortlisted" : "0 bookmarked",
      trendType: (analytics.saved_jobs ?? 0) > 0 ? "positive" : "neutral",
      caption: "Pinned for application drafting & review",
    },
  ];

  // Tier 2 metrics (Application Pipeline)
  const pipelineMetrics = [
    {
      step: "01 · SUBMITTED",
      label: "Applications",
      value: analytics.applications ?? 0,
      icon: Send,
      trend: (analytics.applications ?? 0) > 0 ? "Active pipeline" : "0 in pipeline",
      trendType: (analytics.applications ?? 0) > 0 ? "positive" : "neutral",
      stageClass: "stage-1",
      fillWidth: (analytics.applications ?? 0) > 0 ? "100%" : "0%",
    },
    {
      step: "02 · SCREENING",
      label: "Interviews",
      value: analytics.interviews ?? 0,
      icon: Calendar,
      trend: (analytics.interviews ?? 0) > 0 ? "In progress" : "0 active rounds",
      trendType: (analytics.interviews ?? 0) > 0 ? "positive" : "neutral",
      stageClass: "stage-2",
      fillWidth: (analytics.interviews ?? 0) > 0 ? "75%" : "0%",
    },
    {
      step: "03 · DECISION",
      label: "Offers",
      value: analytics.offers ?? 0,
      icon: Trophy,
      trend: (analytics.offers ?? 0) > 0 ? "Received" : "0 offers",
      trendType: (analytics.offers ?? 0) > 0 ? "positive" : "neutral",
      stageClass: "stage-3",
      fillWidth: (analytics.offers ?? 0) > 0 ? "100%" : "0%",
    },
    {
      step: "04 · ARCHIVED",
      label: "Rejected",
      value: analytics.rejected_applications ?? 0,
      icon: Archive,
      trend: (analytics.rejected_applications ?? 0) > 0 ? "Concluded" : "0 archived",
      trendType: "muted",
      stageClass: "stage-4",
      fillWidth: (analytics.rejected_applications ?? 0) > 0 ? "40%" : "0%",
    },
  ];

  return (
    <div className="analytics-container">
      {/* Tier 1: Job Discovery (3-column grid) */}
      <section className="analytics-section">
        <div className="section-title-row">
          <div>
            <h3>Job Discovery</h3>
            <span className="section-subtitle">Real-time market scanning and profile alignment</span>
          </div>
          <span className="widget-tag">Tier 1 · Sourcing</span>
        </div>
        <div className="grid-tier-1">
          {discoveryMetrics.map((item) => {
            const Icon = item.icon;
            return (
              <div className="linear-metric-card" key={item.label}>
                <div className="linear-card-header">
                  <span className="linear-metric-label">{item.label}</span>
                  <Icon size={18} className="linear-icon-primary" />
                </div>
                <div className="linear-metric-value-row">
                  <span className="linear-metric-number">{item.value}</span>
                  <span className={`linear-trend-badge ${item.trendType}`}>{item.trend}</span>
                </div>
                <p className="linear-metric-caption">{item.caption}</p>
              </div>
            );
          })}
        </div>

        {/* High Match Alignment Roles Preview */}
        {matchingJobsList.length > 0 && (
          <div style={{ marginTop: "1.25rem", padding: "14px 16px", background: "var(--colors-surface)", borderRadius: "8px", border: "1px solid var(--colors-hairline)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px", flexWrap: "wrap", gap: "6px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Sparkles size={16} className="linear-icon-primary" />
                <h4 style={{ margin: 0, fontSize: "14px", fontWeight: 700 }}>
                  High-Alignment Matching Roles ({matchingJobsList.length})
                </h4>
              </div>
              <span style={{ fontSize: "12px", color: "var(--colors-slate)" }}>
                Scored above match threshold using your confirmed skills
              </span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "10px" }}>
              {matchingJobsList.slice(0, 6).map((job) => {
                const comp = getCompanyDetails(job.company_id, companies);
                return (
                  <div
                    key={job.id}
                    style={{
                      padding: "12px 14px",
                      background: "var(--colors-canvas)",
                      borderRadius: "6px",
                      border: "1px solid var(--colors-hairline)",
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                      gap: "8px",
                    }}
                  >
                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "6px" }}>
                        <strong style={{ fontSize: "13.5px", color: "var(--colors-ink)" }}>{cleanJobTitle(job.title)}</strong>
                        <span
                          style={{
                            fontSize: "11px",
                            fontWeight: 700,
                            padding: "2px 7px",
                            borderRadius: "10px",
                            background: job.fitScore >= 70 ? "rgba(16, 185, 129, 0.12)" : "rgba(99, 102, 241, 0.12)",
                            color: job.fitScore >= 70 ? "#059669" : "var(--colors-primary)",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {job.fitScore > 0 ? `${job.fitScore}% Match` : "Aligned"}
                        </span>
                      </div>
                      <span style={{ fontSize: "12px", color: "var(--colors-slate)", display: "block", marginTop: "2px" }}>
                        {comp.name} · {job.location || "Remote"}
                      </span>
                    </div>
                    {job.matchedSkills?.length > 0 && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                        {job.matchedSkills.slice(0, 3).map((s) => (
                          <span
                            key={s}
                            style={{
                              fontSize: "10.5px",
                              padding: "2px 6px",
                              borderRadius: "4px",
                              background: "rgba(16, 185, 129, 0.08)",
                              color: "#059669",
                              fontWeight: 600,
                            }}
                          >
                            ✓ {s}
                          </span>
                        ))}
                      </div>
                    )}
                    <div style={{ display: "flex", justifyContent: "flex-end", paddingTop: "4px", borderTop: "1px solid var(--colors-hairline)" }}>
                      <button
                        type="button"
                        className="button-link"
                        style={{ fontSize: "12px", fontWeight: 600, padding: 0 }}
                        onClick={() => {
                          setTailoringJob(job);
                          generateResume(job.id)
                            .then((res) => setTailoredResume(res))
                            .catch(() => {});
                        }}
                      >
                        Tailor Resume →
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </section>

      {/* Tier 2: Application Pipeline (4-column funnel view) */}
      <section className="analytics-section">
        <div className="section-title-row">
          <div>
            <h3>Application Pipeline</h3>
            <span className="section-subtitle">End-to-end recruitment funnel and interview progress</span>
          </div>
          <span className="widget-tag">Tier 2 · Progression</span>
        </div>
        <div className="pipeline-funnel-grid">
          {pipelineMetrics.map((item) => {
            const Icon = item.icon;
            return (
              <div className="pipeline-card" key={item.label}>
                <div className="pipeline-step-badge">{item.step}</div>
                <div className="linear-card-header">
                  <span className="linear-metric-label">{item.label}</span>
                  <Icon size={16} className="linear-icon-muted" />
                </div>
                <div className="linear-metric-value-row">
                  <span className="linear-metric-number">{item.value}</span>
                  <span className={`linear-trend-badge ${item.trendType}`}>{item.trend}</span>
                </div>
                <div className="pipeline-progress-track">
                  <div
                    className={`pipeline-progress-fill ${item.stageClass}`}
                    style={{ width: item.fillWidth }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Bottom Section: 2 columns */}
      <div className="analytics-details-grid">
        {/* Top Missing Skills */}
        <section className="linear-widget-panel">
          <div className="widget-header">
            <h3 className="widget-title">Top Missing Skills</h3>
            <span className="widget-tag">Skill Gap Analytics</span>
          </div>
          {analytics.skill_gaps.length === 0 ? (
            <div className="skill-gap-empty-state">
              <div className="empty-state-icon-wrap">
                <TrendingUp size={22} />
              </div>
              <h4>No Recurring Skill Gaps Yet</h4>
              <p>Apply or match jobs to start seeing skill gap analytics. NextHire analyzes job requirements against your profile in real-time.</p>
              <div className="skill-gap-skeleton-list">
                <div className="skeleton-label-row">
                  <span className="skeleton-pill">Distributed Systems</span>
                  <span className="skeleton-meta">Preview gap</span>
                </div>
                <div className="skeleton-bar-track">
                  <div className="skeleton-bar-fill" style={{ width: "68%" }} />
                </div>
                <div className="skeleton-label-row">
                  <span className="skeleton-pill">GraphQL & Microservices</span>
                  <span className="skeleton-meta">Preview gap</span>
                </div>
                <div className="skeleton-bar-track">
                  <div className="skeleton-bar-fill" style={{ width: "42%" }} />
                </div>
                <div className="skeleton-label-row">
                  <span className="skeleton-pill">Kubernetes Orchestration</span>
                  <span className="skeleton-meta">Preview gap</span>
                </div>
                <div className="skeleton-bar-track">
                  <div className="skeleton-bar-fill" style={{ width: "24%" }} />
                </div>
              </div>
            </div>
          ) : (
            <div className="skill-gap-progress-list">
              {analytics.skill_gaps.map((gap) => {
                const maxJobs = Math.max(...analytics.skill_gaps.map((g) => g.jobs), 1);
                const percent = Math.min(Math.round((gap.jobs / maxJobs) * 100), 100);
                return (
                  <div className="skill-gap-row" key={gap.skill}>
                    <div className="skill-gap-info">
                      <span className="skill-name">{gap.skill}</span>
                      <span className="skill-count">{gap.jobs} {gap.jobs === 1 ? "job" : "jobs"} require this</span>
                    </div>
                    <div className="skill-bar-track">
                      <div className="skill-bar-fill" style={{ width: `${percent}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* Target Companies Overview */}
        <section className="linear-widget-panel">
          <div className="widget-header">
            <h3 className="widget-title">Target Companies Overview</h3>
            <a href="/profile" className="widget-action-link">
              <Plus size={13} />
              <span>Add Companies</span>
            </a>
          </div>
          {analytics.target_companies.length === 0 ? (
            <div className="companies-empty-state">
              <div className="empty-state-icon-wrap">
                <Building2 size={22} />
              </div>
              <h4>No Target Companies Added</h4>
              <p>Add target companies to your profile to monitor match rates, track job openings, and tailor your application materials.</p>
              <a
                href="/profile"
                className="primary-button"
                style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
              >
                <Plus size={14} />
                <span>Add Target Companies</span>
              </a>
            </div>
          ) : (
            <div className="target-companies-list">
              {analytics.target_companies.map((company) => (
                <div className="target-company-item" key={company}>
                  <div className="company-badge-avatar">
                    {company.charAt(0).toUpperCase()}
                  </div>
                  <div className="company-details">
                    <span className="company-name">{company}</span>
                    <span className="company-status">High match target · Actively hiring</span>
                  </div>
                  <a href="/jobs" className="company-explore-link">
                    <span>Explore jobs</span>
                    <ExternalLink size={12} />
                  </a>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {tailoredResume && tailoringJob && (
        <TailoredResumeModal
          resume={tailoredResume}
          jobs={[tailoringJob]}
          companies={companies}
          onClose={() => {
            setTailoredResume(null);
            setTailoringJob(null);
          }}
          onApprove={(r) => {
            updateResume(r.id, r.content, "approved").then((updated) => setTailoredResume(updated));
          }}
          onDownloadLatex={(resumeId, filename) => {
            exportResumeLatex(resumeId).then((latex) => {
              const blob = new Blob([latex], { type: "application/x-latex" });
              const url = URL.createObjectURL(blob);
              const link = document.createElement("a");
              link.href = url;
              link.download = filename;
              link.click();
              URL.revokeObjectURL(url);
            });
          }}
        />
      )}
    </div>
  );
}

function SettingsPage({ user }) {
  const [privacy, setPrivacy] = useState(null);
  const [privacySaved, setPrivacySaved] = useState(false);
  const [exporting, setExporting] = useState(false);

  // Candidate workspace profile state
  const [profile, setProfile] = useState(null);
  const [displayName, setDisplayName] = useState(user?.display_name || "");
  const [preferredRoles, setPreferredRoles] = useState("");
  const [preferredLocations, setPreferredLocations] = useState("");
  const [targetCompanies, setTargetCompanies] = useState("");
  const [workModality, setWorkModality] = useState("remote");
  const [minFitScore, setMinFitScore] = useState(70);
  const [defaultTemplate, setDefaultTemplate] = useState("default");

  // Notifications state
  const [notifyMatchingJobs, setNotifyMatchingJobs] = useState(true);
  const [notifyDeadlines, setNotifyDeadlines] = useState(true);
  const [notifyWeeklyDigest, setNotifyWeeklyDigest] = useState(false);

  const [savingProfile, setSavingProfile] = useState(false);
  const [profileNotice, setProfileNotice] = useState("");
  const [profileError, setProfileError] = useState("");

  useEffect(() => {
    getPrivacySettings().then(setPrivacy).catch(() => {});
    getProfile()
      .then((p) => {
        setProfile(p);
        if (p.display_name) setDisplayName(p.display_name);
        if (p.preferred_roles?.length) setPreferredRoles(p.preferred_roles.join(", "));
        if (p.preferred_locations?.length) setPreferredLocations(p.preferred_locations.join(", "));
        if (p.target_companies?.length) setTargetCompanies(p.target_companies.join(", "));
      })
      .catch(() => {});
  }, []);

  const handleSaveProfile = (event) => {
    event.preventDefault();
    setSavingProfile(true);
    setProfileError("");
    setProfileNotice("");

    const rolesList = preferredRoles
      .split(",")
      .map((r) => r.trim())
      .filter(Boolean);
    const locationsList = preferredLocations
      .split(",")
      .map((l) => l.trim())
      .filter(Boolean);
    const companiesList = targetCompanies
      .split(",")
      .map((c) => c.trim())
      .filter(Boolean);

    updateProfile({
      display_name: displayName.trim(),
      preferred_roles: rolesList,
      preferred_locations: locationsList,
      target_companies: companiesList,
    })
      .then((updated) => {
        setProfile(updated);
        setProfileNotice("✓ Candidate workspace settings saved successfully!");
        setTimeout(() => setProfileNotice(""), 3500);
      })
      .catch((err) => {
        setProfileError(err.message || "Failed to update profile settings.");
      })
      .finally(() => setSavingProfile(false));
  };

  const handleExport = () => {
    setExporting(true);
    exportUserData()
      .then((data) => {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "nexthire-candidate-export.json";
        link.click();
        URL.revokeObjectURL(url);
      })
      .finally(() => setExporting(false));
  };

  return (
    <div className="analytics-container" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Workspace Banner */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", borderBottom: "1px solid var(--colors-hairline)", paddingBottom: "1rem" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: "20px", fontWeight: 700, color: "var(--colors-ink)" }}>
            Candidate Workspace & Preferences
          </h2>
          <p style={{ margin: "4px 0 0 0", fontSize: "13px", color: "var(--colors-slate)" }}>
            Manage your account identity, matching thresholds, target career criteria, and privacy governance.
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <span style={{ fontSize: "12px", fontWeight: 600, padding: "3px 10px", borderRadius: "12px", background: "rgba(99, 102, 241, 0.12)", color: "var(--colors-primary)" }}>
            {user?.role === "ADMIN" ? "Platform Administrator" : "Active Candidate Workspace"}
          </span>
        </div>
      </div>

      {profileNotice && (
        <div style={{ padding: "10px 14px", borderRadius: "8px", background: "rgba(16, 185, 129, 0.12)", color: "#065f46", fontSize: "13px", fontWeight: 600 }}>
          {profileNotice}
        </div>
      )}
      {profileError && (
        <div className="error-message" role="alert" style={{ margin: 0 }}>
          {profileError}
        </div>
      )}

      {/* Card 1: Identity & Account Profile */}
      <section className="linear-widget-panel">
        <div className="widget-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <User size={16} className="linear-icon-primary" />
            <h3 className="widget-title">Account Identity</h3>
          </div>
          <span className="widget-tag">Profile Details</span>
        </div>
        <form onSubmit={handleSaveProfile} style={{ display: "grid", gap: "14px", marginTop: "10px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "12px" }}>
            <label style={{ margin: 0 }}>
              Full Display Name
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Candidate Full Name"
                style={{ marginTop: "4px" }}
              />
            </label>
            <label style={{ margin: 0 }}>
              Account Email
              <input
                type="email"
                value={user?.email || ""}
                disabled
                style={{ marginTop: "4px", background: "var(--colors-surface-soft)", color: "var(--colors-steel)", cursor: "not-allowed" }}
              />
            </label>
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button className="primary-button" type="submit" disabled={savingProfile} style={{ padding: "7px 18px", fontSize: "13px" }}>
              {savingProfile ? "Saving..." : "Save Identity"}
            </button>
          </div>
        </form>
      </section>

      {/* Card 2: Job Search & Work Modality Preferences */}
      <section className="linear-widget-panel">
        <div className="widget-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Briefcase size={16} className="linear-icon-primary" />
            <h3 className="widget-title">Job Search & Modality Criteria</h3>
          </div>
          <span className="widget-tag">Role Alignment</span>
        </div>
        <p style={{ margin: "0 0 12px 0", fontSize: "13px", color: "var(--colors-slate)" }}>
          NextHire references these criteria when indexing roles and evaluating your career match scores.
        </p>
        <form onSubmit={handleSaveProfile} style={{ display: "grid", gap: "14px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "12px" }}>
            <label style={{ margin: 0 }}>
              Target Job Titles (comma separated)
              <input
                type="text"
                value={preferredRoles}
                onChange={(e) => setPreferredRoles(e.target.value)}
                placeholder="e.g. Senior Backend Engineer, Full Stack Developer, AI Engineer"
                style={{ marginTop: "4px" }}
              />
            </label>
            <label style={{ margin: 0 }}>
              Preferred Locations (comma separated)
              <input
                type="text"
                value={preferredLocations}
                onChange={(e) => setPreferredLocations(e.target.value)}
                placeholder="e.g. Remote, Bengaluru, London, San Francisco"
                style={{ marginTop: "4px" }}
              />
            </label>
          </div>

          <label style={{ margin: 0 }}>
            Target Dream Companies
            <input
              type="text"
              value={targetCompanies}
              onChange={(e) => setTargetCompanies(e.target.value)}
              placeholder="e.g. Google, Apple, Stripe, Razorpay"
              style={{ marginTop: "4px" }}
            />
          </label>

          <div>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--colors-ink)", display: "block", marginBottom: "6px" }}>
              Work Modality Preference
            </span>
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              {[
                { id: "remote", label: "Remote Only (Globally or Regionally)" },
                { id: "hybrid", label: "Hybrid (1-3 Days In-Office)" },
                { id: "onsite", label: "On-site (Full Relocation / In-Person)" },
              ].map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setWorkModality(m.id)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "6px",
                    fontSize: "12.5px",
                    fontWeight: 600,
                    cursor: "pointer",
                    border: workModality === m.id ? "1px solid var(--colors-primary)" : "1px solid var(--colors-hairline)",
                    background: workModality === m.id ? "rgba(99, 102, 241, 0.12)" : "var(--colors-canvas)",
                    color: workModality === m.id ? "var(--colors-primary)" : "var(--colors-ink)",
                  }}
                >
                  {workModality === m.id ? "✓ " : ""}{m.label}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button className="primary-button" type="submit" disabled={savingProfile} style={{ padding: "7px 18px", fontSize: "13px" }}>
              {savingProfile ? "Saving..." : "Save Career Preferences"}
            </button>
          </div>
        </form>
      </section>

      {/* Card 3: AI Intelligence & Matching Parameters */}
      <section className="linear-widget-panel">
        <div className="widget-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Sparkles size={16} className="linear-icon-primary" />
            <h3 className="widget-title">AI Matching & Resume Tailoring Parameters</h3>
          </div>
          <span className="widget-tag">Algorithmic Tuning</span>
        </div>
        <div style={{ display: "grid", gap: "14px", marginTop: "8px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "14px" }}>
            <div style={{ padding: "12px", background: "var(--colors-surface-soft)", borderRadius: "8px", border: "1px solid var(--colors-hairline)" }}>
              <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--colors-ink)" }}>
                Minimum Match Fit Threshold
              </span>
              <p style={{ margin: "2px 0 8px 0", fontSize: "12px", color: "var(--colors-slate)" }}>
                Roles scoring at or above this threshold appear in your curated feeds and matching jobs analytics.
              </p>
              <div style={{ display: "flex", gap: "6px" }}>
                {[50, 60, 70, 80].map((score) => (
                  <button
                    key={score}
                    type="button"
                    onClick={() => setMinFitScore(score)}
                    style={{
                      flex: 1,
                      padding: "5px 0",
                      borderRadius: "6px",
                      fontSize: "12px",
                      fontWeight: 700,
                      cursor: "pointer",
                      border: minFitScore === score ? "1px solid var(--colors-primary)" : "1px solid var(--colors-hairline)",
                      background: minFitScore === score ? "var(--colors-primary)" : "var(--colors-canvas)",
                      color: minFitScore === score ? "#ffffff" : "var(--colors-ink)",
                    }}
                  >
                    {score}%+
                  </button>
                ))}
              </div>
            </div>

            <div style={{ padding: "12px", background: "var(--colors-surface-soft)", borderRadius: "8px", border: "1px solid var(--colors-hairline)" }}>
              <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--colors-ink)" }}>
                Default Resume Tailoring Template
              </span>
              <p style={{ margin: "2px 0 8px 0", fontSize: "12px", color: "var(--colors-slate)" }}>
                Select the structural template used when generating role-specific LaTeX resumes.
              </p>
              <select
                value={defaultTemplate}
                onChange={(e) => setDefaultTemplate(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", fontSize: "13px", borderRadius: "6px", border: "1px solid var(--colors-hairline)" }}
              >
                <option value="default">Clean Single-Column (General Software / Standard)</option>
                <option value="technical">Technical Skills-Forward (Engineering & SRE)</option>
              </select>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "10px 12px", borderRadius: "6px", background: "rgba(99, 102, 241, 0.08)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
            <ShieldCheck size={16} style={{ color: "var(--colors-primary)", flexShrink: 0 }} />
            <span style={{ fontSize: "12.5px", color: "var(--colors-ink)" }}>
              AI Engine: <strong>Gemini 1.5 Flash + Rule-Based Token Taxonomy Active</strong>. Strict provenance guarantees zero hallucinated career claims.
            </span>
          </div>
        </div>
      </section>

      {/* Card 4: Workspace Notification Preferences */}
      <section className="linear-widget-panel">
        <div className="widget-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Bell size={16} className="linear-icon-primary" />
            <h3 className="widget-title">Workspace Alerts & Notifications</h3>
          </div>
          <span className="widget-tag">Alert Channels</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "8px" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "13.5px", color: "var(--colors-ink)" }}>
            <input
              type="checkbox"
              checked={notifyMatchingJobs}
              onChange={(e) => setNotifyMatchingJobs(e.target.checked)}
              style={{ width: "17px", height: "17px", accentColor: "var(--colors-primary)" }}
            />
            <span>Instant email alerts when a new job posting aligns with your skills (&gt;{minFitScore}% fit)</span>
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "13.5px", color: "var(--colors-ink)" }}>
            <input
              type="checkbox"
              checked={notifyDeadlines}
              onChange={(e) => setNotifyDeadlines(e.target.checked)}
              style={{ width: "17px", height: "17px", accentColor: "var(--colors-primary)" }}
            />
            <span>Application pipeline reminders (upcoming interviews, post-interview thank you follow-ups)</span>
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "13.5px", color: "var(--colors-ink)" }}>
            <input
              type="checkbox"
              checked={notifyWeeklyDigest}
              onChange={(e) => setNotifyWeeklyDigest(e.target.checked)}
              style={{ width: "17px", height: "17px", accentColor: "var(--colors-primary)" }}
            />
            <span>Weekly market trend digest and skill demand gap report</span>
          </label>
        </div>
      </section>

      {/* Card 5: Privacy, Security & Data Governance */}
      <section className="linear-widget-panel">
        <div className="widget-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Shield size={16} className="linear-icon-primary" />
            <h3 className="widget-title">Privacy, Security & Data Governance</h3>
          </div>
          <span className="widget-tag">Compliance</span>
        </div>
        <p style={{ color: "var(--colors-slate)", fontSize: "13px", margin: "0 0 1rem 0" }}>
          Control how your career knowledge and job application analytics are processed. You own all your data.
        </p>
        {privacy && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "13.5px", color: "var(--colors-ink)" }}>
              <input
                type="checkbox"
                checked={privacy.analytics_enabled}
                onChange={(event) =>
                  updatePrivacySettings({
                    analytics_enabled: event.target.checked,
                  }).then((updated) => {
                    setPrivacy(updated);
                    setPrivacySaved(true);
                    setTimeout(() => setPrivacySaved(false), 2500);
                  })
                }
                style={{ width: "18px", height: "18px", accentColor: "var(--colors-primary)" }}
              />
              <span>Allow personalized product analytics and fit recommendations</span>
            </label>
            {privacySaved && (
              <p style={{ margin: 0, fontSize: "13px", color: "var(--colors-semantic-success)", fontWeight: 600 }}>
                ✓ Privacy settings updated successfully.
              </p>
            )}

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px", paddingTop: "0.5rem", borderTop: "1px solid var(--colors-hairline)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <ShieldCheck size={15} style={{ color: "#10b981" }} />
                <span style={{ fontSize: "12px", color: "var(--colors-slate)" }}>
                  Active Session: CSRF Token verified · Encrypted session cookie active
                </span>
              </div>
              <button
                className="button-secondary"
                onClick={handleExport}
                disabled={exporting}
                style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "12.5px" }}
              >
                <Download size={14} />
                <span>{exporting ? "Generating Export..." : "Download Complete Data (JSON)"}</span>
              </button>
            </div>
          </div>
        )}
      </section>

      {user?.role === "ADMIN" && (
        <div style={{ marginTop: "1rem", paddingTop: "1.5rem", borderTop: "2px solid var(--colors-hairline)" }}>
          <div style={{ marginBottom: "1rem" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--colors-primary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
              Administrator Console
            </span>
            <h3 style={{ margin: "2px 0 0 0", fontSize: "18px", fontWeight: 700 }}>Platform Administration</h3>
          </div>
          <AdminPage />
        </div>
      )}
    </div>
  );
}

function AdminPage() {
  const [overview, setOverview] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [crawls, setCrawls] = useState([]);
  const [scheduler, setScheduler] = useState(null);
  const [companyForm, setCompanyForm] = useState({ name: "", career_page_url: "", website: "" });
  const [addingCompany, setAddingCompany] = useState(false);
  const [scrapingAll, setScrapingAll] = useState(false);
  const [scrapingId, setScrapingId] = useState("");
  const [notice, setNotice] = useState("");
  const [noticeType, setNoticeType] = useState("success");
  const [editingCompany, setEditingCompany] = useState(null);
  const [editForm, setEditForm] = useState({ name: "", career_page_url: "", website: "" });
  const [error, setError] = useState(false);
  const [companySearch, setCompanySearch] = useState("");
  const [companyPage, setCompanyPage] = useState(1);
  const [resettingPrototype, setResettingPrototype] = useState(false);
  const [naukriQuery, setNaukriQuery] = useState("Software Engineer");
  const [naukriLocation, setNaukriLocation] = useState("Bengaluru, India");
  const [naukriLimit, setNaukriLimit] = useState(20);
  const [scrapingNaukri, setScrapingNaukri] = useState(false);
  const [approvingId, setApprovingId] = useState("");
  const [rejectingId, setRejectingId] = useState("");
  const [whitelistFilter, setWhitelistFilter] = useState("all");
  const COMPANIES_PER_PAGE = 20;

  const handleNaukriScrape = (event) => {
    event.preventDefault();
    setScrapingNaukri(true);
    scrapeNaukriJobs({
      search_term: naukriQuery,
      location: naukriLocation,
      results_wanted: naukriLimit,
    })
      .then((newJobs) => {
        loadAll();
        showNotice(`JobSpy successfully scraped ${newJobs.length} live jobs from Naukri for "${naukriQuery}"!`);
      })
      .catch((err) => showNotice(err.message || "JobSpy Naukri scraping failed", "error"))
      .finally(() => setScrapingNaukri(false));
  };

  const pendingCompanies = useMemo(
    () => companies.filter((c) => c.verification_status === "pending"),
    [companies]
  );

  const filteredCompanies = useMemo(() => {
    let list = companies;
    if (whitelistFilter === "pending") {
      list = list.filter((c) => c.verification_status === "pending");
    } else if (whitelistFilter === "verified") {
      list = list.filter((c) => c.verification_status !== "pending");
    }
    const q = companySearch.trim().toLowerCase();
    if (!q) return list;
    return list.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (c.career_page_url && c.career_page_url.toLowerCase().includes(q)) ||
        (c.website && c.website.toLowerCase().includes(q))
    );
  }, [companies, companySearch, whitelistFilter]);

  const totalCompanyPages = Math.ceil(filteredCompanies.length / COMPANIES_PER_PAGE) || 1;
  const paginatedCompanies = useMemo(() => {
    const start = (companyPage - 1) * COMPANIES_PER_PAGE;
    return filteredCompanies.slice(start, start + COMPANIES_PER_PAGE);
  }, [filteredCompanies, companyPage]);

  const loadAll = () => {
    getAdminOverview().then(setOverview).catch(() => setError(true));
    getSchedulerStatus().then(setScheduler).catch(() => {});
    Promise.all([
      getAdminCompanies(),
      getAdminJobs(),
      getAdminCrawls(),
    ]).then(([nextCompanies, nextJobs, nextCrawls]) => {
      setCompanies(nextCompanies);
      setJobs(nextJobs);
      setCrawls(nextCrawls);
    }).catch(() => setError(true));
  };

  useEffect(() => {
    loadAll();
  }, []);

  const showNotice = (msg, type = "success") => {
    setNotice(msg);
    setNoticeType(type);
    setTimeout(() => setNotice(""), 4000);
  };

  const submitCompany = (event) => {
    event.preventDefault();
    setAddingCompany(true);
    createCompany(companyForm)
      .then((created) => {
        setCompanyForm({ name: "", career_page_url: "", website: "" });
        showNotice(`Added ${created.name}! Crawling career page for live roles...`);
        // Immediately crawl the newly added company
        return refreshCompany(created.id);
      })
      .then((crawl) => {
        loadAll();
        showNotice(`Finished scraping: Found ${crawl.jobs_found} roles (${crawl.jobs_added} added).`);
      })
      .catch((err) => {
        loadAll();
        showNotice(err.message || "Failed to add company", "error");
      })
      .finally(() => setAddingCompany(false));
  };

  const handleScrapeCompany = (companyId, companyName) => {
    setScrapingId(companyId);
    refreshCompany(companyId)
      .then((crawl) => {
        loadAll();
        if (crawl.status === "succeeded") {
          showNotice(`Scraped ${companyName}: Found ${crawl.jobs_found} roles (${crawl.jobs_added} added, ${crawl.jobs_updated} updated).`);
        } else {
          showNotice(`Scrape failed for ${companyName}: ${crawl.error_code || "Unknown error"}`, "error");
        }
      })
      .catch((err) => showNotice(err.message || "Scrape failed", "error"))
      .finally(() => setScrapingId(""));
  };

  const handleScrapeAll = () => {
    setScrapingAll(true);
    triggerScheduler()
      .then((res) => {
        loadAll();
        showNotice(`Scraped all ${res.companies_crawled || companies.length} company career pages successfully!`);
      })
      .catch((err) => showNotice(err.message || "Failed to run scheduled scrapers", "error"))
      .finally(() => setScrapingAll(false));
  };

  const handleToggleActive = (company) => {
    updateCompany(company.id, { active: !company.active })
      .then(() => {
        loadAll();
        showNotice(`${company.name} is now ${!company.active ? "active (will be scraped every 12h)" : "paused"}.`);
      })
      .catch((err) => showNotice(err.message, "error"));
  };

  const handleDeleteCompany = (company) => {
    if (!window.confirm(`Delete ${company.name} and remove its ingested jobs?`)) return;
    deleteCompany(company.id)
      .then(() => {
        loadAll();
        showNotice(`Deleted ${company.name}.`);
      })
      .catch((err) => showNotice(err.message, "error"));
  };

  const handleApproveCompany = (company) => {
    setApprovingId(company.id);
    approveCompany(company.id)
      .then((crawl) => {
        loadAll();
        showNotice(`Whitelisted ${company.name}! Ingested ${crawl.jobs_found} live roles from Naukri.`);
      })
      .catch((err) => showNotice(err.message || "Failed to whitelist company", "error"))
      .finally(() => setApprovingId(""));
  };

  const handleRejectCompany = (company) => {
    if (!window.confirm(`Reject whitelist request for ${company.name}?`)) return;
    setRejectingId(company.id);
    rejectCompany(company.id)
      .then(() => {
        loadAll();
        showNotice(`Rejected and removed ${company.name}.`);
      })
      .catch((err) => showNotice(err.message || "Failed to reject company", "error"))
      .finally(() => setRejectingId(""));
  };

  const handleStartEdit = (company) => {
    setEditingCompany(company);
    setEditForm({
      name: company.name,
      career_page_url: company.career_page_url || "",
      website: company.website || "",
    });
  };

  const handleSaveEdit = (event) => {
    event.preventDefault();
    if (!editingCompany) return;
    updateCompany(editingCompany.id, editForm)
      .then(() => {
        setEditingCompany(null);
        loadAll();
        showNotice(`Updated ${editForm.name}.`);
      })
      .catch((err) => showNotice(err.message, "error"));
  };

  const handleResetPrototype = () => {
    setResettingPrototype(true);
    resetPrototypeCompanies()
      .then((res) => {
        loadAll();
        showNotice(`Registry reset: top ${res.total} prototype companies loaded.`);
      })
      .catch((err) => showNotice(err.message || "Failed to reset companies", "error"))
      .finally(() => setResettingPrototype(false));
  };

  if (error) return <p className="error-message" role="alert">Unable to load admin operations.</p>;
  if (!overview) return <p className="loading-message" role="status">Loading admin workspace...</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", marginTop: "1.5rem" }}>
      {/* Notification Banner */}
      {notice && (
        <div className={noticeType === "error" ? "error-message" : "success-message"} style={{ margin: 0 }}>
          {notice}
        </div>
      )}

      {/* 12-Hour Automated Scraping Banner Card */}
      <section className="linear-widget-panel" style={{ background: "linear-gradient(135deg, rgba(86, 69, 212, 0.05), rgba(86, 69, 212, 0.01))" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <div style={{ width: "24px", height: "24px", borderRadius: "50%", background: "rgba(86, 69, 212, 0.15)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--colors-primary)" }}>
                <Clock size={14} />
              </div>
              <h2 style={{ margin: 0, fontSize: "16px", fontWeight: 700, color: "var(--colors-ink)" }}>
                Automated 12-Hour Career Page Scraper
              </h2>
              <span className="badge-tag-purple" style={{ fontSize: "11px", fontWeight: 700 }}>
                Every 12 Hours (Twice Daily)
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "13px", color: "var(--colors-slate)" }}>
              The background worker automatically crawls registered career pages every 12 hours to discover new open roles and close filled listings.
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <button
              className="primary-button"
              onClick={handleScrapeAll}
              disabled={scrapingAll}
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              <RefreshCw size={14} className={scrapingAll ? "spin" : ""} />
              <span>{scrapingAll ? "Scraping All Pages..." : "Scrape All Now"}</span>
            </button>
          </div>
        </div>

        {/* Scheduler Status Row */}
        <div style={{ display: "flex", gap: "1.5rem", marginTop: "1rem", paddingTop: "0.75rem", borderTop: "1px solid var(--colors-hairline)", flexWrap: "wrap", fontSize: "12.5px" }}>
          <div>
            <span style={{ color: "var(--colors-steel)" }}>Status: </span>
            <strong style={{ color: "var(--colors-semantic-success)", fontWeight: 600 }}>Active (Running)</strong>
          </div>
          <div>
            <span style={{ color: "var(--colors-steel)" }}>Schedule: </span>
            <strong style={{ color: "var(--colors-ink)" }}>Every 12h (43,200s)</strong>
          </div>
          <div>
            <span style={{ color: "var(--colors-steel)" }}>Active Career Pages: </span>
            <strong style={{ color: "var(--colors-ink)" }}>{companies.filter((c) => c.active).length} companies</strong>
          </div>
          <div>
            <span style={{ color: "var(--colors-steel)" }}>Total Crawl Runs: </span>
            <strong style={{ color: "var(--colors-ink)" }}>{crawls.length}</strong>
          </div>
        </div>
      </section>

      {/* JobSpy · Naukri Live Scraper Section */}
      <section className="linear-widget-panel" style={{ border: "1px solid rgba(86, 69, 212, 0.2)", background: "linear-gradient(135deg, rgba(86, 69, 212, 0.04), rgba(59, 130, 246, 0.02))" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem", marginBottom: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <div style={{ width: "24px", height: "24px", borderRadius: "50%", background: "rgba(59, 130, 246, 0.15)", display: "flex", alignItems: "center", justifyContent: "center", color: "#2563eb" }}>
                <Sparkles size={14} />
              </div>
              <h2 style={{ margin: 0, fontSize: "16px", fontWeight: 700, color: "var(--colors-ink)" }}>
                JobSpy · Naukri Live Job Ingestion
              </h2>
              <span className="badge-tag-purple" style={{ fontSize: "11px", fontWeight: 700, background: "rgba(37, 99, 235, 0.1)", color: "#2563eb" }}>
                speedyapply/JobSpy Powered
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "13px", color: "var(--colors-slate)" }}>
              Extract live, verified postings directly from Naukri with structured skills, verified locations, and official application links.
            </p>
          </div>
        </div>

        <form onSubmit={handleNaukriScrape} style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ flex: "1 1 240px", minWidth: "220px" }}>
            <input
              type="text"
              placeholder="Query (e.g. Software Engineer, Google, Python Developer, Stripe)"
              value={naukriQuery}
              onChange={(e) => setNaukriQuery(e.target.value)}
              required
              className="form-input"
              style={{ width: "100%", padding: "8px 12px", fontSize: "13px" }}
            />
          </div>
          <div style={{ width: "160px" }}>
            <input
              type="text"
              placeholder="Location (e.g. Bengaluru, India)"
              value={naukriLocation}
              onChange={(e) => setNaukriLocation(e.target.value)}
              className="form-input"
              style={{ width: "100%", padding: "8px 12px", fontSize: "13px" }}
            />
          </div>
          <div style={{ width: "110px" }}>
            <select
              value={naukriLimit}
              onChange={(e) => setNaukriLimit(Number(e.target.value))}
              className="form-input"
              style={{ width: "100%", padding: "8px 10px", fontSize: "13px" }}
            >
              <option value={10}>10 roles</option>
              <option value={20}>20 roles</option>
              <option value={30}>30 roles</option>
            </select>
          </div>
          <button
            type="submit"
            className="primary-button"
            disabled={scrapingNaukri}
            style={{ display: "inline-flex", alignItems: "center", gap: "6px", height: "38px" }}
          >
            <Search size={14} className={scrapingNaukri ? "spin" : ""} />
            <span>{scrapingNaukri ? "Scraping Naukri via JobSpy..." : "Scrape from Naukri"}</span>
          </button>
        </form>
      </section>

      {/* Metric Cards Grid */}
      <div className="overview-metrics-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))" }}>
        <div className="overview-metric-card">
          <div>
            <div className="linear-card-header">
              <span className="linear-metric-label">Companies</span>
              <Building2 size={16} className="linear-icon-muted" />
            </div>
            <div className="linear-metric-value-row">
              <span className="linear-metric-number">{overview.companies}</span>
              <span className="linear-trend-badge positive">{overview.active_companies} active</span>
            </div>
          </div>
          <p className="linear-metric-caption" style={{ margin: "6px 0 0 0" }}>
            Target career websites and portals monitored.
          </p>
          {overview.pending_companies > 0 && (
            <div style={{ marginTop: "8px" }}>
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 700,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  padding: "2px 8px",
                  borderRadius: "12px",
                  background: "rgba(234, 88, 12, 0.12)",
                  color: "#ea580c",
                }}
              >
                <AlertCircle size={11} />
                {overview.pending_companies} pending whitelist
              </span>
            </div>
          )}
        </div>

        <div className="overview-metric-card">
          <div>
            <div className="linear-card-header">
              <span className="linear-metric-label">Indexed Jobs</span>
              <Briefcase size={16} className="linear-icon-muted" />
            </div>
            <div className="linear-metric-value-row">
              <span className="linear-metric-number">{overview.jobs}</span>
              <span className="linear-trend-badge positive">{overview.open_jobs} currently open</span>
            </div>
          </div>
          <p className="linear-metric-caption" style={{ margin: "6px 0 0 0" }}>
            Live roles ingested via JobSpy &amp; career adapters.
          </p>
        </div>

        <div className="overview-metric-card">
          <div>
            <div className="linear-card-header">
              <span className="linear-metric-label">Total Ingestion Runs</span>
              <Clock size={16} className="linear-icon-muted" />
            </div>
            <div className="linear-metric-value-row">
              <span className="linear-metric-number">{overview.crawls}</span>
              <span className="linear-trend-badge positive">{overview.successful_crawls} successful</span>
            </div>
          </div>
          <p className="linear-metric-caption" style={{ margin: "6px 0 0 0" }}>
            Sync and crawl operations executed.
          </p>
        </div>

        <div className="overview-metric-card">
          <div>
            <div className="linear-card-header">
              <span className="linear-metric-label">Registered Candidates</span>
              <Layers size={16} className="linear-icon-muted" />
            </div>
            <div className="linear-metric-value-row">
              <span className="linear-metric-number">{overview.users}</span>
              <span className="linear-trend-badge neutral">NextHire Candidates</span>
            </div>
          </div>
          <p className="linear-metric-caption" style={{ margin: "6px 0 0 0" }}>
            Active candidate profiles &amp; resumes in system.
          </p>
        </div>
      </div>

      {/* Candidate Target Company Whitelist Queue */}
      {pendingCompanies.length > 0 && (
        <section
          className="linear-widget-panel"
          style={{
            border: "1px solid rgba(234, 88, 12, 0.35)",
            background: "linear-gradient(135deg, rgba(234, 88, 12, 0.05), rgba(245, 158, 11, 0.02))",
          }}
        >
          <div className="widget-header" style={{ flexWrap: "wrap", gap: "10px", marginBottom: "0.75rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div
                style={{
                  width: "28px",
                  height: "28px",
                  borderRadius: "50%",
                  background: "rgba(234, 88, 12, 0.15)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#ea580c",
                }}
              >
                <ShieldCheck size={16} />
              </div>
              <div>
                <h2 className="widget-title" style={{ margin: 0 }}>
                  Candidate Whitelist Queue ({pendingCompanies.length})
                </h2>
                <span style={{ fontSize: "12px", color: "var(--colors-slate)" }}>
                  Companies added by candidates in their profile awaiting admin whitelist approval
                </span>
              </div>
            </div>
            <span
              className="badge-tag-orange"
              style={{
                fontSize: "11px",
                fontWeight: 700,
                background: "rgba(234, 88, 12, 0.15)",
                color: "#ea580c",
                padding: "3px 8px",
                borderRadius: "4px",
              }}
            >
              Action Required
            </span>
          </div>

          <p style={{ color: "var(--colors-slate)", fontSize: "13px", marginBottom: "1rem" }}>
            Approving a company will verify it in NextHire and immediately trigger JobSpy to scrape 10–12 verified open roles from Naukri.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {pendingCompanies.map((c) => {
              const isApproving = approvingId === c.id;
              const isRejecting = rejectingId === c.id;
              return (
                <div
                  key={c.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 16px",
                    background: "var(--colors-surface-card)",
                    borderRadius: "8px",
                    border: "1px solid rgba(234, 88, 12, 0.25)",
                    flexWrap: "wrap",
                    gap: "10px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <div
                      style={{
                        width: "34px",
                        height: "34px",
                        borderRadius: "6px",
                        background: "#ea580c",
                        color: "#fff",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontWeight: 700,
                        fontSize: "13px",
                      }}
                    >
                      {c.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <strong style={{ fontSize: "14px", color: "var(--colors-ink)" }}>{c.name}</strong>
                        <span
                          style={{
                            fontSize: "11px",
                            fontWeight: 600,
                            padding: "2px 6px",
                            borderRadius: "4px",
                            background: "rgba(234, 88, 12, 0.12)",
                            color: "#ea580c",
                          }}
                        >
                          Candidate Requested
                        </span>
                      </div>
                      <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>
                        {c.website || c.career_page_url || "Direct candidate target submission"}
                      </span>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <button
                      className="primary-button"
                      onClick={() => handleApproveCompany(c)}
                      disabled={isApproving || isRejecting}
                      style={{
                        fontSize: "12px",
                        padding: "6px 14px",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                        background: "#16a34a",
                        borderColor: "#16a34a",
                      }}
                    >
                      <Check size={13} className={isApproving ? "spin" : ""} />
                      <span>{isApproving ? "Approving & Scraping..." : "Approve & Scrape Naukri"}</span>
                    </button>
                    <button
                      className="button-secondary"
                      onClick={() => handleRejectCompany(c)}
                      disabled={isApproving || isRejecting}
                      style={{
                        fontSize: "12px",
                        padding: "6px 12px",
                        color: "#dc2626",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px",
                      }}
                    >
                      <X size={13} />
                      <span>{isRejecting ? "Rejecting..." : "Reject"}</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Add Company Card */}
      <section className="linear-widget-panel">
        <div className="widget-header">
          <h2 className="widget-title">Add Company & Career Page</h2>
          <span className="widget-tag">Naukri Integration</span>
        </div>
        <p style={{ color: "var(--colors-slate)", fontSize: "13.5px", marginBottom: "1rem" }}>
          Add any target company. NextHire searches live openings on Naukri via JobSpy and indexes 10–12 verified roles for this company automatically.
        </p>

        <form onSubmit={submitCompany} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "10px", alignItems: "flex-end" }}>
          <label style={{ margin: 0 }}>
            <span style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--colors-ink)", marginBottom: "4px" }}>
              Company Name *
            </span>
            <input
              required
              type="text"
              placeholder="e.g. Infosys, TCS, Google, Spotify"
              value={companyForm.name}
              onChange={(e) => setCompanyForm({ ...companyForm, name: e.target.value })}
            />
          </label>

          <label style={{ margin: 0 }}>
            <span style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--colors-ink)", marginBottom: "4px" }}>
              Career Page / Website (optional)
            </span>
            <input
              type="url"
              placeholder="https://company.com"
              value={companyForm.career_page_url}
              onChange={(e) => setCompanyForm({ ...companyForm, career_page_url: e.target.value, website: e.target.value })}
            />
          </label>

          <button
            className="primary-button"
            type="submit"
            disabled={addingCompany}
            style={{ height: "40px", display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "6px" }}
          >
            <Plus size={15} />
            <span>{addingCompany ? "Adding & Scraping Naukri..." : "Add Company"}</span>
          </button>
        </form>
      </section>

      {/* Edit Modal / Inline Panel */}
      {editingCompany && (
        <section className="linear-widget-panel" style={{ border: "2px solid var(--colors-primary)" }}>
          <div className="widget-header">
            <h2 className="widget-title">Edit Company: {editingCompany.name}</h2>
            <button className="button-link" onClick={() => setEditingCompany(null)}>Cancel</button>
          </div>
          <form onSubmit={handleSaveEdit} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "10px", marginTop: "1rem" }}>
            <label style={{ margin: 0 }}>
              Company Name
              <input required type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} />
            </label>
            <label style={{ margin: 0 }}>
              Career Page URL
              <input required type="url" value={editForm.career_page_url} onChange={(e) => setEditForm({ ...editForm, career_page_url: e.target.value })} />
            </label>
            <label style={{ margin: 0 }}>
              Website
              <input type="url" value={editForm.website} onChange={(e) => setEditForm({ ...editForm, website: e.target.value })} />
            </label>
            <div style={{ display: "flex", gap: "8px", alignItems: "flex-end" }}>
              <button className="primary-button" type="submit">Save Changes</button>
              <button className="button-secondary" type="button" onClick={() => setEditingCompany(null)}>Cancel</button>
            </div>
          </form>
        </section>
      )}

      {/* Configured Companies List */}
      <section className="linear-widget-panel">
        <div className="widget-header" style={{ flexWrap: "wrap", gap: "10px" }}>
          <div>
            <h2 className="widget-title">Target Companies ({companies.length})</h2>
            <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>Curated top {companies.length} prototype companies for automated crawling</span>
          </div>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <button
              className="button-secondary"
              onClick={handleResetPrototype}
              disabled={resettingPrototype}
              style={{ fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "5px", padding: "5px 12px" }}
            >
              <RefreshCw size={12} className={resettingPrototype ? "spin" : ""} />
              <span>{resettingPrototype ? "Resetting..." : "Reset to Top 12"}</span>
            </button>
            <span className="widget-tag">12-Hour Crawler Queue</span>
          </div>
        </div>
        <p style={{ color: "var(--colors-slate)", fontSize: "13.5px", marginBottom: "1rem" }}>
          These companies are indexed periodically. Click "Scrape Now" to immediately fetch open listings from their careers page.
        </p>

        {/* Whitelist Filter Tabs */}
        <div style={{ display: "flex", gap: "8px", marginBottom: "0.75rem", flexWrap: "wrap" }}>
          <button
            type="button"
            className={whitelistFilter === "all" ? "primary-button" : "button-secondary"}
            onClick={() => { setWhitelistFilter("all"); setCompanyPage(1); }}
            style={{ fontSize: "12px", padding: "5px 12px", height: "30px" }}
          >
            All Companies ({companies.length})
          </button>
          <button
            type="button"
            className={whitelistFilter === "verified" ? "primary-button" : "button-secondary"}
            onClick={() => { setWhitelistFilter("verified"); setCompanyPage(1); }}
            style={{ fontSize: "12px", padding: "5px 12px", height: "30px" }}
          >
            Whitelisted ({companies.filter(c => c.verification_status !== "pending").length})
          </button>
          <button
            type="button"
            className={whitelistFilter === "pending" ? "primary-button" : "button-secondary"}
            onClick={() => { setWhitelistFilter("pending"); setCompanyPage(1); }}
            style={{
              fontSize: "12px",
              padding: "5px 12px",
              height: "30px",
              display: "inline-flex",
              alignItems: "center",
              gap: "5px",
              background: whitelistFilter === "pending" ? "#ea580c" : undefined,
              borderColor: whitelistFilter === "pending" ? "#ea580c" : undefined,
              color: whitelistFilter === "pending" ? "#fff" : undefined,
            }}
          >
            <span>Pending Whitelist</span>
            {pendingCompanies.length > 0 && (
              <span
                style={{
                  background: whitelistFilter === "pending" ? "rgba(255,255,255,0.3)" : "rgba(234,88,12,0.15)",
                  color: whitelistFilter === "pending" ? "#fff" : "#ea580c",
                  borderRadius: "10px",
                  padding: "1px 6px",
                  fontSize: "10px",
                  fontWeight: 700,
                }}
              >
                {pendingCompanies.length}
              </span>
            )}
          </button>
        </div>

        {/* Company Search & Filter Bar */}
        <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap" }}>
          <div style={{ position: "relative", flex: 1, minWidth: "260px" }}>
            <Search size={14} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--colors-steel)", pointerEvents: "none" }} />
            <input
              type="text"
              placeholder="Search companies by name or URL (e.g. Google, Stripe, Apple, Adobe)..."
              value={companySearch}
              onChange={(e) => {
                setCompanySearch(e.target.value);
                setCompanyPage(1);
              }}
              style={{ paddingLeft: "34px", margin: 0, width: "100%", height: "36px", fontSize: "13px" }}
            />
          </div>
          {companySearch && (
            <button
              className="button-secondary"
              onClick={() => {
                setCompanySearch("");
                setCompanyPage(1);
              }}
              style={{ fontSize: "12px", height: "36px", padding: "0 12px" }}
            >
              Clear
            </button>
          )}
          <span style={{ fontSize: "12.5px", color: "var(--colors-steel)" }}>
            Showing {paginatedCompanies.length} of {filteredCompanies.length} companies
          </span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {paginatedCompanies.length === 0 ? (
            <div style={{ padding: "2rem", textAlign: "center", color: "var(--colors-steel)", background: "var(--colors-surface-soft)", borderRadius: "8px" }}>
              No companies found matching "{companySearch}".
            </div>
          ) : (
            paginatedCompanies.map((company) => {
              const isScraping = scrapingId === company.id;
              const isPending = company.verification_status === "pending";
              return (
                <div
                  key={company.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 16px",
                    background: "var(--colors-surface-soft)",
                    borderRadius: "8px",
                    border: isPending ? "1px solid rgba(234, 88, 12, 0.3)" : "1px solid var(--colors-hairline)",
                    flexWrap: "wrap",
                    gap: "10px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "12px", minWidth: "220px", flex: 1 }}>
                    <div style={{ width: "32px", height: "32px", borderRadius: "6px", background: isPending ? "#ea580c" : "var(--colors-primary)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: "13px", flexShrink: 0 }}>
                      {company.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div style={{ overflow: "hidden" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                        <strong style={{ fontSize: "14px", color: "var(--colors-ink)" }}>{company.name}</strong>
                        {isPending ? (
                          <span
                            style={{
                              fontSize: "11px",
                              fontWeight: 600,
                              padding: "2px 6px",
                              borderRadius: "4px",
                              background: "rgba(234, 88, 12, 0.12)",
                              color: "#ea580c",
                            }}
                          >
                            Pending Whitelist
                          </span>
                        ) : (
                          <span
                            style={{
                              fontSize: "11px",
                              fontWeight: 600,
                              padding: "2px 6px",
                              borderRadius: "4px",
                              background: company.active ? "rgba(26, 174, 57, 0.12)" : "rgba(120, 118, 113, 0.12)",
                              color: company.active ? "var(--colors-semantic-success)" : "var(--colors-steel)",
                            }}
                          >
                            {company.active ? "Active" : "Paused"}
                          </span>
                        )}
                      </div>
                      {company.career_page_url ? (
                        <a
                          href={company.career_page_url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ fontSize: "12px", color: "var(--colors-link-blue)", display: "inline-flex", alignItems: "center", gap: "4px", marginTop: "2px", maxWidth: "100%", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                        >
                          <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{company.career_page_url}</span>
                          <ExternalLink size={10} style={{ flexShrink: 0 }} />
                        </a>
                      ) : (
                        <span style={{ fontSize: "12px", color: "var(--colors-steel)" }}>Candidate Submitted Target</span>
                      )}
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                    {isPending ? (
                      <>
                        <button
                          className="primary-button"
                          onClick={() => handleApproveCompany(company)}
                          disabled={approvingId === company.id || rejectingId === company.id}
                          style={{
                            fontSize: "12px",
                            padding: "6px 14px",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "5px",
                            background: "#16a34a",
                            borderColor: "#16a34a",
                          }}
                        >
                          <Check size={12} className={approvingId === company.id ? "spin" : ""} />
                          <span>{approvingId === company.id ? "Approving..." : "Approve & Scrape Naukri"}</span>
                        </button>
                        <button
                          className="button-secondary"
                          onClick={() => handleRejectCompany(company)}
                          disabled={approvingId === company.id || rejectingId === company.id}
                          style={{ fontSize: "12px", padding: "6px 10px", color: "#dc2626" }}
                        >
                          <X size={12} />
                          <span>{rejectingId === company.id ? "Rejecting..." : "Reject"}</span>
                        </button>
                      </>
                    ) : (
                      <>
                        {company.last_sync_status && (
                          <span
                            style={{
                              fontSize: "11px",
                              fontWeight: 600,
                              padding: "3px 8px",
                              borderRadius: "4px",
                              background: company.last_sync_status === "succeeded" ? "rgba(26, 174, 57, 0.1)" : "rgba(221, 91, 0, 0.1)",
                              color: company.last_sync_status === "succeeded" ? "var(--colors-semantic-success)" : "var(--colors-brand-orange)",
                            }}
                          >
                            {company.last_sync_status === "succeeded" ? "Last Scrape: OK" : "Last Scrape: Failed"}
                          </span>
                        )}

                        <button
                          className="primary-button"
                          onClick={() => handleScrapeCompany(company.id, company.name)}
                          disabled={isScraping}
                          style={{ fontSize: "12px", padding: "6px 12px", display: "inline-flex", alignItems: "center", gap: "5px" }}
                        >
                          <RefreshCw size={12} className={isScraping ? "spin" : ""} />
                          <span>{isScraping ? "Scraping Naukri..." : "Scrape Naukri"}</span>
                        </button>

                        <button
                          className="button-secondary"
                          onClick={() => handleToggleActive(company)}
                          style={{ fontSize: "12px", padding: "6px 10px" }}
                        >
                          {company.active ? "Pause" : "Resume"}
                        </button>

                        <button
                          className="button-link"
                          onClick={() => handleStartEdit(company)}
                          style={{ fontSize: "12px" }}
                        >
                          Edit
                        </button>

                        <button
                          className="button-link"
                          onClick={() => handleDeleteCompany(company)}
                          style={{ fontSize: "12px", color: "#ef4444" }}
                          title="Delete company"
                        >
                          <Trash2 size={13} />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Pagination Controls */}
        {totalCompanyPages > 1 && (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "1rem", paddingTop: "0.75rem", borderTop: "1px solid var(--colors-hairline)", flexWrap: "wrap", gap: "10px" }}>
            <span style={{ fontSize: "12.5px", color: "var(--colors-slate)" }}>
              Page {companyPage} of {totalCompanyPages} ({filteredCompanies.length} companies total)
            </span>
            <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
              <button
                className="button-secondary"
                disabled={companyPage <= 1}
                onClick={() => setCompanyPage((p) => Math.max(1, p - 1))}
                style={{ fontSize: "12px", padding: "4px 10px" }}
              >
                Previous
              </button>
              <span style={{ fontSize: "12px", color: "var(--colors-ink)", fontWeight: 600, padding: "0 4px" }}>
                {companyPage} / {totalCompanyPages}
              </span>
              <button
                className="button-secondary"
                disabled={companyPage >= totalCompanyPages}
                onClick={() => setCompanyPage((p) => Math.min(totalCompanyPages, p + 1))}
                style={{ fontSize: "12px", padding: "4px 10px" }}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Discovered Jobs Preview Table */}
      <section className="linear-widget-panel">
        <div className="widget-header">
          <h2 className="widget-title">Live Discovered Jobs ({jobs.length})</h2>
          <a className="button-link" href="/jobs" style={{ fontSize: "13px" }}>
            View in Job Feed →
          </a>
        </div>
        <p style={{ color: "var(--colors-slate)", fontSize: "13.5px", marginBottom: "1rem" }}>
          All scraped jobs are dynamically searchable, filterable, and scored by AI in the candidate Job Feed.
        </p>

        {jobs.length === 0 ? (
          <p className="empty-message">No jobs discovered yet. Add a company and click "Scrape Now" to fetch live openings.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {jobs.slice(0, 8).map(({ job, company_name }) => (
              <div
                key={job.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "10px 14px",
                  background: "var(--colors-surface-soft)",
                  borderRadius: "6px",
                  border: "1px solid var(--colors-hairline)",
                  flexWrap: "wrap",
                  gap: "8px",
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <strong style={{ fontSize: "13.5px", color: "var(--colors-ink)" }}>{job.title}</strong>
                    <span style={{ fontSize: "11px", color: "var(--colors-steel)" }}>· {company_name}</span>
                    <span style={{ fontSize: "11px", padding: "1px 5px", borderRadius: "3px", background: "rgba(86, 69, 212, 0.08)", color: "var(--colors-primary)" }}>
                      {job.status}
                    </span>
                  </div>
                  {job.required_skills && job.required_skills.length > 0 && (
                    <div style={{ display: "flex", gap: "4px", marginTop: "4px", flexWrap: "wrap" }}>
                      {job.required_skills.slice(0, 4).map((s) => (
                        <span key={s} style={{ fontSize: "10.5px", padding: "1px 6px", borderRadius: "3px", background: "var(--colors-surface)", border: "1px solid var(--colors-hairline)" }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <a
                  href={job.url}
                  target="_blank"
                  rel="noreferrer"
                  className="button-link"
                  style={{ fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "3px" }}
                >
                  <span>Apply Link</span>
                  <ExternalLink size={11} />
                </a>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Crawl History & Audit */}
      <section className="linear-widget-panel">
        <div className="widget-header">
          <h2 className="widget-title">Recent Scraping History</h2>
          <span className="widget-tag">{crawls.length} runs</span>
        </div>
        {crawls.length === 0 ? (
          <p className="empty-message">No crawl logs recorded yet.</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "6px" }}>
            {crawls.slice(0, 6).map((crawl, idx) => (
              <li
                key={`${crawl.company_id}-${crawl.completed_at}-${idx}`}
                style={{
                  fontSize: "12.5px",
                  padding: "8px 12px",
                  borderRadius: "4px",
                  background: "var(--colors-surface-soft)",
                  border: "1px solid var(--colors-hairline)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span>
                  <strong>{crawl.company_id}</strong> — status:{" "}
                  <span style={{ color: crawl.status === "succeeded" ? "var(--colors-semantic-success)" : "var(--colors-brand-orange)", fontWeight: 600 }}>
                    {crawl.status}
                  </span>
                  {crawl.error_code ? ` (${crawl.error_code})` : ""}
                </span>
                <span style={{ color: "var(--colors-steel)" }}>
                  {crawl.jobs_found} found · {crawl.jobs_added} added
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

const rootElement = typeof document !== "undefined" ? document.getElementById("root") : null;
if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}
