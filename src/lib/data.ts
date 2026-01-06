import { DataStore, Company, TAMCompany, Job } from "./types";

let cachedData: DataStore | null = null;
let cachedTAM: TAMCompany[] | null = null;

// Filter out sales positions
function filterSalesJobs(jobs: Job[]): Job[] {
  const salesKeywords = [
    'sales associate',
    'sales manager',
    'sales representative',
    'sales consultant',
    'sales analyst',
    'retail sales',
    'inside sales',
    'field sales',
    'showroom sales',
    'web sales',
  ];
  
  return jobs.filter(job => {
    const title = job.job_title.toLowerCase();
    // Keep the job if it doesn't contain sales-only keywords
    // But keep jobs like "Director of Sales" or marketing/design roles that mention sales
    const isSalesOnlyRole = salesKeywords.some(keyword => title.includes(keyword));
    return !isSalesOnlyRole;
  });
}

export async function getData(): Promise<DataStore> {
  if (cachedData) return cachedData;
  
  const res = await fetch("/data.json");
  const rawData: DataStore = await res.json();
  
  // Filter sales jobs from each company
  const filteredCompanies: Record<string, Company> = {};
  
  Object.entries(rawData.companies).forEach(([name, company]) => {
    const filteredJobs = filterSalesJobs(company.jobs);
    if (filteredJobs.length > 0) {
      filteredCompanies[name] = {
        ...company,
        jobs: filteredJobs,
      };
    }
  });
  
  cachedData = {
    ...rawData,
    companies: filteredCompanies,
  };
  
  return cachedData;
}

export async function getTAMData(): Promise<TAMCompany[]> {
  if (cachedTAM) return cachedTAM;
  
  const res = await fetch("/TAM.csv");
  const text = await res.text();
  
  const lines = text.split("\n");
  const headers = lines[0].split(",");
  
  cachedTAM = lines.slice(1).filter(line => line.trim()).map(line => {
    const values = line.split(",");
    const obj: Record<string, string> = {};
    headers.forEach((header, i) => {
      obj[header.trim()] = values[i]?.trim() || "";
    });
    return obj as unknown as TAMCompany;
  });
  
  return cachedTAM;
}

export function getCompanyStats(company: Company) {
  const jobs = company.jobs;
  const analyzedJobs = jobs.filter(j => j.analysis);
  
  const scores = analyzedJobs.map(j => j.analysis!.relevance_score);
  const avgScore = scores.length > 0 
    ? Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 10) / 10 
    : 0;
  
  const highRelevance = scores.filter(s => s >= 7).length;
  
  // Get unique decision makers
  const decisionMakers = new Set<string>();
  analyzedJobs.forEach(j => {
    j.analysis?.team_structure?.decision_makers?.forEach(d => {
      if (d.role) decisionMakers.add(d.role);
    });
  });
  
  // Get unique tools
  const tools = new Set<string>();
  analyzedJobs.forEach(j => {
    j.analysis?.tools_ecosystem?.design_tools?.forEach(t => {
      if (t.tool) tools.add(t.tool);
    });
    j.analysis?.tools_ecosystem?.["3d_tools"]?.forEach(t => {
      if (t.tool) tools.add(t.tool);
    });
    j.analysis?.tools_ecosystem?.ecommerce_platforms?.forEach(t => {
      if (t.platform) tools.add(t.platform);
    });
  });
  
  // Get key insights
  const keyInsights: string[] = [];
  analyzedJobs.forEach(j => {
    if (j.job_title.toLowerCase().includes("ai") || j.job_title.toLowerCase().includes("artificial")) {
      keyInsights.push(`🤖 AI-related role: ${j.job_title}`);
    }
    if (j.analysis?.relevance_score && j.analysis.relevance_score >= 9) {
      keyInsights.push(`⭐ High-value target: ${j.job_title}`);
    }
  });
  
  return {
    totalJobs: jobs.length,
    avgScore,
    highRelevance,
    decisionMakers: Array.from(decisionMakers),
    tools: Array.from(tools),
    keyInsights: keyInsights.slice(0, 5),
  };
}
