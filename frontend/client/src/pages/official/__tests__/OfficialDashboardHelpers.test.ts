import { describe, it, expect } from "vitest";
import { getCleanCompetencyName } from "../OfficialDashboard";

describe("OfficialDashboard Helpers - getCleanCompetencyName", () => {
  it("converts raw technical competency codes to clean human-readable titles", () => {
    expect(getCleanCompetencyName(null, "STAT_SAMPLING")).toBe("Sampling");
    expect(getCleanCompetencyName(null, "STAT_SURVEY_DESIGN")).toBe("Survey Design");
    expect(getCleanCompetencyName(null, "TECH_PYTHON")).toBe("Python");
    expect(getCleanCompetencyName(null, "BEH_ETHICS")).toBe("Ethics");
    expect(getCleanCompetencyName(null, "BEH_LEADERSHIP")).toBe("Leadership");
    expect(getCleanCompetencyName(null, "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE")).toBe("Digital Public Infrastructure");
  });

  it("prefers human-readable names when available without underscores", () => {
    expect(getCleanCompetencyName("Sampling Techniques", "STAT_SAMPLING")).toBe("Sampling Techniques");
    expect(getCleanCompetencyName("Ethics and Integrity in Public Service", "BEH_ETHICS")).toBe("Ethics and Integrity in Public Service");
  });

  it("provides safe fallback when both name and code are empty", () => {
    expect(getCleanCompetencyName(null, null)).toBe("General Capability");
    expect(getCleanCompetencyName("", "")).toBe("General Capability");
  });
});
