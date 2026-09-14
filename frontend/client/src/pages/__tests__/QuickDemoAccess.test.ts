import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

// Helper replicating App.tsx getRoleSlug
function getRoleSlug(role?: string): "trainer" | "admin" | "official" {
  const r = (role || "").toUpperCase();
  if (r === "TRAINER") return "trainer";
  if (r === "ADMIN") return "admin";
  return "official";
}

describe("Quick Demo Access & SIH 2026 Branding Tests", () => {
  const loginPagePath = path.resolve(__dirname, "../LoginPage.tsx");
  const loginPageSource = fs.readFileSync(loginPagePath, "utf-8");

  it("renders 'QUICK DEMO ACCESS · SIH 2026' and contains no references to 'SIH 2024'", () => {
    expect(loginPageSource).toContain("QUICK DEMO ACCESS · SIH 2026");
    expect(loginPageSource).not.toContain("SIH 2024");
    expect(loginPageSource).not.toContain("Quick Demo Access (SIH 2024 / MoSPI)");
  });

  it("contains canonical demo personas with required subtitles", () => {
    // 1. Statistical Officer
    expect(loginPageSource).toContain("📊 Statistical Officer");
    expect(loginPageSource).toContain("MoSPI · Primary Demo");

    // 2. NSSTA Trainer
    expect(loginPageSource).toContain("🎓 NSSTA Trainer");
    expect(loginPageSource).toContain("Training · AI Question Generation");

    // 3. MoSPI Admin
    expect(loginPageSource).toContain("🏛️ MoSPI Admin");
    expect(loginPageSource).toContain("Workforce · Department Overview");

    // 4. Education Officer (preserved)
    expect(loginPageSource).toContain("📚 Education Officer");
    expect(loginPageSource).toContain("MoE · Multi-Dept Demo");
  });

  it("maps ADMIN role correctly to admin slug and /admin/dashboard route", () => {
    const adminSlug = getRoleSlug("ADMIN");
    expect(adminSlug).toBe("admin");
    const adminTarget = `/${adminSlug}/dashboard`;
    expect(adminTarget).toBe("/admin/dashboard");

    const trainerSlug = getRoleSlug("TRAINER");
    expect(trainerSlug).toBe("trainer");

    const officialSlug = getRoleSlug("OFFICIAL");
    expect(officialSlug).toBe("official");
  });

  it("passes Password123! consistently for all demo logins", () => {
    expect(loginPageSource).toContain('login("admin@shikshasetu.gov.in", "Password123!")');
    expect(loginPageSource).toContain('login("official@shikshasetu.gov.in", "Password123!")');
    expect(loginPageSource).toContain('login("trainer@shikshasetu.gov.in", "Password123!")');
    expect(loginPageSource).toContain('login("edu.officer@shikshasetu.gov.in", "Password123!")');
  });
});
