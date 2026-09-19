/**
 * Government Organization & Designation Taxonomy for ShikshaSetu.
 * Grounded in:
 * - Cabinet Secretariat Allocation of Business Rules 2026 & IGOD
 * - All 28 States and 8 Union Territories
 * - Realistic field workforce entities (Talathi, Tehsil, Block, Collectorate, Gram Panchayat)
 * - Searchable Designation Catalogue with domain groupings and aliases
 */

export type GovernmentLevel = "CENTRAL" | "STATE" | "UT";

export type OrganizationType =
  | "MINISTRY"
  | "DEPARTMENT"
  | "INDEPENDENT_DEPARTMENT"
  | "DIRECTORATE"
  | "COMMISSIONERATE"
  | "ATTACHED_OFFICE"
  | "SUBORDINATE_OFFICE"
  | "DISTRICT_ADMINISTRATION"
  | "DIVISIONAL_OFFICE"
  | "TEHSIL"
  | "TALUKA"
  | "BLOCK"
  | "MUNICIPAL_CORPORATION"
  | "MUNICIPAL_COUNCIL"
  | "GRAM_PANCHAYAT"
  | "STATUTORY_BODY"
  | "AUTONOMOUS_BODY"
  | "COMMISSION"
  | "AUTHORITY"
  | "GOVERNMENT_INSTITUTION"
  | "PSU"
  | "OTHER";

export interface GovernmentOrganization {
  id: string;
  name: string;
  short_name: string;
  level: GovernmentLevel;
  organization_type: OrganizationType;
  parent_id?: string | null;
  state_code?: string | null;
  district?: string | null;
  active: boolean;
  source: string;
  source_last_verified: string;
  aliases: string[];
  default_role_code?: string;
}

export interface DesignationItem {
  id: string;
  title: string;
  domain: string;
  category: string;
  archetype_role: string;
  aliases: string[];
}

export interface StateUT {
  code: string;
  name: string;
  type: "STATE" | "UT";
}

// ─── States and Union Territories ───────────────────────────────────────────

export const STATES_AND_UTS: StateUT[] = [
  // 28 States
  { code: "AP", name: "Andhra Pradesh", type: "STATE" },
  { code: "AR", name: "Arunachal Pradesh", type: "STATE" },
  { code: "AS", name: "Assam", type: "STATE" },
  { code: "BR", name: "Bihar", type: "STATE" },
  { code: "CG", name: "Chhattisgarh", type: "STATE" },
  { code: "GA", name: "Goa", type: "STATE" },
  { code: "GJ", name: "Gujarat", type: "STATE" },
  { code: "HR", name: "Haryana", type: "STATE" },
  { code: "HP", name: "Himachal Pradesh", type: "STATE" },
  { code: "JH", name: "Jharkhand", type: "STATE" },
  { code: "KA", name: "Karnataka", type: "STATE" },
  { code: "KL", name: "Kerala", type: "STATE" },
  { code: "MP", name: "Madhya Pradesh", type: "STATE" },
  { code: "MH", name: "Maharashtra", type: "STATE" },
  { code: "MN", name: "Manipur", type: "STATE" },
  { code: "ML", name: "Meghalaya", type: "STATE" },
  { code: "MZ", name: "Mizoram", type: "STATE" },
  { code: "NL", name: "Nagaland", type: "STATE" },
  { code: "OD", name: "Odisha", type: "STATE" },
  { code: "PB", name: "Punjab", type: "STATE" },
  { code: "RJ", name: "Rajasthan", type: "STATE" },
  { code: "SK", name: "Sikkim", type: "STATE" },
  { code: "TN", name: "Tamil Nadu", type: "STATE" },
  { code: "TS", name: "Telangana", type: "STATE" },
  { code: "TR", name: "Tripura", type: "STATE" },
  { code: "UP", name: "Uttar Pradesh", type: "STATE" },
  { code: "UK", name: "Uttarakhand", type: "STATE" },
  { code: "WB", name: "West Bengal", type: "STATE" },
  // 8 Union Territories
  { code: "AN", name: "Andaman and Nicobar Islands", type: "UT" },
  { code: "CH", name: "Chandigarh", type: "UT" },
  { code: "DH", name: "Dadra and Nagar Haveli and Daman and Diu", type: "UT" },
  { code: "DL", name: "Delhi", type: "UT" },
  { code: "JK", name: "Jammu and Kashmir", type: "UT" },
  { code: "LA", name: "Ladakh", type: "UT" },
  { code: "LD", name: "Lakshadweep", type: "UT" },
  { code: "PY", name: "Puducherry", type: "UT" },
];

// ─── Central Ministries (Cabinet Secretariat 2026 / IGOD) ───────────────────

