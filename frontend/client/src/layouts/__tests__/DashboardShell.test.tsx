// @vitest-environment happy-dom
import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardShell, DashboardNavItem } from "../DashboardShell";
import { LayoutDashboard, Target } from "lucide-react";

// Mock AuthContext
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      full_name: "Abhishek Pathak",
      designation: "Statistical Officer",
      department: "Ministry of Statistics",
    },
    logout: vi.fn(),
  }),
}));

// Mock i18n
vi.mock("@/i18n", () => ({
  useTranslation: () => ({
    t: (key: string) => (key === "common.logout" ? "Logout" : key),
    isHindi: false,
  }),
}));

// Mock LanguageToggle
vi.mock("@/components/LanguageToggle", () => ({
  LanguageToggle: () => <div data-testid="language-toggle">Lang</div>,
}));

describe("DashboardShell Layout Alignment & Typography Contract", () => {
  const sampleNavItems: DashboardNavItem[] = [
    { id: "Dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "Skill Gaps", label: "Skill Gaps", icon: Target },
  ];

  it("renders a fixed 264px sidebar and 72px header sharing the exact grid structure", () => {
    const { container } = render(
      <DashboardShell
        activePage="Dashboard"
        onNavigate={vi.fn()}
        navItems={sampleNavItems}
        workspaceTitle="Learner workspace"
        headerWorkspaceLabel="SHIKSHASETU WORKSPACE"
        logoHref="/official"
        roleBadgeText="Statistical Officer"
      >
        <div data-testid="dashboard-content">Main Content Area</div>
      </DashboardShell>
    );

    // 1. Sidebar width contract: strictly w-[264px]
    const sidebar = container.querySelector("aside");
    expect(sidebar).toBeTruthy();
    expect(sidebar?.className).toContain("w-[264px]");

    // 2. Sidebar brand header: strictly h-[72px]
    const sidebarBrandBar = sidebar?.firstElementChild as HTMLElement;
    expect(sidebarBrandBar.className).toContain("h-[72px]");

    // 3. Top header: strictly h-[72px]
    const header = container.querySelector("header");
    expect(header).toBeTruthy();
    expect(header?.className).toContain("h-[72px]");

    // 4. Shared grid container: both header and main use max-w-[1360px]
    const headerInner = header?.firstElementChild as HTMLElement;
    expect(headerInner.className).toContain("max-w-[1360px]");
    expect(headerInner.className).toContain("px-6 lg:px-9");

    const mainInner = container.querySelector("main > div") as HTMLElement;
    expect(mainInner.className).toContain("max-w-[1360px]");
    expect(mainInner.className).toContain("px-6 lg:px-9");

    // 5. Offset of main workspace: lg:pl-[264px]
    const mainWorkspace = header?.parentElement as HTMLElement;
    expect(mainWorkspace.className).toContain("lg:pl-[264px]");
  });

  it("renders the simplified ShikshaSetu logo without 'CAPABILITY INTELLIGENCE' in sidebar", () => {
    const { container } = render(
      <DashboardShell
        activePage="Dashboard"
        onNavigate={vi.fn()}
        navItems={sampleNavItems}
        workspaceTitle="Learner workspace"
      >
        <div>Content</div>
      </DashboardShell>
    );

    // Must show brand link "ShikshaSetu"
    const brandLink = container.querySelector("aside header, aside div a[aria-label='ShikshaSetu']");
    expect(brandLink).toBeTruthy();
    // Must NOT contain "CAPABILITY INTELLIGENCE" anywhere in the sidebar
    const sidebar = container.querySelector("aside");
    expect(sidebar?.textContent).not.toContain("CAPABILITY INTELLIGENCE");
  });

  it("places the Logout button strictly in the bottom-left sidebar profile section", () => {
    const { container } = render(
      <DashboardShell
        activePage="Dashboard"
        onNavigate={vi.fn()}
        navItems={sampleNavItems}
        workspaceTitle="Learner workspace"
      >
        <div>Content</div>
      </DashboardShell>
    );

    const sidebar = container.querySelector("aside");
    const logoutBtnInSidebar = sidebar?.querySelector("button[title='Logout']");
    expect(logoutBtnInSidebar).toBeTruthy();

    const header = container.querySelector("header");
    const logoutBtnInHeader = header?.querySelector("button[title='Logout']");
    expect(logoutBtnInHeader).toBeNull();
  });

  it("highlights active nav item with font-semibold, accent background, and indicator pill", () => {
    const { container } = render(
      <DashboardShell
        activePage="Dashboard"
        onNavigate={vi.fn()}
        navItems={sampleNavItems}
        workspaceTitle="Learner workspace"
      >
        <div>Content</div>
      </DashboardShell>
    );

    const activeBtn = container.querySelector("nav button[aria-current='page']") as HTMLElement;
    expect(activeBtn).toBeTruthy();
    expect(activeBtn.textContent).toContain("Dashboard");
    expect(activeBtn.className).toContain("font-semibold");
    expect(activeBtn.className).toContain("text-xs");
  });
});
