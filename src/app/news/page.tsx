"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getNewsData, getManagementInterviewsData, getData } from "@/lib/data";
import { NewsDataStore, ManagementInterviewsDataStore, NewsItem, ManagementInterviewItem, DataStore } from "@/lib/types";
import { NewsCard } from "@/components/company/NewsCard";
import { ManagementInterviewCard } from "@/components/company/ManagementInterviewCard";
import { NewsDetailModal } from "@/components/company/NewsDetailModal";
import { ManagementInterviewDetailModal } from "@/components/company/ManagementInterviewDetailModal";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Building2, Newspaper, MessageSquare, ChevronDown, ChevronLeft, ChevronRight, Search, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

type FeedItemType = 
  | { type: "news"; companyName: string; data: NewsItem }
  | { type: "interview"; companyName: string; data: ManagementInterviewItem };

export default function NewsPage() {
  const [newsData, setNewsData] = useState<NewsDataStore | null>(null);
  const [interviewsData, setInterviewsData] = useState<ManagementInterviewsDataStore | null>(null);
  const [companiesData, setCompaniesData] = useState<DataStore | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<FeedItemType | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set(["all"]));
  const [currentPage, setCurrentPage] = useState(1);
  const [showOnlyTier0, setShowOnlyTier0] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const ITEMS_PER_PAGE = 20;

  useEffect(() => {
    Promise.all([
      getNewsData(),
      getManagementInterviewsData(),
      getData()
    ])
      .then(([news, interviews, companies]) => {
        setNewsData(news);
        setInterviewsData(interviews);
        setCompaniesData(companies);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error loading data:", error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse text-neutral-400">Loading...</div>
      </div>
    );
  }

  // Define Tier 0 companies list first
  const tier0Companies = ["Costco", "Target", "Home Depot", "Lowe's", "La-Z-Boy", "Pottery Barn", "Williams Sonoma", "West Elm", "California Closets"];

  // Combine news and interviews into a single feed - Only from Tier 0 companies
  const feedItems: FeedItemType[] = [];

  if (newsData) {
    Object.entries(newsData).forEach(([companyName, companyNews]) => {
      // Only include Tier 0 companies
      if (tier0Companies.includes(companyName) && companyNews.news_items && companyNews.news_items.length > 0) {
        companyNews.news_items.forEach((newsItem) => {
          feedItems.push({
            type: "news",
            companyName,
            data: newsItem,
          });
        });
      }
    });
  }

  if (interviewsData) {
    Object.entries(interviewsData).forEach(([companyName, companyInterviews]) => {
      // Only include Tier 0 companies
      if (tier0Companies.includes(companyName) && companyInterviews.management_items && companyInterviews.management_items.length > 0) {
        companyInterviews.management_items.forEach((interview) => {
          feedItems.push({
            type: "interview",
            companyName,
            data: interview,
          });
        });
      }
    });
  }

  // Apply Tier 0 filter first
  let tier0FilteredItems = feedItems;
  if (showOnlyTier0) {
    tier0FilteredItems = feedItems.filter((item) => tier0Companies.includes(item.companyName));
  }

  // Apply search filter
  let searchFilteredItems = tier0FilteredItems;
  if (searchQuery.trim()) {
    const query = searchQuery.toLowerCase().trim();
    searchFilteredItems = tier0FilteredItems.filter((item) =>
      item.companyName.toLowerCase().includes(query)
    );
  }

  // Get category counts from search-filtered items
  const categoryCounts: Record<string, number> = {
    all: searchFilteredItems.length,
    news: searchFilteredItems.filter((item) => item.type === "news").length,
    interviews: searchFilteredItems.filter((item) => item.type === "interview").length,
  };

  // Filter items based on selected categories
  let filteredItems = searchFilteredItems;
  if (!selectedCategories.has("all")) {
    filteredItems = searchFilteredItems.filter((item) => {
      if (selectedCategories.has("news") && item.type === "news") return true;
      if (selectedCategories.has("interviews") && item.type === "interview") return true;
      return false;
    });
  }

  // Sort by date (most recent first)
  filteredItems.sort((a, b) => {
    const dateA = new Date(a.data.published_date || "2025-01-01").getTime();
    const dateB = new Date(b.data.published_date || "2025-01-01").getTime();
    return dateB - dateA;
  });

  // Pagination
  const totalPages = Math.ceil(filteredItems.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const paginatedItems = filteredItems.slice(startIndex, endIndex);

  // Calculate stats
  const totalCompanies = tier0Companies.length;

  // Handle category change
  const handleCategoryChange = (category: string) => {
    setSelectedCategories(prev => {
      const newSet = new Set(prev);
      
      if (category === "all") {
        return new Set(["all"]);
      }
      
      newSet.delete("all");
      
      if (newSet.has(category)) {
        newSet.delete(category);
        if (newSet.size === 0) {
          return new Set(["all"]);
        }
      } else {
        newSet.add(category);
      }
      
      return newSet;
    });
    setCurrentPage(1); // Reset to page 1 when filter changes
  };

  // Handle Tier 0 filter change
  const handleTier0FilterChange = () => {
    setShowOnlyTier0(prev => !prev);
    setCurrentPage(1);
  };

  // Handle search change
  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setCurrentPage(1);
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-6 py-2.5">
          <div className="flex items-center justify-between min-h-[52px]">
            <div>
              <h1 className="text-base font-semibold text-neutral-900">News</h1>
              <p className="text-xs text-neutral-500 mt-0.5">
                {filteredItems.length} articles · {totalCompanies} companies
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters Header - Fixed */}
      <div style={{ backgroundColor: '#FBFAF9' }}>
        <div className="max-w-3xl mx-auto py-3">
          <div className="flex items-center justify-between">
          {/* Left: Stats */}
          <div className="flex items-center gap-1.5">
            <Newspaper className="w-3.5 h-3.5 text-neutral-400" />
            <span className="text-xs font-medium text-neutral-700">
              {filteredItems.length} articles
            </span>
          </div>

          {/* Right: Filters */}
          <div className="flex items-center gap-2">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-neutral-400" />
              <Input
                type="text"
                placeholder="Search companies..."
                value={searchQuery}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="h-[26px] pl-7 pr-7 text-[10px] md:text-[10px] font-medium w-40 border-neutral-200 text-neutral-600 placeholder:text-neutral-400 placeholder:font-medium bg-white"
              />
              {searchQuery && (
                <button
                  onClick={() => handleSearchChange("")}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            {/* Tier 0 Filter */}
            <button
              onClick={handleTier0FilterChange}
              className={cn(
                "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
                showOnlyTier0
                  ? "bg-green-100 text-green-700 border-green-300"
                  : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
              )}
            >
              Tier 0 Only
              {showOnlyTier0 && (
                <span className="text-green-600 font-semibold">✓</span>
              )}
            </button>

            {/* Category Filter */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={cn(
                  "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
                  !selectedCategories.has("all")
                    ? "bg-violet-100 text-violet-700 border-violet-300"
                    : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
                )}>
                  Category
                  {!selectedCategories.has("all") && (
                    <span className="text-violet-600 font-semibold">
                      ({selectedCategories.size})
                    </span>
                  )}
                  <ChevronDown className="w-3 h-3 text-neutral-400" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {!selectedCategories.has("all") && (
                  <>
                    <button
                      onClick={() => setSelectedCategories(new Set(["all"]))}
                      className="w-full text-left px-2 py-1.5 text-xs text-violet-600 hover:text-violet-700 font-medium"
                    >
                      Clear filters
                    </button>
                    <DropdownMenuSeparator />
                  </>
                )}
                <DropdownMenuCheckboxItem
                  checked={selectedCategories.has("all")}
                  onCheckedChange={() => handleCategoryChange("all")}
                  onSelect={(e) => e.preventDefault()}
                  className="text-xs"
                >
                  All
                  <span className="ml-auto text-neutral-400">
                    ({categoryCounts.all})
                  </span>
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={selectedCategories.has("news")}
                  onCheckedChange={() => handleCategoryChange("news")}
                  onSelect={(e) => e.preventDefault()}
                  className="text-xs"
                >
                  Company News
                  <span className="ml-auto text-neutral-400">
                    ({categoryCounts.news})
                  </span>
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={selectedCategories.has("interviews")}
                  onCheckedChange={() => handleCategoryChange("interviews")}
                  onSelect={(e) => e.preventDefault()}
                  className="text-xs"
                >
                  Management Interviews
                  <span className="ml-auto text-neutral-400">
                    ({categoryCounts.interviews})
                  </span>
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
      </div>

      {/* Scrollable Content Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          {/* News Feed */}
          <div className="max-w-3xl mx-auto space-y-3">
          {paginatedItems.map((item, index) => (
            <div key={`${item.type}-${item.companyName}-${index}`}>
              {/* Company Name Header */}
              <Link 
                href={`/jobs/${encodeURIComponent(item.companyName)}`}
                className="flex items-center gap-1.5 mb-1.5 hover:opacity-70 transition-opacity"
              >
                <div className="w-4 h-4 rounded bg-neutral-100 flex items-center justify-center">
                  <Building2 className="w-2.5 h-2.5 text-neutral-500" />
                </div>
                <span className="text-[11px] font-medium text-neutral-700">{item.companyName}</span>
                {tier0Companies.includes(item.companyName) && (
                  <Badge variant="secondary" className="font-normal text-[9px] h-4 bg-green-100 text-green-700 hover:bg-green-100">
                    Tier 0
                  </Badge>
                )}
              </Link>

              {/* Card */}
              {item.type === "news" ? (
                <NewsCard
                  news={item.data as NewsItem}
                  onClick={() => setSelectedItem(item)}
                />
              ) : (
                <ManagementInterviewCard
                  item={item.data as ManagementInterviewItem}
                  onClick={() => setSelectedItem(item)}
                />
              )}
            </div>
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-neutral-200">
            <div className="text-xs text-neutral-500">
              Showing {startIndex + 1}-{Math.min(endIndex, filteredItems.length)} of {filteredItems.length} articles
            </div>
            
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="h-7 w-7 p-0"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </Button>
              <div className="flex items-center gap-0.5">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                  // Show first page, last page, current page, and pages around current
                  if (
                    page === 1 ||
                    page === totalPages ||
                    (page >= currentPage - 1 && page <= currentPage + 1)
                  ) {
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={cn(
                          "h-7 w-7 rounded-md text-xs font-medium transition-colors",
                          currentPage === page
                            ? "bg-violet-100 text-violet-700"
                            : "text-neutral-600 hover:bg-neutral-100"
                        )}
                      >
                        {page}
                      </button>
                    );
                  } else if (page === currentPage - 2 || page === currentPage + 2) {
                    return (
                      <span key={page} className="text-neutral-400 text-xs px-1">
                        ...
                      </span>
                    );
                  }
                  return null;
                })}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="h-7 w-7 p-0"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        )}

        {/* End of max-w-7xl container */}
        </div>
      </div>

      {/* Modals */}
      {selectedItem && selectedItem.type === "news" && (
        <NewsDetailModal
          news={selectedItem.data as NewsItem}
          isOpen={true}
          onClose={() => setSelectedItem(null)}
        />
      )}

      {selectedItem && selectedItem.type === "interview" && (
        <ManagementInterviewDetailModal
          interview={selectedItem.data as ManagementInterviewItem}
          isOpen={true}
          onClose={() => setSelectedItem(null)}
        />
      )}
    </div>
  );
}