export const CENTRAL_MINISTRIES: GovernmentOrganization[] = [
  {
    id: "GOI-AGRI",
    name: "Ministry of Agriculture and Farmers Welfare",
    short_name: "MoAFW",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Agriculture", "MoAFW", "Department of Agriculture"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-AYUSH",
    name: "Ministry of AYUSH",
    short_name: "AYUSH",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Ayush", "Ayurveda"],
    default_role_code: "PUBLIC_HEALTH_DATA_OFFICER",
  },
  {
    id: "GOI-CHEM",
    name: "Ministry of Chemicals and Fertilizers",
    short_name: "MoCF",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Chemicals and Fertilizers", "MoCF"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-CIVIL",
    name: "Ministry of Civil Aviation",
    short_name: "MoCA",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Civil Aviation", "MoCA", "DGCA"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-COAL",
    name: "Ministry of Coal",
    short_name: "MoC",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Coal"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-COMMERCE",
    name: "Ministry of Commerce and Industry",
    short_name: "MoCI",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Commerce and Industry", "DPIIT", "Commerce"],
    default_role_code: "DATA_ANALYST_OFFICER",
  },
  {
    id: "GOI-COMM",
    name: "Ministry of Communications",
    short_name: "MoC",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Communications", "DoT", "Department of Posts", "India Post"],
    default_role_code: "DIGITAL_GOVERNANCE_ARCHITECT",
  },
  {
    id: "GOI-CONSUMER",
    name: "Ministry of Consumer Affairs, Food and Public Distribution",
    short_name: "MoCAFPD",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Consumer Affairs", "Food and Public Distribution"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-COOP",
    name: "Ministry of Cooperation",
    short_name: "MoCoop",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Cooperation", "Sahakarita"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-CORP",
    name: "Ministry of Corporate Affairs",
    short_name: "MCA",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Corporate Affairs", "MCA", "ROC"],
    default_role_code: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
  },
  {
    id: "GOI-CULTURE",
    name: "Ministry of Culture",
    short_name: "MoC",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Culture", "ASI"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-DEFENCE",
    name: "Ministry of Defence",
    short_name: "MoD",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Defence", "MoD", "DRDO"],
    default_role_code: "CYBERSECURITY_GOVERNANCE_OFFICER",
  },
  {
    id: "GOI-DONER",
    name: "Ministry of Development of North Eastern Region",
    short_name: "MDoNER",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["DoNER"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-EARTH",
    name: "Ministry of Earth Sciences",
    short_name: "MoES",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Earth Sciences", "IMD"],
    default_role_code: "DATA_ANALYST_OFFICER",
  },
  {
    id: "GOI-MOE",
    name: "Ministry of Education",
    short_name: "MoE",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: [
      "Ministry of Education",
      "MoE",
      "Department of School Education & Literacy",
      "Department of Higher Education",
      "NCERT",
    ],
    default_role_code: "EDUCATION_OFFICER",
  },
  {
    id: "GOI-MEITY",
    name: "Ministry of Electronics and Information Technology (MeitY)",
    short_name: "MeitY",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: [
      "Ministry of Electronics and Information Technology",
      "MeitY",
      "National Informatics Centre",
      "NIC",
      "Digital India",
      "CERT-In",
    ],
    default_role_code: "DIGITAL_GOVERNANCE_ARCHITECT",
  },
  {
    id: "GOI-MOEFCC",
    name: "Ministry of Environment, Forest and Climate Change",
    short_name: "MoEFCC",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Environment", "Forest", "MoEFCC"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-MEA",
    name: "Ministry of External Affairs",
    short_name: "MEA",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["External Affairs", "MEA"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-MOF",
    name: "Ministry of Finance",
    short_name: "MoF",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Ministry of Finance", "MoF", "Department of Expenditure", "Department of Economic Affairs"],
    default_role_code: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
  },
  {
    id: "GOI-FAHD",
    name: "Ministry of Fisheries, Animal Husbandry and Dairying",
    short_name: "MoFAHD",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Fisheries", "Animal Husbandry", "MoFAHD"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-FPI",
    name: "Ministry of Food Processing Industries",
    short_name: "MoFPI",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Food Processing", "MoFPI"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-MOHFW",
    name: "Ministry of Health and Family Welfare",
    short_name: "MoHFW",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Ministry of Health and Family Welfare (MoHFW)", "Health", "MoHFW", "National Health Authority"],
    default_role_code: "PUBLIC_HEALTH_DATA_OFFICER",
  },
  {
    id: "GOI-HI",
    name: "Ministry of Heavy Industries",
    short_name: "MHI",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Heavy Industries", "MHI"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-MHA",
    name: "Ministry of Home Affairs",
    short_name: "MHA",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Home Affairs", "MHA", "Internal Security"],
    default_role_code: "CYBERSECURITY_GOVERNANCE_OFFICER",
  },
  {
    id: "GOI-MOHUA",
    name: "Ministry of Housing and Urban Affairs",
    short_name: "MoHUA",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Housing and Urban Affairs", "MoHUA", "Smart Cities"],
    default_role_code: "DIGITAL_GOVERNANCE_ARCHITECT",
  },
  {
    id: "GOI-MIB",
    name: "Ministry of Information and Broadcasting",
    short_name: "MIB",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Information and Broadcasting", "MIB", "PIB"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-JS",
    name: "Ministry of Jal Shakti",
    short_name: "MoJS",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Jal Shakti", "Water Resources", "JJM"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-MOLE",
    name: "Ministry of Labour and Employment",
    short_name: "MoLE",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Labour and Employment", "MoLE", "EPFO", "ESIC"],
    default_role_code: "DATA_ANALYST_OFFICER",
  },
  {
    id: "GOI-LAW",
    name: "Ministry of Law and Justice",
    short_name: "MoLJ",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Law and Justice", "Legal Affairs"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-MSME",
    name: "Ministry of Micro, Small and Medium Enterprises",
    short_name: "MSME",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["MSME"],
    default_role_code: "DATA_ANALYST_OFFICER",
  },
  {
    id: "GOI-MINES",
    name: "Ministry of Mines",
    short_name: "MoM",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Mines", "GSI"],
    default_role_code: "DATA_ANALYST_OFFICER",
  },
  {
    id: "GOI-MINORITY",
    name: "Ministry of Minority Affairs",
    short_name: "MoMA",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Minority Affairs", "MoMA"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-MNRE",
    name: "Ministry of New and Renewable Energy",
    short_name: "MNRE",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Renewable Energy", "MNRE", "Solar"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-PANCHAYAT",
    name: "Ministry of Panchayati Raj",
    short_name: "MoPR",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Panchayati Raj", "MoPR"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-MPA",
    name: "Ministry of Parliamentary Affairs",
    short_name: "MPA",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Parliamentary Affairs", "MPA"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-DOPT",
    name: "Department of Personnel and Training (DoPT)",
    short_name: "DoPT",
    level: "CENTRAL",
    organization_type: "DEPARTMENT",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: [
      "Department of Personnel and Training (DoPT)",
      "DoPT",
      "Ministry of Personnel, Public Grievances and Pensions",
      "Personnel and Training",
      "Mission Karmayogi",
      "Capacity Building Commission",
    ],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-PETRO",
    name: "Ministry of Petroleum and Natural Gas",
    short_name: "MoPNG",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Petroleum", "MoPNG"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-PLANNING",
    name: "Ministry of Planning",
    short_name: "MoP",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Planning", "NITI Aayog"],
    default_role_code: "DATA_ANALYST_OFFICER",
  },
  {
    id: "GOI-PORTS",
    name: "Ministry of Ports, Shipping and Waterways",
    short_name: "MoPSW",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Ports", "Shipping", "MoPSW"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-POWER",
    name: "Ministry of Power",
    short_name: "MoP",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Power", "CEA"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-RAILWAYS",
    name: "Ministry of Railways",
    short_name: "MoR",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Railways", "Railway Board"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-RTH",
    name: "Ministry of Road Transport and Highways",
    short_name: "MoRTH",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Road Transport", "MoRTH", "NHAI"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-MORD",
    name: "Ministry of Rural Development & Panchayati Raj",
    short_name: "MoRD",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: [
      "Ministry of Rural Development & Panchayati Raj",
      "Ministry of Rural Development",
      "Department of Rural Development",
      "MoRD",
      "MGNREGS",
      "NRLM",
    ],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-DST",
    name: "Ministry of Science and Technology",
    short_name: "MoST",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Science and Technology", "DST", "DBT", "CSIR"],
    default_role_code: "DATA_ANALYST_OFFICER",
  },
  {
    id: "GOI-MSDE",
    name: "Ministry of Skill Development and Entrepreneurship",
    short_name: "MSDE",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Skill Development", "MSDE", "NSDC"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-MSJE",
    name: "Ministry of Social Justice and Empowerment",
    short_name: "MoSJE",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Social Justice", "MoSJE"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-MOSPI",
    name: "Ministry of Statistics & Programme Implementation (MoSPI)",
    short_name: "MoSPI",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: [
      "Ministry of Statistics & Programme Implementation (MoSPI)",
      "Ministry of Statistics and Programme Implementation",
      "MoSPI",
      "National Statistical Office",
      "NSO",
      "NSSO",
      "Central Statistics Office",
      "CSO",
      "National Statistical Systems Training Academy",
      "NSSTA",
    ],
    default_role_code: "STATISTICAL_OFFICER",
  },
  {
    id: "GOI-STEEL",
    name: "Ministry of Steel",
    short_name: "MoS",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Steel", "SAIL"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-TEXTILES",
    name: "Ministry of Textiles",
    short_name: "MoT",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Textiles"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-TOURISM",
    name: "Ministry of Tourism",
    short_name: "MoT",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Tourism", "Incredible India"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
  {
    id: "GOI-TRIBAL",
    name: "Ministry of Tribal Affairs",
    short_name: "MoTA",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Tribal Affairs", "MoTA", "TRIFED"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-WCD",
    name: "Ministry of Women and Child Development",
    short_name: "MWCD",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Women and Child Development", "MWCD", "Poshan", "Anganwadi"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
  },
  {
    id: "GOI-YAS",
    name: "Ministry of Youth Affairs and Sports",
    short_name: "MYAS",
    level: "CENTRAL",
    organization_type: "MINISTRY",
    active: true,
    source: "Cabinet Secretariat Allocation of Business Rules 2026",
    source_last_verified: "2026-03",
    aliases: ["Youth Affairs and Sports", "MYAS", "SAI"],
    default_role_code: "CAPACITY_BUILDING_OFFICER",
  },
];

// ─── State Department & Field Office Hierarchies ────────────────────────────

export interface StateDeptTemplate {
  slug: string;
  name: string;
  organization_type: OrganizationType;
  aliases: string[];
  default_role_code: string;
  field_offices: {
    slug: string;
    name: string;
    organization_type: OrganizationType;
  }[];
}

export const STATE_DEPARTMENT_TEMPLATES: StateDeptTemplate[] = [
  {
    slug: "REV",
    name: "Revenue and Land Administration Department",
    organization_type: "DEPARTMENT",
    aliases: ["Revenue Department", "Land Records", "Revenue & Forest", "Bhoomi"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
    field_offices: [
      {
        slug: "DIV",
        name: "Divisional Commissioner Office",
        organization_type: "DIVISIONAL_OFFICE",
      },
      {
        slug: "DIST-COLL",
        name: "District Collectorate / District Administration",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "SUBDIV",
        name: "Sub-Divisional Officer (SDO / SDM) Office",
        organization_type: "SUBORDINATE_OFFICE",
      },
      {
        slug: "TEHSIL",
        name: "Tehsil / Taluka Office",
        organization_type: "TEHSIL",
      },
      {
        slug: "REV-INSP",
        name: "Revenue Circle / Revenue Inspector Office",
        organization_type: "SUBORDINATE_OFFICE",
      },
      {
        slug: "TALATHI",
        name: "Talathi / Patwari Office (Village Revenue Saja)",
        organization_type: "SUBORDINATE_OFFICE",
      },
      {
        slug: "LAND-REC",
        name: "District Land Records & Survey Office",
        organization_type: "DIRECTORATE",
      },
    ],
  },
  {
    slug: "RDPR",
    name: "Rural Development & Panchayati Raj Department",
    organization_type: "DEPARTMENT",
    aliases: ["Panchayat", "Rural Development", "Gram Vikas"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
    field_offices: [
      {
        slug: "ZP",
        name: "Zilla Parishad / District Panchayat",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "DRDA",
        name: "District Rural Development Agency (DRDA)",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "BDO",
        name: "Block Development Office (BDO / Panchayat Samiti)",
        organization_type: "BLOCK",
      },
      {
        slug: "GP",
        name: "Gram Panchayat Office",
        organization_type: "GRAM_PANCHAYAT",
      },
    ],
  },
  {
    slug: "EDU",
    name: "School Education & Literacy Department",
    organization_type: "DEPARTMENT",
    aliases: ["Education Department", "Primary Education", "Secondary Education"],
    default_role_code: "EDUCATION_OFFICER",
    field_offices: [
      {
        slug: "DIR-EDU",
        name: "Directorate of School Education",
        organization_type: "DIRECTORATE",
      },
      {
        slug: "DEO",
        name: "District Education Office (DEO)",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "BEO",
        name: "Block Education Office (BEO)",
        organization_type: "BLOCK",
      },
      {
        slug: "DIET",
        name: "District Institute of Education & Training (DIET)",
        organization_type: "GOVERNMENT_INSTITUTION",
      },
      {
        slug: "SCH-COL",
        name: "Government School / Government College",
        organization_type: "GOVERNMENT_INSTITUTION",
      },
    ],
  },
  {
    slug: "HEALTH",
    name: "Public Health & Family Welfare Department",
    organization_type: "DEPARTMENT",
    aliases: ["Health Department", "Arogya"],
    default_role_code: "PUBLIC_HEALTH_DATA_OFFICER",
    field_offices: [
      {
        slug: "DIR-HEALTH",
        name: "Directorate of Health Services (DHS)",
        organization_type: "DIRECTORATE",
      },
      {
        slug: "DHO",
        name: "District Health Office / Civil Surgeon Office",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "DH-HOSP",
        name: "District Government Hospital / Sub-District Hospital",
        organization_type: "GOVERNMENT_INSTITUTION",
      },
      {
        slug: "CHC-PHC",
        name: "Community Health Centre (CHC) / Primary Health Centre (PHC)",
        organization_type: "GOVERNMENT_INSTITUTION",
      },
    ],
  },
  {
    slug: "FIN",
    name: "Finance & Treasury Department",
    organization_type: "DEPARTMENT",
    aliases: ["Finance Department", "Treasury", "Accounts"],
    default_role_code: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
    field_offices: [
      {
        slug: "DIR-TREASURY",
        name: "Directorate of Accounts & Treasuries",
        organization_type: "DIRECTORATE",
      },
      {
        slug: "DIST-TREASURY",
        name: "District Treasury Office",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "SUB-TREASURY",
        name: "Sub-Treasury Office",
        organization_type: "SUBORDINATE_OFFICE",
      },
    ],
  },
  {
    slug: "HOME",
    name: "Home & Police Administration Department",
    organization_type: "DEPARTMENT",
    aliases: ["Police Department", "Home Department"],
    default_role_code: "CYBERSECURITY_GOVERNANCE_OFFICER",
    field_offices: [
      {
        slug: "DGP",
        name: "Directorate General of Police (DGP HQ)",
        organization_type: "DIRECTORATE",
      },
      {
        slug: "COMM-POLICE",
        name: "Police Commissionerate",
        organization_type: "COMMISSIONERATE",
      },
      {
        slug: "SP-OFFICE",
        name: "District Police Office (SP / SSP Office)",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "SDPO",
        name: "Sub-Divisional Police Office (SDPO / DSP)",
        organization_type: "SUBORDINATE_OFFICE",
      },
      {
        slug: "POLICE-STATION",
        name: "Police Station",
        organization_type: "SUBORDINATE_OFFICE",
      },
    ],
  },
  {
    slug: "UD",
    name: "Urban Development & Municipal Administration",
    organization_type: "DEPARTMENT",
    aliases: ["Urban Development", "Municipalities", "Nagar Vikas"],
    default_role_code: "DIGITAL_GOVERNANCE_ARCHITECT",
    field_offices: [
      {
        slug: "MCORP",
        name: "Municipal Corporation",
        organization_type: "MUNICIPAL_CORPORATION",
      },
      {
        slug: "MCOUNCIL",
        name: "Municipal Council / Municipality",
        organization_type: "MUNICIPAL_COUNCIL",
      },
      {
        slug: "NAGARP",
        name: "Nagar Panchayat / Town Panchayat",
        organization_type: "SUBORDINATE_OFFICE",
      },
    ],
  },
  {
    slug: "IT",
    name: "Information Technology & e-Governance Department",
    organization_type: "DEPARTMENT",
    aliases: ["IT Department", "DIT", "e-Governance", "State Informatics"],
    default_role_code: "DIGITAL_GOVERNANCE_ARCHITECT",
    field_offices: [
      {
        slug: "DIR-IT",
        name: "Directorate of Information Technology",
        organization_type: "DIRECTORATE",
      },
      {
        slug: "SEMT",
        name: "State e-Mission Team (SeMT)",
        organization_type: "AUTONOMOUS_BODY",
      },
      {
        slug: "DIST-EDIST",
        name: "District e-Governance Society (DeGS)",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
    ],
  },
  {
    slug: "AGRI",
    name: "Agriculture & Horticulture Department",
    organization_type: "DEPARTMENT",
    aliases: ["State Agriculture Department", "Krishi Vibhag"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
    field_offices: [
      {
        slug: "DIR-AGRI",
        name: "Directorate of Agriculture",
        organization_type: "DIRECTORATE",
      },
      {
        slug: "DAO",
        name: "District Agriculture Office (DAO)",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "BAO",
        name: "Block Agriculture Office",
        organization_type: "BLOCK",
      },
    ],
  },
  {
    slug: "WCD",
    name: "Women & Child Development and Social Welfare",
    organization_type: "DEPARTMENT",
    aliases: ["Mahila Bal Vikas", "Social Welfare"],
    default_role_code: "RURAL_DEVELOPMENT_OFFICER",
    field_offices: [
      {
        slug: "DIR-WCD",
        name: "Directorate of Women & Child Development",
        organization_type: "DIRECTORATE",
      },
      {
        slug: "DWCDO",
        name: "District Social Welfare / WCD Office",
        organization_type: "DISTRICT_ADMINISTRATION",
      },
      {
        slug: "CDPO",
        name: "Child Development Project Office (CDPO / ICDS)",
        organization_type: "BLOCK",
      },
    ],
  },
];

// ─── Searchable Designation Catalogue ───────────────────────────────────────

export const DESIGNATION_CATALOGUE: DesignationItem[] = [
  // 1. Administrative / Civil Service
  {
    id: "DESIG-ADM-SEC",
    title: "Secretary",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Principal Secretary", "Chief Secretary", "Special Secretary"],
  },
  {
    id: "DESIG-ADM-ADDSEC",
    title: "Additional Secretary",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Addl Secretary"],
  },
  {
    id: "DESIG-ADM-JTSEC",
    title: "Joint Secretary",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["JS"],
  },
  {
    id: "DESIG-ADM-DIR",
    title: "Director",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Director (Admin)", "Director (Training)", "Director (Macroeconomic Statistics)"],
  },
  {
    id: "DESIG-ADM-DEPSEC",
    title: "Deputy Secretary",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["DS"],
  },
  {
    id: "DESIG-ADM-UNDSEC",
    title: "Under Secretary",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["US"],
  },
  {
    id: "DESIG-ADM-SECOFF",
    title: "Section Officer (SO)",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Section Officer", "SO"],
  },
  {
    id: "DESIG-ADM-ASSTSEC",
    title: "Assistant Section Officer (ASO)",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Assistant Section Officer", "ASO"],
  },
  {
    id: "DESIG-ADM-ADMOFF",
    title: "Administrative Officer",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["AO"],
  },
  {
    id: "DESIG-ADM-DISTCOLL",
    title: "District Collector / District Magistrate",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["District Collector", "District Magistrate", "DM", "DC"],
  },
  {
    id: "DESIG-ADM-ADDCOLL",
    title: "Additional Collector / Additional DM",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Additional Collector", "ADM", "ADC"],
  },
  {
    id: "DESIG-ADM-DEPCOLL",
    title: "Deputy Collector",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Dy Collector"],
  },
  {
    id: "DESIG-ADM-SDO",
    title: "Sub-Divisional Officer (SDO / SDM)",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Sub-Divisional Officer", "SDO", "SDM", "Sub-Divisional Magistrate", "Prant Officer"],
  },
  {
    id: "DESIG-ADM-TEHSILDAR",
    title: "Tahsildar / Tehsildar",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Tahsildar", "Tehsildar", "Mamlatdar", "Taluk Executive Magistrate"],
  },
  {
    id: "DESIG-ADM-NAIBTEHSIL",
    title: "Naib Tahsildar / Nayab Tehsildar",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Naib Tehsildar", "Nayab Tehsildar", "Naib Tahsildar"],
  },
  {
    id: "DESIG-ADM-BDO",
    title: "Block Development Officer (BDO)",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Block Development Officer", "BDO"],
  },
  {
    id: "DESIG-ADM-EXTOFF",
    title: "Extension Officer",
    domain: "Administrative / Civil Service",
    category: "CIVIL_SERVICE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Extension Officer", "EO"],
  },

  // 2. Revenue / Land Administration
  {
    id: "DESIG-REV-TALATHI",
    title: "Talathi",
    domain: "Revenue / Land Administration",
    category: "REVENUE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Talathi", "Village Revenue Officer", "VRO", "Village Accountant", "Karnam"],
  },
  {
    id: "DESIG-REV-PATWARI",
    title: "Patwari",
    domain: "Revenue / Land Administration",
    category: "REVENUE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Patwari", "Village Patwari"],
  },
  {
    id: "DESIG-REV-LEKHPAL",
    title: "Lekhpal",
    domain: "Revenue / Land Administration",
    category: "REVENUE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Lekhpal", "Rajasva Lekhpal"],
  },
  {
    id: "DESIG-REV-REV_INSP",
    title: "Revenue Inspector",
    domain: "Revenue / Land Administration",
    category: "REVENUE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Revenue Inspector", "RI", "Kanoongo", "Girdawar"],
  },
  {
    id: "DESIG-REV-CIRCLE",
    title: "Circle Officer",
    domain: "Revenue / Land Administration",
    category: "REVENUE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Circle Officer", "CO"],
  },
  {
    id: "DESIG-REV-REVOFF",
    title: "Revenue Officer",
    domain: "Revenue / Land Administration",
    category: "REVENUE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Revenue Officer", "Assistant Commissioner (Revenue)"],
  },
  {
    id: "DESIG-REV-SURVEYOR",
    title: "Surveyor / Land Records Surveyor",
    domain: "Revenue / Land Administration",
    category: "REVENUE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Surveyor", "Land Surveyor", "Bhumi Abhilekh Nirikshak"],
  },
  {
    id: "DESIG-REV-LAND_RECORDS",
    title: "Land Records Officer",
    domain: "Revenue / Land Administration",
    category: "REVENUE",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["District Inspector Land Records", "DILR", "Superintendent Land Records"],
  },

  // 3. Statistics / Data
  {
    id: "DESIG-STAT-OFFICER",
    title: "Statistical Officer",
    domain: "Statistics / Data",
    category: "STATISTICS",
    archetype_role: "STATISTICAL_OFFICER",
    aliases: ["Statistical Officer", "SO (Stats)"],
  },
  {
    id: "DESIG-STAT-SSO",
    title: "Senior Statistical Officer (SSO)",
    domain: "Statistics / Data",
    category: "STATISTICS",
    archetype_role: "STATISTICAL_OFFICER",
    aliases: ["Senior Statistical Officer", "SSO"],
  },
  {
    id: "DESIG-STAT-ASST_STAT",
    title: "Assistant Statistical Officer",
    domain: "Statistics / Data",
    category: "STATISTICS",
    archetype_role: "STATISTICAL_OFFICER",
    aliases: ["Assistant Statistical Officer", "ASO (Stats)"],
  },
  {
    id: "DESIG-STAT-INVESTIGATOR",
    title: "Statistical Investigator",
    domain: "Statistics / Data",
    category: "STATISTICS",
    archetype_role: "STATISTICAL_OFFICER",
    aliases: ["Statistical Investigator", "JSO", "Junior Statistical Officer"],
  },
  {
    id: "DESIG-STAT-ANALYST",
    title: "Data Analyst",
    domain: "Statistics / Data",
    category: "STATISTICS",
    archetype_role: "DATA_ANALYST_OFFICER",
    aliases: ["Data Analyst", "Senior Data Analyst", "Lead Statistician"],
  },
  {
    id: "DESIG-STAT-RESEARCH",
    title: "Research Officer",
    domain: "Statistics / Data",
    category: "STATISTICS",
    archetype_role: "STATISTICAL_OFFICER",
    aliases: ["Research Officer", "Assistant Director (Statistics)"],
  },
  {
    id: "DESIG-STAT-ECON_INVEST",
    title: "Economic Investigator",
    domain: "Statistics / Data",
    category: "STATISTICS",
    archetype_role: "DATA_ANALYST_OFFICER",
    aliases: ["Economic Investigator", "Economic Officer"],
  },
  {
    id: "DESIG-STAT-ASST",
    title: "Statistical Assistant",
    domain: "Statistics / Data",
    category: "STATISTICS",
    archetype_role: "STATISTICAL_OFFICER",
    aliases: ["Statistical Assistant", "Computor"],
  },

  // 4. Finance / Accounts
  {
    id: "DESIG-FIN-AO",
    title: "Accounts Officer",
    domain: "Finance / Accounts",
    category: "FINANCE",
    archetype_role: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
    aliases: ["Accounts Officer", "AO", "Senior Accounts Officer"],
  },
  {
    id: "DESIG-FIN-AAO",
    title: "Assistant Accounts Officer (AAO)",
    domain: "Finance / Accounts",
    category: "FINANCE",
    archetype_role: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
    aliases: ["Assistant Accounts Officer", "AAO", "Accounts Officer (AAO / AO)"],
  },
  {
    id: "DESIG-FIN-ACCOUNTANT",
    title: "Accountant",
    domain: "Finance / Accounts",
    category: "FINANCE",
    archetype_role: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
    aliases: ["Accountant", "Senior Accountant", "Junior Accountant"],
  },
  {
    id: "DESIG-FIN-TREASURY",
    title: "Treasury Officer",
    domain: "Finance / Accounts",
    category: "FINANCE",
    archetype_role: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
    aliases: ["Treasury Officer", "District Treasury Officer", "Sub-Treasury Officer"],
  },
  {
    id: "DESIG-FIN-AUDIT",
    title: "Audit Officer",
    domain: "Finance / Accounts",
    category: "FINANCE",
    archetype_role: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
    aliases: ["Audit Officer", "Senior Audit Officer", "Auditor"],
  },
  {
    id: "DESIG-FIN-CASHIER",
    title: "Cashier",
    domain: "Finance / Accounts",
    category: "FINANCE",
    archetype_role: "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
    aliases: ["Cashier", "Head Cashier"],
  },

  // 5. Education
  {
    id: "DESIG-EDU-TEACHER",
    title: "Teacher",
    domain: "Education",
    category: "EDUCATION",
    archetype_role: "EDUCATION_OFFICER",
    aliases: [
      "Teacher",
      "Primary Teacher (PRT)",
      "Trained Graduate Teacher (TGT)",
      "Post Graduate Teacher (PGT)",
      "Senior Teacher (PGT/TGT)",
    ],
  },
  {
    id: "DESIG-EDU-HEADMASTER",
    title: "Headmaster / Principal",
    domain: "Education",
    category: "EDUCATION",
    archetype_role: "EDUCATION_OFFICER",
    aliases: ["Headmaster", "Principal", "Vice Principal", "Headmistress"],
  },
  {
    id: "DESIG-EDU-BEO",
    title: "Block Education Officer (BEO)",
    domain: "Education",
    category: "EDUCATION",
    archetype_role: "EDUCATION_OFFICER",
    aliases: ["Block Education Officer", "BEO"],
  },
  {
    id: "DESIG-EDU-DEO",
    title: "District Education Officer (DEO)",
    domain: "Education",
    category: "EDUCATION",
    archetype_role: "EDUCATION_OFFICER",
    aliases: ["District Education Officer", "DEO"],
  },
  {
    id: "DESIG-EDU-LECTURER",
    title: "Lecturer / Assistant Professor",
    domain: "Education",
    category: "EDUCATION",
    archetype_role: "EDUCATION_OFFICER",
    aliases: ["Assistant Professor", "Lecturer", "Professor", "Assistant Professor / Lecturer"],
  },
  {
    id: "DESIG-EDU-EDTECH",
    title: "Digital Learning & EdTech Specialist",
    domain: "Education",
    category: "EDUCATION",
    archetype_role: "DIGITAL_LEARNING_SPECIALIST",
    aliases: ["Digital Learning Specialist", "EdTech Coordinator", "Smart Classroom Lead", "Online Assessment Officer", "ICT In-charge"],
  },
  {
    id: "DESIG-EDU-CURRICULUM",
    title: "Curriculum & Assessment Specialist",
    domain: "Education",
    category: "EDUCATION",
    archetype_role: "EDUCATION_OFFICER",
    aliases: ["Curriculum & Assessment Specialist", "Education Research Officer", "Curriculum Specialist"],
  },

  // 6. Health
  {
    id: "DESIG-HEALTH-MO",
    title: "Medical Officer",
    domain: "Health",
    category: "HEALTH",
    archetype_role: "PUBLIC_HEALTH_DATA_OFFICER",
    aliases: ["Medical Officer", "Medical Officer (Public Health)", "MO", "Civil Assistant Surgeon"],
  },
  {
    id: "DESIG-HEALTH-CMO",
    title: "Chief Medical Officer (CMO)",
    domain: "Health",
    category: "HEALTH",
    archetype_role: "PUBLIC_HEALTH_DATA_OFFICER",
    aliases: ["Chief Medical Officer", "CMO", "Civil Surgeon"],
  },
  {
    id: "DESIG-HEALTH-PUBLIC_HEALTH",
    title: "Public Health Officer",
    domain: "Health",
    category: "HEALTH",
    archetype_role: "PUBLIC_HEALTH_DATA_OFFICER",
    aliases: ["Public Health Officer", "District Health Programme Officer", "Surveillance Officer"],
  },
  {
    id: "DESIG-HEALTH-NURSE",
    title: "Staff Nurse",
    domain: "Health",
    category: "HEALTH",
    archetype_role: "PUBLIC_HEALTH_DATA_OFFICER",
    aliases: ["Staff Nurse", "Nursing Officer", "Senior Nursing Officer"],
  },
  {
    id: "DESIG-HEALTH-PHARMACIST",
    title: "Pharmacist",
    domain: "Health",
    category: "HEALTH",
    archetype_role: "PUBLIC_HEALTH_DATA_OFFICER",
    aliases: ["Pharmacist", "Chief Pharmacist"],
  },
  {
    id: "DESIG-HEALTH-LAB_TECH",
    title: "Lab Technician",
    domain: "Health",
    category: "HEALTH",
    archetype_role: "PUBLIC_HEALTH_DATA_OFFICER",
    aliases: ["Lab Technician", "Laboratory Assistant"],
  },
  {
    id: "DESIG-HEALTH-INSPECTOR",
    title: "Health Inspector / Sanitary Inspector",
    domain: "Health",
    category: "HEALTH",
    archetype_role: "PUBLIC_HEALTH_DATA_OFFICER",
    aliases: ["Health Inspector", "Sanitary Inspector", "Food Safety Officer"],
  },

  // 7. IT & Digital Governance
  {
    id: "DESIG-IT-ARCHITECT",
    title: "Digital Governance & e-Gov Architect",
    domain: "IT / Digital Governance",
    category: "IT",
    archetype_role: "DIGITAL_GOVERNANCE_ARCHITECT",
    aliases: ["Enterprise Architect", "e-Governance Project Lead", "Technical Director (e-Gov)"],
  },
  {
    id: "DESIG-IT-OFFICER",
    title: "Informatics Officer / Scientist 'B'",
    domain: "IT / Digital Governance",
    category: "IT",
    archetype_role: "DIGITAL_GOVERNANCE_ARCHITECT",
    aliases: [
      "Informatics Officer / Scientist 'B'",
      "Scientist B",
      "IT Systems Officer",
      "IT Officer",
      "District Informatics Officer (DIO)",
    ],
  },
  {
    id: "DESIG-IT-CYBER",
    title: "Cybersecurity & Data Privacy Officer",
    domain: "IT / Digital Governance",
    category: "IT",
    archetype_role: "CYBERSECURITY_GOVERNANCE_OFFICER",
    aliases: ["Cybersecurity Lead", "Information Security Officer (CISO Team)", "Data Protection Officer", "Security Auditor"],
  },
  {
    id: "DESIG-IT-DEV",
    title: "Software Developer / Data Engineer",
    domain: "IT / Digital Governance",
    category: "IT",
    archetype_role: "DIGITAL_GOVERNANCE_ARCHITECT",
    aliases: ["Software Developer", "Data Engineer", "Systems Analyst", "Network Engineer"],
  },

  // 8. Police / Public Safety
  {
    id: "DESIG-POL-SP",
    title: "Superintendent of Police (SP / SSP)",
    domain: "Police / Public Safety",
    category: "POLICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Superintendent of Police", "SP", "SSP", "DCP"],
  },
  {
    id: "DESIG-POL-DSP",
    title: "Deputy Superintendent of Police (DSP / ACP)",
    domain: "Police / Public Safety",
    category: "POLICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Deputy Superintendent of Police", "DSP", "DySP", "ACP"],
  },
  {
    id: "DESIG-POL-INSPECTOR",
    title: "Police Inspector",
    domain: "Police / Public Safety",
    category: "POLICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Police Inspector", "PI", "SHO"],
  },
  {
    id: "DESIG-POL-SI",
    title: "Sub-Inspector (SI)",
    domain: "Police / Public Safety",
    category: "POLICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Sub-Inspector", "SI"],
  },
  {
    id: "DESIG-POL-ASI",
    title: "Assistant Sub-Inspector (ASI)",
    domain: "Police / Public Safety",
    category: "POLICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Assistant Sub-Inspector", "ASI"],
  },
  {
    id: "DESIG-POL-CONSTABLE",
    title: "Head Constable / Constable",
    domain: "Police / Public Safety",
    category: "POLICE",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Constable", "Head Constable", "Police Constable"],
  },

  // 9. Panchayat / Rural Development
  {
    id: "DESIG-PANCH-SEC",
    title: "Panchayat Secretary",
    domain: "Panchayat / Rural Development",
    category: "PANCHAYAT",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Panchayat Secretary", "Gram Panchayat Secretary"],
  },
  {
    id: "DESIG-PANCH-SEVAK",
    title: "Gram Sevak / Village Development Officer (VDO)",
    domain: "Panchayat / Rural Development",
    category: "PANCHAYAT",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["Gram Sevak", "Gram Sevika", "Village Development Officer", "VDO"],
  },
  {
    id: "DESIG-PANCH-PROJ_MGR",
    title: "District Project Manager (NRLM / MGNREGS)",
    domain: "Panchayat / Rural Development",
    category: "PANCHAYAT",
    archetype_role: "RURAL_DEVELOPMENT_OFFICER",
    aliases: ["District Project Manager", "DPM", "NRLM Coordinator"],
  },

  // 10. General Administration / Support
  {
    id: "DESIG-GEN-SUPT",
    title: "Office Superintendent",
    domain: "General Administration / Support",
    category: "SUPPORT",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Office Superintendent", "Superintendent"],
  },
  {
    id: "DESIG-GEN-CLERK",
    title: "Clerk (Senior / Junior Clerk)",
    domain: "General Administration / Support",
    category: "SUPPORT",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Clerk", "Junior Clerk", "Senior Clerk", "Office Assistant", "LDC", "UDC"],
  },
  {
    id: "DESIG-GEN-DEO",
    title: "Data Entry Operator (DEO)",
    domain: "General Administration / Support",
    category: "SUPPORT",
    archetype_role: "DATA_ANALYST_OFFICER",
    aliases: ["Data Entry Operator", "DEO", "Computer Operator"],
  },
  {
    id: "DESIG-GEN-STENO",
    title: "Personal Assistant / Stenographer",
    domain: "General Administration / Support",
    category: "SUPPORT",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Personal Assistant", "PA", "Stenographer", "Private Secretary", "PS"],
  },

  // 11. Custom / Other
  {
    id: "DESIG-OTHER",
    title: "Other — Please specify",
    domain: "Other Government Function",
    category: "OTHER",
    archetype_role: "CAPACITY_BUILDING_OFFICER",
    aliases: ["Other", "Custom Designation"],
  },
];

