"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getData } from "@/lib/data";
import { Company, CompanyNews, ManagementInterviews } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft, 
  Globe, 
  Linkedin, 
  Building2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { OverviewTab } from "@/components/company/OverviewTab";
import { TechStackTab } from "@/components/company/TechStackTab";
import { NewsTab } from "@/components/company/NewsTab";
import { ManagementInterviewsTab } from "@/components/company/ManagementInterviewsTab";

export default function CompanyPage() {
  const params = useParams();
  const companyName = decodeURIComponent(params.company as string);
  
  const [company, setCompany] = useState<Company | null>(null);
  const [companyNews, setCompanyNews] = useState<CompanyNews | null>(null);
  const [managementInterviews, setManagementInterviews] = useState<ManagementInterviews | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"jobs" | "tech" | "company_news" | "management_interviews">("jobs");

  // Function to reload data
  const loadCompanyData = () => {
    getData().then((data) => {
      // Try exact match first, then lowercase
      const found = data.companies[companyName] || data.companies[companyName.toLowerCase()];
      setCompany(found || null);
      setLoading(false);
    });
  };

  const loadNewsData = () => {
    fetch('/news_data.json?' + Date.now()) // Cache bust
      .then(res => res.json())
      .then((data) => {
        // Try to find news with case-insensitive search
        let news = data[companyName];
        if (!news) {
          // Try to find by case-insensitive match
          const key = Object.keys(data).find(k => k.toLowerCase() === companyName.toLowerCase());
          news = key ? data[key] : null;
        }
        setCompanyNews(news || null);
      })
      .catch(() => {
        setCompanyNews(null);
      });
  };

  const loadInterviewsData = () => {
    console.log('[loadInterviewsData] Loading interviews for:', companyName);
    fetch('/management_interviews.json?' + Date.now()) // Cache bust
      .then(res => res.json())
      .then((data) => {
        console.log('[loadInterviewsData] Received data:', data);
        // Try to find interviews with case-insensitive search
        let interviews = data[companyName];
        if (!interviews) {
          // Try to find by case-insensitive match
          const key = Object.keys(data).find(k => k.toLowerCase() === companyName.toLowerCase());
          interviews = key ? data[key] : null;
        }
        console.log('[loadInterviewsData] Interviews for company:', interviews);
        setManagementInterviews(interviews || null);
      })
      .catch((error) => {
        console.error('[loadInterviewsData] Error:', error);
        setManagementInterviews(null);
      });
  };

  useEffect(() => {
    loadCompanyData();
    loadNewsData();
    loadInterviewsData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [companyName]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse text-neutral-400">Loading...</div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <p className="text-neutral-500">Company not found</p>
        <Link href="/jobs">
          <Button variant="outline">Back to Companies</Button>
        </Link>
      </div>
    );
  }

  const tabs = [
    { id: "jobs", label: "Jobs" },
    { id: "tech", label: "Tech Stack" },
    { id: "company_news", label: "Company News" },
    { id: "management_interviews", label: "Management Interviews" },
  ] as const;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-white sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-2.5">
          {/* Back button */}
          <Link href="/jobs" className="inline-flex items-center gap-1 text-xs text-neutral-500 hover:text-neutral-700 mb-2">
            <ArrowLeft className="w-3 h-3" />
            Back to Companies
          </Link>
          
          {/* Company info */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-neutral-500" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-neutral-900">{company.name}</h1>
              <div className="flex items-center gap-1.5 mt-1">
                <Badge variant="secondary" className="text-[10px] h-5 px-2">{company.industry}</Badge>
                <span className="text-neutral-300">•</span>
                <span className="text-xs text-neutral-500">{company.employees} employees</span>
                {company.website && (
                  <>
                    <span className="text-neutral-300">•</span>
                    <a 
                      href={company.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-[10px] text-neutral-600 hover:text-neutral-900 flex items-center gap-1 transition-colors"
                    >
                      <Globe className="w-3 h-3" />
                      Website
                    </a>
                  </>
                )}
                <span className="text-neutral-300">•</span>
                <a 
                  href={`https://www.linkedin.com/company/${company.name.toLowerCase().replace(/\s+/g, '-')}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-[10px] text-neutral-600 hover:text-neutral-900 flex items-center gap-1 transition-colors"
                >
                  <Linkedin className="w-3 h-3" />
                  LinkedIn
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs - footer of header, custom bar */}
        <div className="max-w-7xl mx-auto px-6 pb-1">
          <div className="flex items-center gap-5 text-xs border-b border-neutral-200">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "pb-1.5 -mb-[1px] border-b-2 transition-colors text-[12px]",
                    isActive
                      ? "border-violet-500 text-violet-700 font-semibold"
                      : "border-transparent text-neutral-500 hover:text-neutral-800 font-medium"
                  )}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        {activeTab === "jobs" && <OverviewTab company={company} />}
        {activeTab === "tech" && <TechStackTab company={company} />}
        {activeTab === "company_news" && <NewsTab company={company} companyNews={companyNews} onRefreshComplete={() => {
          console.log('[Page] Refresh complete callback triggered for news');
          loadNewsData();
        }} />}
        {activeTab === "management_interviews" && (
            <ManagementInterviewsTab
              items={managementInterviews?.management_items || []}
              companyName={company.name}
              executives={managementInterviews?.key_executives_identified}
              searchDate={managementInterviews?.search_date}
              onRefreshComplete={() => {
                console.log('[Page] Refresh complete callback triggered for interviews');
                loadInterviewsData();
              }}
            />
        )}
      </div>
    </div>
  );
}

