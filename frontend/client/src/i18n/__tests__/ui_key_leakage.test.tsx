// @vitest-environment happy-dom
import React from "react";
import { describe, it, expect, afterEach } from "vitest";
import { render, cleanup } from "@testing-library/react";
import { LanguageProvider } from "../provider";
import { useTranslation } from "../useTranslation";
import { hi } from "../hi";

afterEach(() => {
  cleanup();
});

function TestComponent({ i18nKey }: { i18nKey: string }) {
  const { t } = useTranslation();
  return <div data-testid="test-val">{t(i18nKey)}</div>;
}

describe("UI Localization Key Leakage Prevention", () => {
  it("renders human-readable text for skillGaps and quizzes keys in English", () => {
    const r1 = render(
      <LanguageProvider>
        <TestComponent i18nKey="skillGaps.intelligenceTitle" />
      </LanguageProvider>
    );
    expect(r1.getByTestId("test-val").textContent).toBe("Skill Gap Intelligence");
    cleanup();

    const r2 = render(
      <LanguageProvider>
        <TestComponent i18nKey="skillGaps.roleRequirements" />
      </LanguageProvider>
    );
    expect(r2.getByTestId("test-val").textContent).toBe("Role Requirements");
    cleanup();

    const r3 = render(
      <LanguageProvider>
        <TestComponent i18nKey="quizzes.assigned" />
      </LanguageProvider>
    );
    expect(r3.getByTestId("test-val").textContent).toBe("Assigned Quizzes");
  });

  it("never leaks raw dot-notation keys for unknown or missing keys", () => {
    const r1 = render(
      <LanguageProvider>
        <TestComponent i18nKey="analytics.quarterlyGrowthOverview" />
      </LanguageProvider>
    );
    const text1 = r1.getByTestId("test-val").textContent;
    expect(text1).not.toContain(".");
    expect(text1).toBe("Quarterly Growth Overview");
    cleanup();

    const r2 = render(
      <LanguageProvider>
        <TestComponent i18nKey="customNamespace.userProfileCard" />
      </LanguageProvider>
    );
    const text2 = r2.getByTestId("test-val").textContent;
    expect(text2).not.toContain(".");
    expect(text2).toBe("User Profile Card");
  });

  it("has authentic Hindi translations for all critical UI keys without raw leakage", () => {
    expect(hi.skillGaps.intelligenceTitle).not.toContain("skillGaps.");
    expect(hi.skillGaps.roleRequirements).not.toContain("skillGaps.");
    expect(hi.quizzes.assigned).not.toContain("quizzes.");
  });
});
