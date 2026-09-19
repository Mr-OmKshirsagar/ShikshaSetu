import React, { useState, useMemo, useRef, useEffect } from "react";
import {
  Building2,
  MapPin,
  Briefcase,
  Search,
  Check,
  ChevronDown,
  X,
  PlusCircle,
  Landmark,
} from "lucide-react";
import {
  type GovernmentLevel,
  type GovernmentOrganization,
  type DesignationItem,
  type StateUT,
  STATES_AND_UTS,
  CENTRAL_MINISTRIES,
  DESIGNATION_CATALOGUE,
  getOrganizationsForLevelAndState,
  normalizeStr,
} from "@/lib/governmentTaxonomy";

export interface GovernmentTaxonomySelectorProps {
  level: GovernmentLevel;
  setLevel: (level: GovernmentLevel) => void;
  stateCode: string;
  setStateCode: (code: string) => void;
  selectedOrg: GovernmentOrganization | null;
  setSelectedOrg: (org: GovernmentOrganization | null) => void;
  designation: string;
  setDesignation: (desig: string) => void;
  customDesignation: string;
  setCustomDesignation: (val: string) => void;
  isCustomDesignation: boolean;
  setIsCustomDesignation: (isCustom: boolean) => void;
  disabled?: boolean;
  required?: boolean;
}

