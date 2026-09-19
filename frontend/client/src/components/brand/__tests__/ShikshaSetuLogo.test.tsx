// @vitest-environment happy-dom
import React from "react";
import { describe, it, expect, afterEach } from "vitest";
import { render, cleanup } from "@testing-library/react";
import { ShikshaSetuLogo } from "../ShikshaSetuLogo";

describe("ShikshaSetuLogo Component", () => {
  afterEach(() => {
    cleanup();
  });

  it("renders the full logo variant with alt='ShikshaSetu' by default", () => {
    const { getByRole } = render(<ShikshaSetuLogo />);
    const img = getByRole("img");
    expect(img).toBeDefined();
    expect(img.getAttribute("alt")).toBe("ShikshaSetu");
    expect(img.getAttribute("src")).toBe("/assets/shikshasetu-logo.png");
    expect(img.className).toContain("object-contain");
  });

  it("renders the icon variant with the symbol asset", () => {
    const { getByRole } = render(<ShikshaSetuLogo variant="icon" size="md" />);
    const img = getByRole("img");
    expect(img).toBeDefined();
    expect(img.getAttribute("alt")).toBe("ShikshaSetu");
    expect(img.getAttribute("src")).toBe("/assets/shikshasetu-icon.png");
    expect(img.className).toContain("object-contain");
  });

  it("renders the compact variant with symbol and typography", () => {
    const { getByRole, getByText } = render(
      <ShikshaSetuLogo variant="compact" subtitle="Capability Intelligence" />
    );
    const img = getByRole("img");
    expect(img.getAttribute("src")).toBe("/assets/shikshasetu-icon.png");
    expect(getByText("ShikshaSetu")).toBeDefined();
    expect(getByText("Capability Intelligence")).toBeDefined();
  });

  it("renders an accessible navigation link when href is provided", () => {
    const { getByRole } = render(<ShikshaSetuLogo variant="full" href="/official" />);
    const link = getByRole("link");
    expect(link).toBeDefined();
    expect(link.getAttribute("href")).toBe("/official");
    expect(link.getAttribute("aria-label")).toBe("ShikshaSetu");
  });

  it("does not duplicate wordmark outside image when variant='full'", () => {
    const { container } = render(<ShikshaSetuLogo variant="full" />);
    const textNodes = container.querySelectorAll("span, p, div.text-base");
    expect(textNodes.length).toBe(0);
  });
});
