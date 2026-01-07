export interface Evidence {
  name?: string;
  mission?: string;
  pain?: string;
  team?: string;
  role?: string;
  tool?: string;
  platform?: string;
  need?: string; // Legacy field
  process?: string; // Current processes/methods without specific tools
  insight?: string;
  relevance?: string;
  evidence: string;
}

export interface MissionsFit {
  key_personas: Evidence[];
  relevant_missions: Evidence[];
  pain_points: Evidence[];
  summary: string;
}

export interface ValuePropositionInsight {
  insight: string;
  evidence: string;
  relevance?: string;
}

export interface EfficiencyConversion {
  volume_scale?: ValuePropositionInsight[];
  speed_time_to_market?: ValuePropositionInsight[];
  conversion_revenue?: ValuePropositionInsight[];
}

export interface BrandCreativity {
  brand_consistency?: ValuePropositionInsight[];
  creative_direction?: ValuePropositionInsight[];
  photography_staging?: ValuePropositionInsight[];
}

export interface ValueProposition {
  efficiency_conversion?: EfficiencyConversion;
  brand_creativity?: BrandCreativity;
}

export interface DepartmentTeam {
  key_decision_makers?: Evidence[];
  managers?: Evidence[];
  collaborators?: Evidence[];
}

export interface TeamStructure {
  marketing?: DepartmentTeam;
  ecommerce?: DepartmentTeam;
  creative?: DepartmentTeam;
  product?: DepartmentTeam;
  sales?: DepartmentTeam;
  other?: DepartmentTeam;
  // Legacy fields for backward compatibility
  reports_to?: { role: string; evidence: string } | null;
  collaborates_with?: Evidence[];
  decision_makers?: Evidence[];
  team_info?: string;
}

export interface ToolsEcosystem {
  design_tools?: Evidence[];
  "3d_tools"?: Evidence[];
  photography_tools?: Evidence[];
  ecommerce_platforms?: Evidence[];
  status_quo?: Evidence[];
  // Legacy field for backward compatibility
  other_tools?: Evidence[];
}

export interface JobAnalysis {
  relevance_score: number;
  value_proposition?: ValueProposition;
  missions_fit?: MissionsFit;
  team_structure?: TeamStructure;
  tools_ecosystem?: ToolsEcosystem;
  sales_recommendation?: string;
}

export interface Job {
  job_title: string;
  job_url?: string;
  job_board_url?: string;
  job_board: string;
  location: string;
  date?: string;
  date_creation?: string;
  description: string;
  analysis: JobAnalysis | null;
  success: boolean;
}

// Nouvelle structure pour l'analyse des tendances
export interface TrendCategory {
  signal_strength: number;
  job_count: number;
  key_roles: string[];
  evolution: string;
  new_themes: string[];
  hiring_velocity: "slow" | "moderate" | "fast" | "accelerating";
  evidence: string[];
}

export interface TrendsAnalysis {
  company_name: string;
  analysis_period: {
    start_date: string;
    end_date: string;
    total_jobs: number;
  };
  overall_signal_strength: number;
  overall_summary: string;
  trends: {
    digital_growth_product: TrendCategory;
    visual_content_creative: TrendCategory;
  };
}

export interface Company {
  name: string;
  industry: string;
  website: string;
  employees: string;
  jobs: Job[];
  linkedin?: string;
  trends_analysis?: TrendsAnalysis; // Nouvelle structure d'analyse
}

export interface DataStore {
  companies: Record<string, Company>;
  metadata: {
    started: string;
    completed?: string;
    total_jobs?: number;
  };
}

export interface TAMCompany {
  CompanyName: string;
  Website: string;
  LinkedIn: string;
  "Sub Industry": string;
  Country: string;
  Employees: string;
}

// Types pour les actualités des entreprises
export interface NewsItem {
  title: string;
  source: string;
  url: string;
  published_date: string;
  summary: string;
  relevance_score: number;
  relevance_reason: string;
  key_insights: string[];
  category: 
    // High priority signals (8-10)
    | "catalog_expansion"
    | "supply_chain_challenges"
    | "international_expansion"
    | "time_to_market"
    | "visual_content_strategy"
    | "large_catalog_operations"
    // Medium priority signals (5-7)
    | "omnichannel_strategy"
    | "product_customization"
    | "private_label"
    | "technology_innovation"
    | "sustainability_initiative"
    | "ecommerce_growth"
    // Supporting signals (3-5)
    | "cost_optimization"
    | "merger_acquisition"
    | "platform_migration"
    | "marketing_campaigns"
    | "ai_adoption"
    // Legacy categories (for backward compatibility)
    | "digital_transformation"
    | "visual_content"
    | "ai_investment"
    | "hiring"
    | "partnership"
    | "product_innovation";
}

export interface OverallAssessment {
  presti_fit_score: number;
  key_opportunities: string[];
  recommended_approach: string;
}

export interface CompanyNews {
  company_name: string;
  search_date: string;
  news_items: NewsItem[];
  overall_assessment: OverallAssessment;
  scrape_metadata: {
    timestamp: string;
    model: string;
    success: boolean;
  };
  raw_response?: string;
  error?: string;
}

export interface NewsDataStore {
  [companyName: string]: CompanyNews;
}

// Types pour les interviews du management
export interface ManagementInterviewItem {
  title: string;
  source: string;
  url: string;
  published_date: string;
  format: "interview" | "podcast" | "keynote" | "article" | "panel" | "LinkedIn_post" | "webinar" | "profile";
  executive_name: string;
  executive_title: string;
  summary: string;
  key_quotes: string[];
  topics_discussed: string[];
  relevance_score: number;
  relevance_reason: string;
  sales_insights: string[];
}

export interface KeyExecutive {
  name: string;
  title: string;
  relevance: string;
  content_count: number;
}

export interface ManagementOverallAssessment {
  decision_maker_visibility: "high" | "medium" | "low";
  strategic_priorities: string[];
  presti_entry_points: string[];
  recommended_contact: string;
}

export interface ManagementInterviews {
  company_name: string;
  search_date: string;
  management_items: ManagementInterviewItem[];
  key_executives_identified: KeyExecutive[];
  overall_assessment: ManagementOverallAssessment;
  scrape_metadata: {
    timestamp: string;
    model: string;
    success: boolean;
    web_search_used: boolean;
  };
  raw_response?: string;
  error?: string;
}

export interface ManagementInterviewsDataStore {
  [companyName: string]: ManagementInterviews;
}
