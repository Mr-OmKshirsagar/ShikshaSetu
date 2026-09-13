import { describe, it, expect } from "vitest";
import {
  getRecommendationTitle,
  getRecommendationProvider,
} from "../OfficialDashboard";
import type { Recommendation } from "@/lib/api";

describe("Official Dashboard Next Best Action - Resource Display Regression Tests", () => {
  it("extracts human-readable title when resource is a nested object from backend API", () => {
    // Exactly matches backend LearningRecommendation schema from GET /recommendations/me
    const backendRec = {
      rank: 1,
      resource: {
        resource_id: "NSSTA-NSSTA-PROT-033",
        provider: "NSSTA",
        resource_type: "TRAINING_PROGRAMME",
        title: "Data Ethics, Governance, and Quality in a Changing Data Ecosystem",
        metadata: {
          duration_hours: 40.0,
          difficulty: null,
          target_roles: [],
          prerequisites: [],
        },
        competencies: ["DIGOV_DATA_PRIVACY", "STAT_DATA_QUALITY_FRAMEWORKS"],
        status: "ACTIVE",
      },
      provider: "NSSTA",
      competency_code: "STAT_DATA_QUALITY_FRAMEWORKS",
      competency_name: "Data Quality Frameworks",
      current_level: null,
      required_level: 4.0,
      gap: 4.0,
      score: 0.635,
    } as unknown as Recommendation;

    const title = getRecommendationTitle(backendRec);
    const provider = getRecommendationProvider(backendRec);

    expect(title).toBe("Data Ethics, Governance, and Quality in a Changing Data Ecosystem");
    expect(title).not.toBe("[object Object]");
    expect(provider).toBe("NSSTA");

    // Test the interpolated message rendered in the Next Best Action card
    const cardText = `Recommended curriculum: "${title}" from ${provider}. Matched to your role responsibilities.`;
    expect(cardText).toContain('"Data Ethics, Governance, and Quality in a Changing Data Ecosystem"');
    expect(cardText).not.toContain("[object Object]");
  });

  it("extracts human-readable title when resource is an iGOT course object", () => {
    const igotRec = {
      rank: 1,
      resource: {
        resource_id: "IGOT-do_113981544641339392163",
        provider: "IGOT",
        resource_type: "COURSE",
        title: "Design Thinking for Excellence in Public Services",
      },
      provider: "IGOT",
      competency_code: "TECH_DATA_VISUALIZATION",
      competency_name: "Data Visualization",
    } as unknown as Recommendation;

    const title = getRecommendationTitle(igotRec);
    expect(title).toBe("Design Thinking for Excellence in Public Services");
    expect(title).not.toBe("[object Object]");
  });

  it("falls back gracefully when resource is an empty object without title", () => {
    const emptyObjectRec = {
      resource: {},
      provider: "iGOT",
    } as unknown as Recommendation;

    const title = getRecommendationTitle(emptyObjectRec);
    expect(title).toBe("Targeted Capability Course");
    expect(title).not.toBe("[object Object]");
  });

  it("handles alternative property names like resource_title and title", () => {
    const recWithResourceTitle = {
      resource_title: "Statistical Sampling Foundations",
      provider: "NSSTA",
    } as unknown as Recommendation;

    expect(getRecommendationTitle(recWithResourceTitle)).toBe("Statistical Sampling Foundations");

    const recWithDirectTitle = {
      title: "Public Finance and Budgeting",
      provider: "iGOT",
    } as unknown as Recommendation;

    expect(getRecommendationTitle(recWithDirectTitle)).toBe("Public Finance and Budgeting");
  });

  it("handles null or undefined recommendation safely", () => {
    expect(getRecommendationTitle(null)).toBe("");
    expect(getRecommendationTitle(undefined)).toBe("");
    expect(getRecommendationProvider(null)).toBe("iGOT");
    expect(getRecommendationProvider(undefined)).toBe("iGOT");
  });
});
