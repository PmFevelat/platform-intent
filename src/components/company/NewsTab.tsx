"use client";

import { useState } from "react";
import { Company, CompanyNews, NewsItem } from "@/lib/types";
import { 
  Newspaper,
  TrendingUp,
  Sparkles,
  AlertCircle,
  ChevronDown
} from "lucide-react";
import { cn } from "@/lib/utils";
import { NewsCard } from "@/components/company/NewsCard";
import { NewsDetailModal } from "@/components/company/NewsDetailModal";
import { RefreshDataButton } from "@/components/company/RefreshDataButton";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

interface NewsTabProps {
  company: Company;
  companyNews: CompanyNews | null;
  onRefreshComplete?: () => void;
}

export function NewsTab({ company, companyNews, onRefreshComplete }: NewsTabProps) {
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set(["All"]));
  const [selectedDateFilters, setSelectedDateFilters] = useState<Set<string>>(new Set(["All time"]));

  // ⚠️ HARD FILTER: Remove all news older than 2020
  const allNewsItems = companyNews?.news_items || [];
  const newsItems = allNewsItems
    .filter(item => {
      const itemDate = new Date(item.published_date);
      const itemYear = itemDate.getFullYear();
      return !isNaN(itemYear) && itemYear >= 2020; // Only 2020, 2021, 2022, 2023, 2024
    })
    .sort((a, b) => {
      // Sort by date (newest first)
      const dateA = new Date(a.published_date).getTime();
      const dateB = new Date(b.published_date).getTime();
      return dateB - dateA;
    });

  // Available categories with labels and priority
  const categoryLabels: Record<string, string> = {
    all: "All",
    // High priority signals (🔥)
    digital_transformation: "Digital Transformation",
    catalog_expansion: "Catalog Expansion",
    ecommerce_growth: "E-commerce Growth",
    visual_content_strategy: "Visual Strategy",
    supply_chain_challenges: "Supply Chain",
    international_expansion: "International",
    time_to_market: "Time-to-Market",
    large_catalog_operations: "Large Catalog",
    // Medium priority signals (💡)
    omnichannel_strategy: "Omnichannel",
    product_customization: "Customization",
    private_label: "Private Label",
    technology_innovation: "Tech Innovation",
    product_innovation: "Product Innovation",
    sustainability_initiative: "Sustainability",
    partnership: "Partnership",
    // Supporting signals (🔍)
    cost_optimization: "Cost Optimization",
    merger_acquisition: "M&A",
    platform_migration: "Platform Migration",
    marketing_campaigns: "Marketing",
    ai_adoption: "AI Adoption",
    // Other
    visual_content: "Visual Content",
    ai_investment: "AI Investment",
    hiring: "Hiring",
  };

  // Calculate news age in days
  const getNewsAge = (dateString: string): number => {
    if (!dateString || dateString === "Invalid Date") return Infinity;
    const newsDate = new Date(dateString);
    if (isNaN(newsDate.getTime())) return Infinity;
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - newsDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // Date filter options - granular + yearly
  const dateFilterOptions = [
    { label: "All time", type: "all" as const, value: null },
    { label: "Last 7 days", type: "days" as const, value: 7 },
    { label: "Last 30 days", type: "days" as const, value: 30 },
    { label: "Last 3 months", type: "days" as const, value: 90 },
    { label: "Last 6 months", type: "days" as const, value: 180 },
    { label: "Last year", type: "days" as const, value: 365 },
    { label: "2024", type: "year" as const, value: 2024 },
    { label: "2023", type: "year" as const, value: 2023 },
    { label: "2022", type: "year" as const, value: 2022 },
    { label: "2021", type: "year" as const, value: 2021 },
    { label: "2020", type: "year" as const, value: 2020 },
  ];

  // Apply date filter first
  let dateFilteredNews = newsItems;
  
  if (!selectedDateFilters.has("All time")) {
    dateFilteredNews = newsItems.filter(news => {
      const newsAge = getNewsAge(news.published_date);
      const newsDate = new Date(news.published_date);
      const newsYear = newsDate.getFullYear();
      
      // Check if news matches any selected filter
      return Array.from(selectedDateFilters).some(filterLabel => {
        const option = dateFilterOptions.find(opt => opt.label === filterLabel);
        if (!option) return false;
        
        if (option.type === "days") {
          return newsAge <= option.value!;
        } else if (option.type === "year") {
          return newsYear === option.value;
        }
        return false;
      });
    });
  }

  // Count news for each date filter
  const dateFilterCounts: Record<string, number> = {};
  dateFilterOptions.forEach(option => {
    if (option.type === "all") {
      dateFilterCounts[option.label] = newsItems.length;
    } else if (option.type === "days") {
      dateFilterCounts[option.label] = newsItems.filter(news => 
        getNewsAge(news.published_date) <= option.value!
      ).length;
    } else if (option.type === "year") {
      dateFilterCounts[option.label] = newsItems.filter(news => {
        const newsDate = new Date(news.published_date);
        return newsDate.getFullYear() === option.value;
      }).length;
    }
  });

  // Get category counts from date-filtered news
  const categoryCounts: Record<string, number> = { "All": dateFilteredNews.length };
  dateFilteredNews.forEach(news => {
    categoryCounts[news.category] = (categoryCounts[news.category] || 0) + 1;
  });

  // Get available categories sorted by count
  const categories = Array.from(new Set(dateFilteredNews.map(item => item.category)))
    .sort((a, b) => categoryCounts[b] - categoryCounts[a]);

  // Apply category filter
  let filteredNews = dateFilteredNews;
  if (!selectedCategories.has("All")) {
    filteredNews = dateFilteredNews.filter(news => selectedCategories.has(news.category));
  }

  // Sort by date (newest first) - CRITICAL for proper display order
  filteredNews = filteredNews.sort((a, b) => {
    const dateA = new Date(a.published_date).getTime();
    const dateB = new Date(b.published_date).getTime();
    return dateB - dateA; // Descending order: newest first
  });

  // Handle category change
  const handleCategoryChange = (category: string) => {
    setSelectedCategories(prev => {
      const newSet = new Set(prev);
      
      if (category === "All") {
        return new Set(["All"]);
      }
      
      newSet.delete("All");
      
      if (newSet.has(category)) {
        newSet.delete(category);
        if (newSet.size === 0) {
          return new Set(["All"]);
        }
      } else {
        newSet.add(category);
      }
      
      return newSet;
    });
  };

  // Handle date filter change
  const handleDateFilterChange = (dateFilter: string) => {
    setSelectedDateFilters(prev => {
      const newSet = new Set(prev);
      
      if (dateFilter === "All time") {
        return new Set(["All time"]);
      }
      
      newSet.delete("All time");
      
      if (newSet.has(dateFilter)) {
        newSet.delete(dateFilter);
        if (newSet.size === 0) {
          return new Set(["All time"]);
        }
      } else {
        newSet.add(dateFilter);
      }
      
      return newSet;
    });
  };

  if (newsItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3">
        <div className="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center">
          <Newspaper className="w-6 h-6 text-neutral-400" />
        </div>
        <div className="text-center">
          <h3 className="text-sm font-semibold text-neutral-900 mb-1">
            No news available
          </h3>
          <p className="text-xs text-neutral-500 max-w-md">
            News for this company haven&apos;t been collected yet. 
            Run the scraping script to fetch the latest news.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4 h-[calc(100vh-240px)]">
      {/* Left/Center: News Cards - Scrollable Container */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Filters and Stats Header */}
        <div className="flex items-center justify-between mb-3 flex-shrink-0">
          {/* Left: Stats & Refresh */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <Newspaper className="w-3.5 h-3.5 text-neutral-400" />
              <span className="text-xs font-medium text-neutral-700">
                {filteredNews.length} news
              </span>
              {companyNews?.search_date && (
                <>
                  <span className="text-neutral-300">•</span>
                  <span className="text-[10px] text-neutral-500">
                    Updated: {new Date(companyNews.search_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </>
              )}
            </div>
            
            {/* Refresh Data Button */}
            <RefreshDataButton 
              companyName={company.name}
              dataType="news"
              onRefreshComplete={onRefreshComplete}
            />
          </div>

          {/* Right: Filters */}
          <div className="flex items-center gap-2">
            {/* Date Filters - Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={cn(
                  "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
                  !selectedDateFilters.has("All time")
                    ? "bg-blue-100 text-blue-700 border-blue-300"
                    : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
                )}>
                  Time Period
                  {!selectedDateFilters.has("All time") && (
                    <span className="text-blue-600 font-semibold">
                      ({selectedDateFilters.size})
                    </span>
                  )}
                  <ChevronDown className="w-3 h-3 text-neutral-400" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {!selectedDateFilters.has("All time") && (
                  <>
                    <button
                      onClick={() => setSelectedDateFilters(new Set(["All time"]))}
                      className="w-full text-left px-2 py-1.5 text-xs text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Clear filters
                    </button>
                    <DropdownMenuSeparator />
                  </>
                )}
                {dateFilterOptions.map((option) => (
                  <DropdownMenuCheckboxItem
                    key={option.label}
                    checked={selectedDateFilters.has(option.label)}
                    onCheckedChange={() => handleDateFilterChange(option.label)}
                    onSelect={(e) => e.preventDefault()}
                    className="text-xs"
                  >
                    {option.label}
                    <span className="ml-auto text-neutral-400">
                      ({dateFilterCounts[option.label]})
                    </span>
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Category Filters - Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={cn(
                  "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
                  !selectedCategories.has("All")
                    ? "bg-violet-100 text-violet-700 border-violet-300"
                    : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
                )}>
                  Categories
                  {!selectedCategories.has("All") && (
                    <span className="text-violet-600 font-semibold">
                      ({selectedCategories.size})
                    </span>
                  )}
                  <ChevronDown className="w-3 h-3 text-neutral-400" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {!selectedCategories.has("All") && (
                  <>
                    <button
                      onClick={() => setSelectedCategories(new Set(["All"]))}
                      className="w-full text-left px-2 py-1.5 text-xs text-violet-600 hover:text-violet-700 font-medium"
                    >
                      Clear filters
                    </button>
                    <DropdownMenuSeparator />
                  </>
                )}
                <DropdownMenuCheckboxItem
                  checked={selectedCategories.has("All")}
                  onCheckedChange={() => handleCategoryChange("All")}
                  onSelect={(e) => e.preventDefault()}
                  className="text-xs"
                >
                  All
                  <span className="ml-auto text-neutral-400">
                    ({categoryCounts["All"]})
                  </span>
                </DropdownMenuCheckboxItem>
                {categories.map((category) => (
                  <DropdownMenuCheckboxItem
                    key={category}
                    checked={selectedCategories.has(category)}
                    onCheckedChange={() => handleCategoryChange(category)}
                    onSelect={(e) => e.preventDefault()}
                    className="text-xs"
                  >
                    {categoryLabels[category] || category.replace(/_/g, " ")}
                    <span className="ml-auto text-neutral-400">
                      ({categoryCounts[category] || 0})
                    </span>
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* News Grid - Scrollable Area */}
        <div className="flex-1 overflow-y-auto pr-2">
          <div className="grid grid-cols-1 gap-3">
            {filteredNews.map((news, idx) => (
              <NewsCard 
                key={idx} 
                news={news} 
                onClick={() => setSelectedNews(news)}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Right: Overall Assessment Panel - Fixed */}
      {companyNews?.overall_assessment && (
        <div className="w-72 flex-shrink-0">
          <div className="bg-white border border-neutral-200 rounded-lg p-3 h-fit">
              {/* Header with Score */}
              <div className="flex items-center justify-between mb-2.5">
                <div className="flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-violet-600" />
                  <h3 className="text-xs font-semibold text-neutral-900">Assessment</h3>
                </div>
                <div className={cn(
                  "px-2 py-0.5 rounded-full text-xs font-bold border",
                  companyNews.overall_assessment.presti_fit_score >= 8 
                    ? "bg-green-50 text-green-700 border-green-200"
                    : companyNews.overall_assessment.presti_fit_score >= 6
                    ? "bg-amber-50 text-amber-700 border-amber-200"
                    : "bg-neutral-100 text-neutral-600 border-neutral-200"
                )}>
                  {companyNews.overall_assessment.presti_fit_score}/10
                </div>
              </div>

              {/* Recommended Approach */}
              <div className="mb-2.5">
                <p className="text-[10px] text-neutral-600 leading-relaxed">
                  {companyNews.overall_assessment.recommended_approach}
                </p>
              </div>

              {/* Key Opportunities */}
              {companyNews.overall_assessment.key_opportunities.length > 0 && (
                <div>
                  <h4 className="text-[10px] font-semibold text-neutral-700 mb-1.5">Key Opportunities</h4>
                  <ul className="space-y-1">
                    {companyNews.overall_assessment.key_opportunities.map((opp, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-violet-600 mt-0.5 text-[10px]">•</span>
                        <span className="text-[10px] text-neutral-700 leading-relaxed flex-1">{opp}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
      )}

      {/* News Detail Modal */}
      <NewsDetailModal 
        news={selectedNews}
        isOpen={!!selectedNews}
        onClose={() => setSelectedNews(null)}
      />
    </div>
  );
}

