import { useEffect, useState, useMemo } from "react";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { Eye, EyeOff, Building2, Briefcase, Award, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { Role } from "@/lib/api";
import { DEPARTMENT_TAXONOMY } from "@/lib/departments";

export default function LoginPage() {
  const { login } = useAuth();
  const [location, navigate] = useLocation();
  const isRegister = location === "/register";
  const [showPassword, setShowPassword] = useState(false);
  const [roles, setRoles] = useState<Role[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  // Registration fields
  const [fullName, setFullName] = useState("");
  const [employeeId, setEmployeeId] = useState("");
  const [department, setDepartment] = useState("");
  const [selectedRoleCode, setSelectedRoleCode] = useState("");
  const [selectedRoleId, setSelectedRoleId] = useState("");
  const [designation, setDesignation] = useState("");
  const [customDesignation, setCustomDesignation] = useState("");
  const [isCustomDesignation, setIsCustomDesignation] = useState(false);

  // Shared fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    api.roles
      .list()
      .then((data) => {
        setRoles(data || []);
      })
      .catch(() => undefined);
  }, []);

  // Department-filtered available roles
  const availableRoles = useMemo(() => {
    if (!department) return [];
    const deptObj = DEPARTMENT_TAXONOMY.find((d) => d.department_name === department);
    if (!deptObj) return [];
    return deptObj.roles;
  }, [department]);

  // Selected role configuration & description
  const selectedRoleConfig = useMemo(() => {
    return availableRoles.find((r) => r.role_code === selectedRoleCode);
  }, [availableRoles, selectedRoleCode]);

  // Role-filtered available designations
  const availableDesignations = useMemo(() => {
    return selectedRoleConfig ? selectedRoleConfig.designations : [];
  }, [selectedRoleConfig]);

  // Handle Department Change
  const handleDepartmentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const nextDept = e.target.value;
    setDepartment(nextDept);
    // Reset cascading fields
    setSelectedRoleCode("");
    setSelectedRoleId("");
    setDesignation("");
    setCustomDesignation("");
    setIsCustomDesignation(false);
  };

  // Handle Role Change
  const handleRoleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const nextRoleCode = e.target.value;
    setSelectedRoleCode(nextRoleCode);

    // Match backend role ID if available
    const matchedBackendRole = roles.find(
      (r) => r.role_code === nextRoleCode || r.role_name === nextRoleCode
    );
    if (matchedBackendRole) {
      setSelectedRoleId(matchedBackendRole.id);
    } else if (roles.length > 0) {
      setSelectedRoleId(roles[0].id);
    }

    // Reset designation
    setDesignation("");
    setCustomDesignation("");
    setIsCustomDesignation(false);
  };

  // Handle Designation Change
  const handleDesignationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    if (val === "__custom__") {
      setIsCustomDesignation(true);
      setDesignation("");
    } else {
      setIsCustomDesignation(false);
      setDesignation(val);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");

    try {
      if (isRegister) {
        const finalDesignation = isCustomDesignation
          ? customDesignation.trim()
          : designation.trim();

        if (!department) {
          throw new Error("Please select your Department / Ministry");
        }
        if (!selectedRoleCode) {
          throw new Error("Please select your Professional Role");
        }
        if (!finalDesignation) {
          throw new Error("Please select or enter your Designation");
        }

        // Resolve active role ID for backend registration
        let resolvedRoleId = selectedRoleId;
        if (!resolvedRoleId) {
          const matched = roles.find(
            (r) => r.role_code === selectedRoleCode || r.role_name === selectedRoleCode
          );
          resolvedRoleId = matched ? matched.id : roles[0]?.id;
        }

        await api.auth.register({
          full_name: fullName.trim(),
          employee_id: employeeId.trim(),
          designation: finalDesignation,
          department: department.trim(),
          role_id: resolvedRoleId || "6a8ff00dbda6ad0866e7667c",
          email: email.trim(),
          password: password.trim(),
        });

        toast.success("Account created successfully. Please sign in.");
        navigate("/login");
        setPassword("");
      } else {
        await login(email.trim(), password.trim());
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f7fb] text-[#18304f]">
      <header className="mx-auto flex max-w-[1380px] items-center justify-between px-6 py-5 lg:px-12">
        <div className="flex items-center gap-3">
          <img src="/shikshasetu-logo.svg" alt="ShikshaSetu" className="h-16 w-auto" />
        </div>
        <div className="hidden items-center gap-7 text-xs font-bold text-slate-500 md:flex">
          <a href="#capabilities" className="transition-colors hover:text-[#0f9f92]">Capabilities</a>
          <a href="#ecosystem" className="transition-colors hover:text-[#0f9f92]">Learning ecosystem</a>
          <span className="flex items-center gap-2 text-[#123057]"><CheckCircle2 size={15} className="text-[#0f9f92]" /> Protected access</span>
        </div>
      </header>

      <main className="mx-auto grid min-h-[calc(100vh-80px)] max-w-[1380px] items-center gap-10 px-6 pb-10 pt-4 lg:grid-cols-[1.08fr_.92fr] lg:gap-16 lg:px-12 lg:pb-16">
      {/* ── Landing hero ── */}
      <div id="capabilities" className="relative overflow-hidden rounded-[2rem] bg-[#123057] p-8 text-white shadow-[0_24px_70px_rgba(18,48,87,.18)] md:p-12 lg:min-h-[650px]">
        <div className="absolute -right-24 -top-24 h-80 w-80 rounded-full border border-white/10" />
        <div className="absolute -bottom-32 -left-20 h-72 w-72 rounded-full border border-[#38d9c0]/20" />
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-[#38d9c0]/25 bg-white/10 px-3 py-1 text-[10px] font-bold uppercase tracking-[.12em] text-[#8ce9dc]">
            Smart India Hackathon · Public sector learning
          </div>
          <h1 className="mt-7 max-w-xl text-4xl font-extrabold leading-[1.08] tracking-[-.04em] md:text-6xl">
            Build the capability your role demands<span className="text-[#38d9c0]">.</span>
          </h1>
          <p className="mt-6 max-w-lg text-sm leading-7 text-blue-100 md:text-base">
            ShikshaSetu turns competency frameworks into a clear path from assessment to evidence-backed professional growth across India&apos;s civil services.
          </p>

          <div className="mt-10 grid max-w-lg grid-cols-3 gap-3 border-y border-white/10 py-5">
            <div><div className="text-2xl font-extrabold text-[#38d9c0]">01</div><div className="mt-1 text-[10px] font-bold uppercase tracking-wider text-blue-200">Assess</div></div>
            <div><div className="text-2xl font-extrabold text-[#38d9c0]">02</div><div className="mt-1 text-[10px] font-bold uppercase tracking-wider text-blue-200">Learn</div></div>
            <div><div className="text-2xl font-extrabold text-[#38d9c0]">03</div><div className="mt-1 text-[10px] font-bold uppercase tracking-wider text-blue-200">Evidence</div></div>
          </div>

          <div id="ecosystem" className="mt-10 grid gap-3 sm:grid-cols-2">
            {[
              "Role-aware competency frameworks",
              "Explainable AI skill-gap analysis",
              "iGOT Karmayogi & NSSTA pathways",
              "Continuous evidence and assessment",
            ].map((item) => (
              <div key={item} className="flex items-start gap-2 text-xs text-blue-100"><CheckCircle2 size={14} className="mt-0.5 shrink-0 text-[#38d9c0]" /><span>{item}</span></div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Sign-in panel ── */}
      <div className="flex items-center justify-center py-4 anim-page-enter lg:py-10">
        <div className="w-full max-w-[480px]">
          {/* Mobile logo */}
          <div className="mb-6 flex items-center gap-2 lg:hidden">
            <img
              src="/shikshasetu-logo.svg"
              alt="ShikshaSetu"
              className="h-14 w-auto"
            />
          </div>

          <div className="rounded-[2rem] border border-[#dfe7f0] bg-white p-7 shadow-[0_24px_70px_rgba(18,48,87,.12)] anim-card-enter md:p-9">
            {/* Header */}
            <div className="mb-6">
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[#0f9f92]/20 bg-[#e8f6f3] px-3 py-1 text-[11px] font-semibold text-[#0f9f92] anim-badge-pop">
                ShikshaSetu · Capability Intelligence Platform
              </div>
              <div className="text-2xl font-bold text-[#123057] tracking-tight">
                {isRegister ? "Create account" : "Welcome back"}
              </div>
              <p className="mt-1 text-xs text-slate-500 font-normal">
                {isRegister
                  ? "Select your department, role, and designation to initialize your tailored framework"
                  : "Sign in to your capability workspace"}
              </p>
            </div>

            {/* Error banner */}
            {error && (
              <div className="mb-4 rounded-xl bg-red-50 px-4 py-3 text-xs font-medium text-red-700 border border-red-100 anim-fade-up">
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-3.5">
              {isRegister && (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Full Name *
                      </label>
                      <input
                        className="form-input !mt-1"
                        placeholder="e.g. Abhishek Pathak"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        required
                      />
                    </div>

                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Employee ID *
                      </label>
                      <input
                        className="form-input !mt-1"
                        placeholder="e.g. EDU-TEACH-2024"
                        value={employeeId}
                        onChange={(e) => setEmployeeId(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  {/* 1. Department Selector */}
                  <div>
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <Building2 size={12} className="text-[#0f9f92]" />
                      Department / Ministry *
                    </label>
                    <select
                      className="form-input !mt-1 bg-slate-50/50 cursor-pointer font-bold text-[#123057]"
                      value={department}
                      onChange={handleDepartmentChange}
                      required
                    >
                      <option value="">Select Department / Ministry</option>
                      {DEPARTMENT_TAXONOMY.map((dept) => (
                        <option key={dept.department_code} value={dept.department_name}>
                          {dept.department_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* 2. Professional Role Selector (Filtered by Department) */}
                  <div>
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <Briefcase size={12} className="text-[#ef7e37]" />
                      Professional Role *
                    </label>
                    <select
                      className={`form-input !mt-1 cursor-pointer font-bold ${
                        !department ? "bg-slate-100 text-slate-400 cursor-not-allowed" : "text-[#123057]"
                      }`}
                      value={selectedRoleCode}
                      onChange={handleRoleChange}
                      disabled={!department}
                      required
                    >
                      <option value="">
                        {!department ? "← Select department above first" : "Select professional role"}
                      </option>
                      {availableRoles.map((role) => (
                        <option key={role.role_code} value={role.role_code}>
                          {role.role_name}
                        </option>
                      ))}
                    </select>
                    {selectedRoleConfig && (
                      <p className="mt-1 text-[11px] text-slate-500 leading-tight">
                        <span className="font-semibold text-teal-800">Domain:</span> {selectedRoleConfig.domain} · {selectedRoleConfig.description}
                      </p>
                    )}
                  </div>

                  {/* 3. Designation Selector (Filtered by Role) */}
                  <div>
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <Award size={12} className="text-[#6d5bc3]" />
                      Designation *
                    </label>
                    <select
                      className={`form-input !mt-1 cursor-pointer font-bold ${
                        !selectedRoleCode ? "bg-slate-100 text-slate-400 cursor-not-allowed" : "text-[#123057]"
                      }`}
                      value={isCustomDesignation ? "__custom__" : designation}
                      onChange={handleDesignationChange}
                      disabled={!selectedRoleCode}
                      required={!isCustomDesignation}
                    >
                      <option value="">
                        {!selectedRoleCode
                          ? "← Select professional role above first"
                          : "Select your designation"}
                      </option>
                      {availableDesignations.map((des) => (
                        <option key={des} value={des}>
                          {des}
                        </option>
                      ))}
                      {selectedRoleCode && (
                        <option value="__custom__">+ Other (Specify Custom Designation)</option>
                      )}
                    </select>

                    {isCustomDesignation && (
                      <input
                        className="form-input !mt-1.5 border-teal-300 focus:border-teal-500 animate-fadeIn"
                        placeholder="Type your official designation"
                        value={customDesignation}
                        onChange={(e) => setCustomDesignation(e.target.value)}
                        required
                        autoFocus
                      />
                    )}
                  </div>
                </>
              )}

              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  Email address *
                </label>
                <input
                  className="form-input !mt-1"
                  type="email"
                  placeholder="name@example.gov.in"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  Password *
                </label>
                <div className="relative !mt-1">
                  <input
                    className="form-input pr-10 !mt-0"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter secure password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete={isRegister ? "new-password" : "current-password"}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none transition-colors p-1"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={busy}
                className="w-full mt-2 rounded-xl bg-[#ef7e37] px-4 py-3 text-sm font-bold text-white hover:bg-[#d96e2a] disabled:opacity-60 transition-all shadow-md hover:shadow-lg btn-interactive"
              >
                {busy
                  ? "Please wait..."
                  : isRegister
                  ? "Create account"
                  : "Sign in"}
              </button>
            </form>

            {/* Toggle login / register */}
            <button
              type="button"
              className="mt-5 w-full text-xs font-bold text-[#0f9f92] hover:underline btn-interactive"
              onClick={() => {
                setError("");
                navigate(isRegister ? "/login" : "/register");
              }}
            >
              {isRegister
                ? "Already registered? Sign in"
                : "New civil services employee? Create an account"}
            </button>
          </div>
        </div>
      </div>
      </main>
    </div>
  );
}

