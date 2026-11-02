import { describe, expect, it } from "vitest";
import {
  getJobSkillsAndScore,
  getRoleDomain,
  getCandidateDomain,
  matchesSkill,
  flattenCandidateSkills,
  deduplicateJobsList,
} from "./main";

describe("Job Matching Algorithm & Domain Safety", () => {
  const candidateSkills = [
    "Languages: C/C++",
    "Python",
    "SQL",
    "JavaScript",
    "HTML/CSS",
    "Web & AI Engineering:MERN Stack",
    "FastAPI",
  ];

  it("returns 0% match score when new user has no skills configured", () => {
    const job = {
      title: "Full Stack Software Engineer",
      required_skills: ["Python", "React", "JavaScript"],
      preferred_skills: ["Docker"],
    };
    const res = getJobSkillsAndScore(job, [], "");
    expect(res.score).toBe(0);
    expect(res.matched).toEqual([]);
    expect(res.missing).toEqual(["Python", "React", "JavaScript"]);
  });

  it("strictly deduplicates jobs by ID, URL, and company::title", () => {
    const rawJobs = [
      { id: "j1", title: "Software Engineer", company_id: "google", url: "https://google.com/jobs/1" },
      { id: "j2", title: "Software Engineer", company_id: "google", url: "https://google.com/jobs/1/" }, // dupe URL
      { id: "j3", title: "Software Engineer", company_id: "google", url: "https://google.com/jobs/diff" }, // dupe company::title
      { id: "j1", title: "Different Title", company_id: "apple", url: "https://apple.com/jobs/2" }, // dupe ID
      { id: "j4", title: "Frontend Developer", company_id: "stripe", url: "https://stripe.com/jobs/4" },
    ];
    const deduped = deduplicateJobsList(rawJobs);
    expect(deduped).toHaveLength(2);
    expect(deduped[0].id).toBe("j1");
    expect(deduped[1].id).toBe("j4");
  });

  it("does not match short tokens inside other words like 'FastAPI' matching 'AI'", () => {
    expect(matchesSkill("AI", ["FastAPI"])).toBe(false);
    expect(matchesSkill("AI", ["Email Processing"])).toBe(false);
    expect(matchesSkill("AI", ["Artificial Intelligence"])).toBe(true);
  });

  it("flattens compound candidate skills correctly", () => {
    const flattened = flattenCandidateSkills(candidateSkills);
    expect(flattened).toContain("c++");
    expect(flattened).toContain("c");
    expect(flattened).toContain("python");
    expect(flattened).toContain("sql");
    expect(flattened).toContain("react");
    expect(flattened).toContain("fastapi");
  });

  it("detects role and candidate domains accurately", () => {
    expect(getRoleDomain("AEO and GEO Marketing Manager")).toBe("marketing");
    expect(getRoleDomain("AR Analyst")).toBe("finance");
    expect(getRoleDomain("Abuse Investigator")).toBe("operations");
    expect(getRoleDomain("AI Engineer")).toBe("engineering");
    expect(getRoleDomain("Senior Software Engineer")).toBe("engineering");

    expect(getCandidateDomain(candidateSkills, "Full Stack Engineer")).toBe("engineering");
  });

  it("penalizes cross-domain roles and prevents 100% inflation for marketing roles", () => {
    // Marketing role with realistic marketing skills
    const marketingJob = {
      title: "AEO and GEO Marketing Manager",
      required_skills: ["Digital Marketing", "SEO & AEO", "Content Strategy"],
      preferred_skills: ["Growth Analytics"],
    };
    const res1 = getJobSkillsAndScore(marketingJob, candidateSkills, "Full Stack Engineer");
    expect(res1.score).toBeLessThanOrEqual(20);

    // Marketing role even if crawler incorrectly tagged it with 'AI'
    const marketingJobWithAI = {
      title: "AEO and GEO Marketing Manager",
      required_skills: ["AI"],
      preferred_skills: [],
    };
    const res2 = getJobSkillsAndScore(marketingJobWithAI, candidateSkills, "Full Stack Engineer");
    expect(res2.score).toBeLessThanOrEqual(20);
    expect(res2.score).not.toBe(100);
  });

  it("awards high match scores to genuine software and AI engineering roles", () => {
    const aiJob = {
      title: "AI Engineer",
      required_skills: ["Python", "FastAPI"],
      preferred_skills: ["Machine Learning"],
    };
    const resAi = getJobSkillsAndScore(aiJob, candidateSkills, "Full Stack Engineer");
    expect(resAi.score).toBeGreaterThanOrEqual(70);

    const swJob = {
      title: "Senior Software Engineer",
      required_skills: ["Python", "SQL", "FastAPI"],
      preferred_skills: ["React"],
    };
    const resSw = getJobSkillsAndScore(swJob, candidateSkills, "Full Stack Engineer");
    expect(resSw.score).toBeGreaterThanOrEqual(85);
  });

  it("sorts jobs descending by highest match score with matched skills tie-breaker", () => {
    const jobLow = {
      id: "j-low",
      title: "Marketing Specialist",
      required_skills: ["SEO", "Content Marketing"],
      preferred_skills: [],
    };
    const jobMid = {
      id: "j-mid",
      title: "Junior Backend Developer",
      required_skills: ["Python", "Docker"],
      preferred_skills: [],
    };
    const jobHigh = {
      id: "j-high",
      title: "Senior Full Stack Engineer",
      required_skills: ["Python", "SQL", "FastAPI"],
      preferred_skills: ["React"],
    };

    const jobs = [jobLow, jobHigh, jobMid];
    const scoredJobs = jobs
      .map((job) => {
        const info = getJobSkillsAndScore(job, candidateSkills, "Full Stack Engineer");
        return { ...job, score: info.score, matched: info.matched };
      })
      .sort((a, b) => {
        if (b.score !== a.score) return b.score - a.score;
        return (b.matched?.length || 0) - (a.matched?.length || 0);
      });

    expect(scoredJobs[0].id).toBe("j-high");
    expect(scoredJobs[1].id).toBe("j-mid");
    expect(scoredJobs[2].id).toBe("j-low");
    expect(scoredJobs[0].score).toBeGreaterThan(scoredJobs[1].score);
    expect(scoredJobs[1].score).toBeGreaterThan(scoredJobs[2].score);
  });
});
