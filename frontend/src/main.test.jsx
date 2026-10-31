import { describe, expect, it } from "vitest";
import {
  getJobSkillsAndScore,
  getRoleDomain,
  getCandidateDomain,
  matchesSkill,
  flattenCandidateSkills,
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
});