// ─── Utility Helper Functions ───────────────────────────────────────────────

export function normalizeStr(s?: string | null): string {
  if (!s) return "";
  return s.trim().toLowerCase().replace(/\s+/g, " ");
}

/**
 * Returns available organizations based on Government Level and State/UT selection.
 */
export function getOrganizationsForLevelAndState(
  level: GovernmentLevel,
  stateCode?: string | null
): GovernmentOrganization[] {
  if (level === "CENTRAL") {
    return CENTRAL_MINISTRIES;
  }

  // State or UT Level: Generate state-specific departments and field offices
  const stateObj = STATES_AND_UTS.find((s) => s.code === stateCode);
  const statePrefix = stateCode || (level === "UT" ? "UT" : "STATE");
  const stateName = stateObj ? stateObj.name : "State Government";

  const orgs: GovernmentOrganization[] = [];

  for (const tmpl of STATE_DEPARTMENT_TEMPLATES) {
    // 1. State Department level
    const deptId = `${statePrefix}-${tmpl.slug}`;
    orgs.push({
      id: deptId,
      name: `${tmpl.name} (${stateName})`,
      short_name: `${statePrefix}-${tmpl.slug}`,
      level,
      organization_type: tmpl.organization_type,
      state_code: stateCode,
      active: true,
      source: "State Government Portal & IGOD",
      source_last_verified: "2026-03",
      aliases: tmpl.aliases.map((a) => `${a} ${stateName}`),
      default_role_code: tmpl.default_role_code,
    });

    // 2. Field Offices under this department
    for (const off of tmpl.field_offices) {
      orgs.push({
        id: `${statePrefix}-${tmpl.slug}-${off.slug}`,
        name: `${off.name} (${tmpl.name}, ${stateName})`,
        short_name: `${off.slug}`,
        level,
        organization_type: off.organization_type,
        parent_id: deptId,
        state_code: stateCode,
        active: true,
        source: "State Government Administration Directory",
        source_last_verified: "2026-03",
        aliases: [off.name, `${off.name} ${stateName}`],
        default_role_code: tmpl.default_role_code,
      });
    }
  }

  return orgs;
}

/**
 * Filter designations by query with fuzzy matching across title, domain, and aliases.
 */
export function searchDesignations(query: string): DesignationItem[] {
  const q = normalizeStr(query);
  if (!q) return DESIGNATION_CATALOGUE;

  return DESIGNATION_CATALOGUE.filter((item) => {
    if (normalizeStr(item.title).includes(q)) return true;
    if (normalizeStr(item.domain).includes(q)) return true;
    return item.aliases.some((alias) => normalizeStr(alias).includes(q));
  });
}

/**
 * Filter organizations by search query.
 */
export function searchOrganizations(
  orgs: GovernmentOrganization[],
  query: string
): GovernmentOrganization[] {
  const q = normalizeStr(query);
  if (!q) return orgs;

  return orgs.filter((org) => {
    if (normalizeStr(org.name).includes(q)) return true;
    if (normalizeStr(org.short_name).includes(q)) return true;
    return org.aliases.some((alias) => normalizeStr(alias).includes(q));
  });
}
