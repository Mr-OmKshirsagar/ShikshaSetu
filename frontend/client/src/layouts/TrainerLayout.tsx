import React, { useMemo } from "react";
import {
  BarChart2,
  BookOpen,
  CheckSquare,
  FileQuestion,
  LayoutDashboard,
  PenTool,
  UserRound,
  Sparkles,
} from "lucide-react";
import { useTranslation } from "@/i18n";
import { DashboardShell, DashboardNavItem, DashboardRoleTheme } from "./DashboardShell";

interface TrainerLayoutProps {
  children: React.ReactNode;
  activePage: string;
  onNavigate: (page: string) => void;
}

const TRAINER_ROLE_THEME: DashboardRoleTheme = {
  activeNavBg: "bg-[#fff2e8]",
  activeNavText: "text-[#c2510e]",
  activeIndicator: "bg-[#ef7e37]",
  hoverNavBg: "hover:bg-orange-50 hover:text-[#c2510e]",
  avatarBg: "bg-orange-100 text-[#c2510e]",
  badgeDotBg: "bg-amber-500",
  headerTitleColor: "text-[#123057]",
};

export function TrainerLayout({ children, activePage, onNavigate }: TrainerLayoutProps) {
  const { isHindi } = useTranslation();

  const navItems: DashboardNavItem[] = useMemo(
    () => [
      { id: "Dashboard", label: isHindi ? "डैशबोर्ड" : "Dashboard", icon: LayoutDashboard },
      { id: "Learning Materials", label: isHindi ? "प्रशिक्षण सामग्री" : "Learning Materials", icon: BookOpen },
      { id: "AI Question Generator", label: isHindi ? "एआई प्रश्न निर्माता" : "AI Question Generator", icon: FileQuestion },
      { id: "Question Review", label: isHindi ? "समीक्षा स्टूडियो" : "Question Review", icon: CheckSquare },
      { id: "Quiz Studio", label: isHindi ? "प्रश्नोत्तरी स्टूडियो" : "Quiz Studio", icon: PenTool },
      { id: "Learner Results", label: isHindi ? "प्रशिक्षु परिणाम" : "Learner Results", icon: BarChart2 },
      { id: "Trainer Talent Passport", label: isHindi ? "प्रशिक्षक टैलेंट पासपोर्ट" : "Trainer Talent Passport", icon: Sparkles },
      { id: "Profile", label: isHindi ? "प्रोफ़ाइल" : "Profile", icon: UserRound },
    ],
    [isHindi]
  );

  return (
    <DashboardShell
      activePage={activePage}
      onNavigate={onNavigate}
      navItems={navItems}
      workspaceTitle={isHindi ? "प्रशिक्षक कार्यक्षेत्र" : "Trainer workspace · Content Creator"}
      headerWorkspaceLabel={isHindi ? "प्रशिक्षक कार्यक्षेत्र" : "SHIKSHASETU WORKSPACE"}
      logoHref="/trainer"
      roleBadgeText="Lead Faculty"
      bgClassName="bg-[#fdf5ee]"
      roleTheme={TRAINER_ROLE_THEME}
    >
      {children}
    </DashboardShell>
  );
}

export default TrainerLayout;
