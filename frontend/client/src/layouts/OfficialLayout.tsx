import React from "react";
import {
  Award,
  BookOpen,
  ClipboardCheck,
  FileText,
  Gauge,
  LayoutDashboard,
  Star,
  Target,
  TrendingUp,
  UserRound,
  Sparkles,
} from "lucide-react";
import { useTranslation } from "@/i18n";
import { CapabilityAssistant } from "@/components/assistant/CapabilityAssistant";
import { DashboardShell, DashboardNavItem } from "./DashboardShell";

interface OfficialLayoutProps {
  children: React.ReactNode;
  activePage: string;
  onNavigate: (page: string) => void;
}

export function OfficialLayout({ children, activePage, onNavigate }: OfficialLayoutProps) {
  const { t, isHindi } = useTranslation();

  const navItems: DashboardNavItem[] = [
    { id: "Dashboard",        label: t("nav.dashboard"),       icon: LayoutDashboard },
    { id: "My Competencies",  label: t("nav.competencies"),    icon: Gauge },
    { id: "Assessments",      label: t("nav.assessments"),     icon: ClipboardCheck },
    { id: "Skill Gaps",       label: t("nav.skillGaps"),       icon: Target },
    { id: "Recommendations",  label: t("nav.recommendations"), icon: BookOpen },
    { id: "My Learning",      label: t("nav.learning"),        icon: Star },
    { id: "Quizzes",          label: t("nav.quizzes"),         icon: Award },
    { id: "Evidence",         label: t("nav.evidence"),        icon: FileText },
    { id: "Progress",         label: t("nav.progress"),        icon: TrendingUp },
    { id: "Talent Passport",  label: t("nav.talentPassport"),  icon: Sparkles },
    { id: "Profile",          label: t("nav.profile"),         icon: UserRound },
  ];

  return (
    <DashboardShell
      activePage={activePage}
      onNavigate={onNavigate}
      navItems={navItems}
      workspaceTitle={isHindi ? "शिक्षार्थी कार्यक्षेत्र" : "Learner workspace"}
      headerWorkspaceLabel={isHindi ? "शिक्षासेतु कार्यक्षेत्र" : "SHIKSHASETU WORKSPACE"}
      logoHref="/official"
      roleBadgeText="Statistical Officer"
      headerActions={
        <CapabilityAssistant
          currentPage={activePage}
          onNavigate={onNavigate}
          headerMode
        />
      }
      roleTheme={{
        activeNavBg: "bg-[#e8f5f3]",
        activeNavText: "text-[#087f76]",
        activeIndicator: "bg-[#087f76]",
        hoverNavBg: "hover:bg-teal-50/50 hover:text-[#087f76]",
        avatarBg: "bg-teal-100 text-[#087f76]",
        badgeDotBg: "bg-emerald-500",
        headerTitleColor: "text-[#123057]",
      }}
    >
      {children}
    </DashboardShell>
  );
}

export default OfficialLayout;
