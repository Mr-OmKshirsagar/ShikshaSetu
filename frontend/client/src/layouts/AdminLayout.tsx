import React from "react";
import {
  BarChart2,
  Brain,
  Building2,
  CalendarRange,
  FileBarChart,
  LayoutDashboard,
  TrendingUp,
  Users,
  UserRound,
  Zap,
} from "lucide-react";
import { useTranslation } from "@/i18n";
import { DashboardShell, DashboardNavItem } from "./DashboardShell";

interface AdminLayoutProps {
  children: React.ReactNode;
  activePage: string;
  onNavigate: (page: string) => void;
}

export function AdminLayout({ children, activePage, onNavigate }: AdminLayoutProps) {
  const { isHindi } = useTranslation();

  const navItems: DashboardNavItem[] = [
    { id: "Dashboard", label: isHindi ? "डैशबोर्ड" : "Dashboard", icon: LayoutDashboard },
    { id: "Workforce Overview", label: isHindi ? "कार्यबल अवलोकन" : "Workforce Overview", icon: Building2 },
    { id: "Competency Analytics", label: isHindi ? "क्षमता विश्लेषण" : "Competency Analytics", icon: BarChart2 },
    { id: "Skill Gap Analytics", label: isHindi ? "कौशल अंतराल विश्लेषण" : "Skill Gap Analytics", icon: Brain },
    { id: "Training Effectiveness", label: isHindi ? "प्रशिक्षण प्रभावशीलता" : "Training Effectiveness", icon: TrendingUp },
    { id: "Emerging Skills", label: isHindi ? "उभरते कौशल" : "Emerging Skills", icon: Zap },
    { id: "Capacity Planning", label: isHindi ? "क्षमता योजना" : "Capacity Planning", icon: CalendarRange },
    { id: "Users", label: isHindi ? "उपयोगकर्ता पंजी" : "Users", icon: Users },
    { id: "Reports", label: isHindi ? "प्रशासकीय रिपोर्ट" : "Reports", icon: FileBarChart },
    { id: "Profile", label: isHindi ? "प्रोफ़ाइल" : "Profile", icon: UserRound },
  ];

  return (
    <DashboardShell
      activePage={activePage}
      onNavigate={onNavigate}
      navItems={navItems}
      workspaceTitle={isHindi ? "प्रशासक कार्यक्षेत्र" : "Admin workspace · Intelligence Console"}
      headerWorkspaceLabel={isHindi ? "प्रशासक कार्यक्षेत्र" : "SHIKSHASETU WORKSPACE"}
      logoHref="/admin"
      roleBadgeText="System Admin"
      bgClassName="bg-[#f3f1fb]"
      roleTheme={{
        activeNavBg: "bg-[#ede8f8]",
        activeNavText: "text-[#5b3eb5]",
        activeIndicator: "bg-[#5b3eb5]",
        hoverNavBg: "hover:bg-purple-50 hover:text-[#4b36a8]",
        avatarBg: "bg-purple-100 text-[#4b36a8]",
        badgeDotBg: "bg-purple-500",
        headerTitleColor: "text-[#4b36a8]",
      }}
    >
      {children}
    </DashboardShell>
  );
}

export default AdminLayout;