export const GovernmentTaxonomySelector: React.FC<GovernmentTaxonomySelectorProps> = ({
  level,
  setLevel,
  stateCode,
  setStateCode,
  selectedOrg,
  setSelectedOrg,
  designation,
  setDesignation,
  customDesignation,
  setCustomDesignation,
  isCustomDesignation,
  setIsCustomDesignation,
  disabled = false,
  required = true,
}) => {
  // Local state for combobox dropdowns
  const [orgOpen, setOrgOpen] = useState(false);
  const [orgSearch, setOrgSearch] = useState("");
  const [desigOpen, setDesigOpen] = useState(false);
  const [desigSearch, setDesigSearch] = useState("");

  const orgRef = useRef<HTMLDivElement>(null);
  const desigRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (orgRef.current && !orgRef.current.contains(event.target as Node)) {
        setOrgOpen(false);
      }
      if (desigRef.current && !desigRef.current.contains(event.target as Node)) {
        setDesigOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Filtered State/UT list according to chosen level
  const statesList = useMemo(() => {
    if (level === "STATE") {
      return STATES_AND_UTS.filter((s) => s.type === "STATE");
    }
    if (level === "UT") {
      return STATES_AND_UTS.filter((s) => s.type === "UT");
    }
    return STATES_AND_UTS;
  }, [level]);

  // Available organizations based on Level and State
  const availableOrganizations = useMemo(() => {
    return getOrganizationsForLevelAndState(level, stateCode);
  }, [level, stateCode]);

  // Filtered organizations by combobox search query
  const filteredOrganizations = useMemo(() => {
    const q = normalizeStr(orgSearch);
    if (!q) return availableOrganizations;
    return availableOrganizations.filter((org) => {
      if (normalizeStr(org.name).includes(q)) return true;
      if (normalizeStr(org.short_name).includes(q)) return true;
      if (normalizeStr(org.organization_type).includes(q)) return true;
      return org.aliases.some((a) => normalizeStr(a).includes(q));
    });
  }, [availableOrganizations, orgSearch]);

  // Filtered designations by combobox search query
  const filteredDesignations = useMemo(() => {
    const q = normalizeStr(desigSearch);
    if (!q) return DESIGNATION_CATALOGUE;
    return DESIGNATION_CATALOGUE.filter((item) => {
      if (normalizeStr(item.title).includes(q)) return true;
      if (normalizeStr(item.domain).includes(q)) return true;
      return item.aliases.some((alias) => normalizeStr(alias).includes(q));
    });
  }, [desigSearch]);

  // Group designations by functional domain
  const groupedDesignations = useMemo(() => {
    const map = new Map<string, DesignationItem[]>();
    for (const d of filteredDesignations) {
      const list = map.get(d.domain) || [];
      list.push(d);
      map.set(d.domain, list);
    }
    return Array.from(map.entries());
  }, [filteredDesignations]);

  // Handle Level Change
  const handleLevelChange = (newLevel: GovernmentLevel) => {
    setLevel(newLevel);
    setSelectedOrg(null);
    setOrgSearch("");
    if (newLevel === "CENTRAL") {
      setStateCode("");
    } else if (newLevel === "STATE" && (!stateCode || statesList.every((s) => s.code !== stateCode))) {
      setStateCode("MH"); // Default sensible state e.g. Maharashtra
    } else if (newLevel === "UT" && (!stateCode || statesList.every((s) => s.code !== stateCode))) {
      setStateCode("DL"); // Default sensible UT e.g. Delhi
    }
  };

  // Handle State Change
  const handleStateChange = (newCode: string) => {
    setStateCode(newCode);
    setSelectedOrg(null);
    setOrgSearch("");
  };

  // Handle Organization Select
  const handleSelectOrg = (org: GovernmentOrganization) => {
    setSelectedOrg(org);
    setOrgOpen(false);
    setOrgSearch("");
  };

  // Handle Designation Select
  const handleSelectDesignation = (desig: DesignationItem) => {
    if (desig.id === "DESIG-OTHER") {
      setIsCustomDesignation(true);
      setDesignation("Other");
    } else {
      setIsCustomDesignation(false);
      setDesignation(desig.title);
      setCustomDesignation("");
    }
    setDesigOpen(false);
    setDesigSearch("");
  };

  return (
    <div className="space-y-4">
      {/* ── 1. Government Level Selector ── */}
      <div>
        <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
          <Landmark size={12} className="text-[#0f9f92]" />
          Government Level *
        </label>
        <div className="mt-1 grid grid-cols-3 gap-2">
          {(
            [
              { id: "CENTRAL", label: "Central Govt" },
              { id: "STATE", label: "State Govt" },
              { id: "UT", label: "Union Territory" },
            ] as const
          ).map((item) => {
            const active = level === item.id;
            return (
              <button
                key={item.id}
                type="button"
                disabled={disabled}
                onClick={() => handleLevelChange(item.id)}
                className={`py-2 px-2.5 rounded-xl border text-xs font-bold transition-all text-center flex items-center justify-center gap-1 ${
                  active
                    ? "bg-[#e8f5f3] border-[#087f76] text-[#087f76] shadow-xs"
                    : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                {active && <Check size={12} className="text-[#087f76]" />}
                {item.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── 2. State / Union Territory Dropdown (when Level != CENTRAL) ── */}
      {level !== "CENTRAL" && (
        <div className="animate-fadeIn">
          <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <MapPin size={12} className="text-[#ef7e37]" />
            {level === "STATE" ? "State *" : "Union Territory *"}
          </label>
          <select
            className="form-input !mt-1 bg-slate-50/50 cursor-pointer font-bold text-[#123057]"
            value={stateCode}
            onChange={(e) => handleStateChange(e.target.value)}
            disabled={disabled}
            required={required}
          >
            <option value="">{level === "STATE" ? "Select State" : "Select Union Territory"}</option>
            {statesList.map((s) => (
              <option key={s.code} value={s.code}>
                {s.name} ({s.code})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* ── 3. Organization / Department / Office (Searchable Combobox) ── */}
      <div className="relative" ref={orgRef}>
        <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Building2 size={12} className="text-[#0f9f92]" />
            Department / Office / Organization *
          </span>
          <span className="text-[9px] font-normal text-slate-400">
            {availableOrganizations.length} available
          </span>
        </label>

        {/* Trigger Button */}
        <button
          type="button"
          disabled={disabled}
          onClick={() => setOrgOpen(!orgOpen)}
          className={`w-full mt-1 border rounded-xl px-3.5 py-2.5 text-xs font-semibold outline-none transition-all flex items-center justify-between text-left cursor-pointer min-h-[42px] focus:ring-2 focus:ring-[#0f9f92]/20 ${
            selectedOrg
              ? "text-[#123057] bg-white border-[#dfe7f0] hover:border-slate-300"
              : "text-slate-400 bg-slate-50/50 border-slate-200 hover:bg-slate-100/50"
          }`}
        >
          <span className="truncate flex-1 min-w-0 mr-2 text-xs font-semibold">
            {selectedOrg ? selectedOrg.name : "Select or search organization..."}
          </span>
          <ChevronDown size={14} className="text-slate-400 shrink-0" />
        </button>

        {/* Combobox Dropdown */}
        {orgOpen && (
          <div className="absolute z-50 left-0 right-0 mt-1 max-h-72 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl flex flex-col animate-fadeIn">
            {/* Search Input */}
            <div className="p-2 border-b border-slate-100 flex items-center gap-2 bg-slate-50">
              <Search size={14} className="text-slate-400 shrink-0 ml-1" />
              <input
                type="text"
                value={orgSearch}
                onChange={(e) => setOrgSearch(e.target.value)}
                placeholder="Type to search (e.g., Revenue, MoSPI, Education, Tahsildar, Talathi)..."
                className="w-full bg-transparent text-xs font-semibold text-[#123057] placeholder:text-slate-400 focus:outline-none"
                autoFocus
              />
              {orgSearch && (
                <button
                  type="button"
                  onClick={() => setOrgSearch("")}
                  className="p-1 hover:bg-slate-200 rounded-full text-slate-400"
                >
                  <X size={12} />
                </button>
              )}
            </div>

            {/* List */}
            <div className="overflow-y-auto flex-1 p-1 max-h-60">
              {filteredOrganizations.length === 0 ? (
                <div className="py-6 text-center text-xs text-slate-400">
                  No matching organizations found for &quot;{orgSearch}&quot;.
                </div>
              ) : (
                filteredOrganizations.map((org) => {
                  const isSelected = selectedOrg?.id === org.id;
                  return (
                    <button
                      key={org.id}
                      type="button"
                      onClick={() => handleSelectOrg(org)}
                      className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors ${
                        isSelected
                          ? "bg-[#e8f5f3] text-[#087f76] font-bold"
                          : "hover:bg-slate-50 text-slate-700"
                      }`}
                    >
                      <div className="truncate pr-2">
                        <div className="font-semibold text-[#123057]">{org.name}</div>
                        <div className="text-[10px] text-slate-400 flex items-center gap-1.5">
                          <span className="bg-slate-100 text-slate-600 px-1.5 py-0.2 rounded font-mono text-[9px]">
                            {org.id}
                          </span>
                          <span>{org.organization_type.replace(/_/g, " ")}</span>
                        </div>
                      </div>
                      {isSelected && <Check size={14} className="text-[#087f76] shrink-0" />}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── 4. Designation Selector (Searchable Combobox with Categories) ── */}
      <div className="relative" ref={desigRef}>
        <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Briefcase size={12} className="text-[#6d5bc3]" />
            Official Government Designation *
          </span>
          <span className="text-[9px] font-normal text-slate-400">
            {DESIGNATION_CATALOGUE.length}+ roles
          </span>
        </label>

        {/* Trigger Button */}
        <button
          type="button"
          disabled={disabled}
          onClick={() => setDesigOpen(!desigOpen)}
          className={`w-full mt-1 border rounded-xl px-3.5 py-2.5 text-xs font-semibold outline-none transition-all flex items-center justify-between text-left cursor-pointer min-h-[42px] focus:ring-2 focus:ring-[#0f9f92]/20 ${
            designation
              ? "text-[#123057] bg-white border-[#dfe7f0] hover:border-slate-300"
              : "text-slate-400 bg-slate-50/50 border-slate-200 hover:bg-slate-100/50"
          }`}
        >
          <span className="truncate flex-1 min-w-0 mr-2 text-xs font-semibold">
            {isCustomDesignation
              ? `Custom: ${customDesignation || "Specify below..."}`
              : designation || "Search designation (e.g., Talathi, Statistical Officer, Teacher)..."}
          </span>
          <ChevronDown size={14} className="text-slate-400 shrink-0" />
        </button>

        {/* Combobox Dropdown */}
        {desigOpen && (
          <div className="absolute z-50 left-0 right-0 mt-1 max-h-80 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl flex flex-col animate-fadeIn">
            {/* Search Input */}
            <div className="p-2 border-b border-slate-100 flex items-center gap-2 bg-slate-50">
              <Search size={14} className="text-slate-400 shrink-0 ml-1" />
              <input
                type="text"
                value={desigSearch}
                onChange={(e) => setDesigSearch(e.target.value)}
                placeholder="Type to search (e.g., Talathi, Stat, Inspector, BDO, Teacher)..."
                className="w-full bg-transparent text-xs font-semibold text-[#123057] placeholder:text-slate-400 focus:outline-none"
                autoFocus
              />
              {desigSearch && (
                <button
                  type="button"
                  onClick={() => setDesigSearch("")}
                  className="p-1 hover:bg-slate-200 rounded-full text-slate-400"
                >
                  <X size={12} />
                </button>
              )}
            </div>

            {/* List with Domain Headings */}
            <div className="overflow-y-auto flex-1 p-1 max-h-64 divide-y divide-slate-100">
              {groupedDesignations.length === 0 ? (
                <div className="py-6 text-center text-xs text-slate-400">
                  No matching designations found.
                </div>
              ) : (
                groupedDesignations.map(([domain, items]) => (
                  <div key={domain} className="py-1">
                    <div className="px-3 py-1 text-[9px] font-bold uppercase tracking-wider text-slate-400">
                      {domain}
                    </div>
                    {items.map((des) => {
                      const isSelected = !isCustomDesignation && designation === des.title;
                      return (
                        <button
                          key={des.id}
                          type="button"
                          onClick={() => handleSelectDesignation(des)}
                          className={`w-full text-left px-3 py-1.5 rounded-xl text-xs flex items-center justify-between transition-colors ${
                            isSelected
                              ? "bg-purple-50 text-[#6d5bc3] font-bold"
                              : "hover:bg-slate-50 text-slate-700"
                          }`}
                        >
                          <div>
                            <span className="font-semibold text-[#123057]">{des.title}</span>
                          </div>
                          {isSelected && <Check size={14} className="text-[#6d5bc3] shrink-0" />}
                        </button>
                      );
                    })}
                  </div>
                ))
              )}

              {/* Always present Other option */}
              <div className="p-1 border-t border-slate-200 bg-slate-50/50">
                <button
                  type="button"
                  onClick={() => {
                    setIsCustomDesignation(true);
                    setDesignation("Other");
                    setDesigOpen(false);
                  }}
                  className="w-full text-left px-3 py-2 rounded-xl text-xs font-bold text-teal-700 hover:bg-teal-50 flex items-center gap-1.5 transition-colors"
                >
                  <PlusCircle size={14} className="text-teal-600" />
                  + Other (Specify Custom Official Designation)
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Custom Designation Input field */}
        {isCustomDesignation && (
          <div className="mt-2 animate-fadeIn">
            <input
              type="text"
              value={customDesignation}
              onChange={(e) => setCustomDesignation(e.target.value)}
              placeholder="Type your official post / designation title"
              disabled={disabled}
              required={required}
              className="form-input border-purple-300 focus:border-purple-600 font-bold text-[#123057]"
              autoFocus
            />
            <p className="mt-1 text-[10px] text-slate-400">
              Please provide your official appointment designation if not listed above.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
