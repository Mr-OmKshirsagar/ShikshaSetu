import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";
import {
  CENTRAL_MINISTRIES,
  STATES_AND_UTS,
  STATE_DEPARTMENT_TEMPLATES,
  DESIGNATION_CATALOGUE,
  getOrganizationsForLevelAndState,
  searchDesignations,
  searchOrganizations,
} from "@/lib/governmentTaxonomy";

describe("Government Organization & Designation Taxonomy", () => {
  it("covers at least 50 Central Ministries grounded in official rules", () => {
    expect(CENTRAL_MINISTRIES.length).toBeGreaterThanOrEqual(50);

    const names = CENTRAL_MINISTRIES.map((m) => m.name.toLowerCase());
    const ids = CENTRAL_MINISTRIES.map((m) => m.id);

    expect(ids).toContain("GOI-MOSPI");
    expect(ids).toContain("GOI-MOE");
    expect(ids).toContain("GOI-MEITY");
    expect(ids).toContain("GOI-MOF");
    expect(ids).toContain("GOI-DOPT");

    // Spot check key ministry domains
    expect(names.some((n) => n.includes("agriculture"))).toBe(true);
    expect(names.some((n) => n.includes("education"))).toBe(true);
    expect(names.some((n) => n.includes("statistics"))).toBe(true);
    expect(names.some((n) => n.includes("finance"))).toBe(true);
    expect(names.some((n) => n.includes("health"))).toBe(true);
    expect(names.some((n) => n.includes("rural development"))).toBe(true);
  });

  it("covers all 28 States and 8 Union Territories", () => {
    const states = STATES_AND_UTS.filter((s) => s.type === "STATE");
    const uts = STATES_AND_UTS.filter((s) => s.type === "UT");

    expect(states.length).toBe(28);
    expect(uts.length).toBe(8);

    const stateCodes = states.map((s) => s.code);
    expect(stateCodes).toContain("MH"); // Maharashtra
    expect(stateCodes).toContain("UP"); // Uttar Pradesh
    expect(stateCodes).toContain("TN"); // Tamil Nadu
    expect(stateCodes).toContain("KA"); // Karnataka
    expect(stateCodes).toContain("GJ"); // Gujarat

    const utCodes = uts.map((u) => u.code);
    expect(utCodes).toContain("DL"); // Delhi
    expect(utCodes).toContain("JK"); // Jammu and Kashmir
    expect(utCodes).toContain("LA"); // Ladakh
  });

  it("generates field administration offices for State Governments including Talathi and Tehsil", () => {
    const mhOrgs = getOrganizationsForLevelAndState("STATE", "MH");
    expect(mhOrgs.length).toBeGreaterThan(20);

    const names = mhOrgs.map((o) => o.name.toLowerCase());
    const types = mhOrgs.map((o) => o.organization_type);

    // Verify Tehsil / Taluka office
    expect(names.some((n) => n.includes("tehsil") || n.includes("taluka"))).toBe(true);
    expect(types).toContain("TEHSIL");

    // Verify Talathi office
    expect(names.some((n) => n.includes("talathi"))).toBe(true);

    // Verify Collectorate & BDO & Gram Panchayat
    expect(types).toContain("DISTRICT_ADMINISTRATION");
    expect(types).toContain("BLOCK");
    expect(types).toContain("GRAM_PANCHAYAT");
  });

  it("supports fuzzy search across designations", () => {
    // 1. Search 'talathi'
    const talathiResults = searchDesignations("talathi");
    expect(talathiResults.length).toBeGreaterThan(0);
    expect(talathiResults[0].title).toBe("Talathi");
    expect(talathiResults[0].domain).toBe("Revenue / Land Administration");

    // 2. Search 'stat'
    const statResults = searchDesignations("stat");
    expect(statResults.length).toBeGreaterThanOrEqual(3);
    const statTitles = statResults.map((s) => s.title);
    expect(statTitles).toContain("Statistical Officer");
    expect(statTitles).toContain("Senior Statistical Officer (SSO)");

    // 3. Search 'education'
    const eduResults = searchDesignations("education");
    expect(eduResults.length).toBeGreaterThan(0);
    const eduTitles = eduResults.map((e) => e.title);
    expect(eduTitles.some((t) => t.includes("Education"))).toBe(true);
  });

  it("supports fuzzy search across organizations", () => {
    const centralOrgs = CENTRAL_MINISTRIES;

    const mospiMatches = searchOrganizations(centralOrgs, "mospi");
    expect(mospiMatches.length).toBeGreaterThan(0);
    expect(mospiMatches[0].id).toBe("GOI-MOSPI");

    const eduMatches = searchOrganizations(centralOrgs, "education");
    expect(eduMatches.length).toBeGreaterThan(0);
    expect(eduMatches[0].id).toBe("GOI-MOE");
  });

  it("includes '+ Other' option in designation catalogue", () => {
    const other = DESIGNATION_CATALOGUE.find((d) => d.id === "DESIG-OTHER");
    expect(other).toBeDefined();
    expect(other?.title).toContain("Other");
  });

  it("verifies LoginPage source code has integrated GovernmentTaxonomySelector and preserved Quick Demo Access", () => {
    const loginPath = path.resolve(__dirname, "../LoginPage.tsx");
    const loginSrc = fs.readFileSync(loginPath, "utf-8");

    // Has GovernmentTaxonomySelector component
    expect(loginSrc).toContain("<GovernmentTaxonomySelector");

    // Preserves Quick Demo Access and SIH 2026 header
    expect(loginSrc).toContain("QUICK DEMO ACCESS · SIH 2026");
    expect(loginSrc).toContain("Statistical Officer");
    expect(loginSrc).toContain("NSSTA Trainer");
    expect(loginSrc).toContain("MoSPI Admin");
    expect(loginSrc).toContain("Education Officer");
    expect(loginSrc).toContain('login("official@shikshasetu.gov.in", "Password123!")');
  });

  it("verifies OfficialProfile source code has integrated GovernmentTaxonomySelector", () => {
    const profilePath = path.resolve(__dirname, "../official/OfficialProfile.tsx");
    const profileSrc = fs.readFileSync(profilePath, "utf-8");

    expect(profileSrc).toContain("<GovernmentTaxonomySelector");
    expect(profileSrc).toContain("Employment Details & Government Taxonomy");
    expect(profileSrc).toContain("organization_id");
    expect(profileSrc).toContain("government_level");
  });
});
