"use client";

import { useState } from "react";
import { Company, FinancialNews, FinancialItem } from "@/lib/types";
import { 
  TrendingUp,
  ChevronDown
} from "lucide-react";
import { cn } from "@/lib/utils";
import { FinancialNewsCard } from "@/components/company/FinancialNewsCard";
import { FinancialNewsDetailModal } from "@/components/company/FinancialNewsDetailModal";
import { RefreshDataButton } from "@/components/company/RefreshDataButton";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

interface FinancialNewsTabProps {
  company: Company;
  financialNews: FinancialNews | null;
  onRefreshComplete?: () => void;
}

export function FinancialNewsTab({ company, financialNews, onRefreshComplete }: FinancialNewsTabProps) {
  const [selectedItem, setSelectedItem] = useState<FinancialItem | null>(null);
  const [selectedDocTypes, setSelectedDocTypes] = useState<Set<string>>(new Set(["All"]));
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set(["All"]));

  const allFinancialItems = financialNews?.financial_items || [];
  const financialItems = allFinancialItems
    .filter(item => {
      const itemDate = new Date(item.published_date);
      const itemYear = itemDate.getFullYear();
      return !isNaN(itemYear) && itemYear >= 2020; // Only 2020+
    })
    .sort((a, b) => {
      const dateA = new Date(a.published_date).getTime();
      const dateB = new Date(b.published_date).getTime();
      return dateB - dateA;
    });

  // Document type labels
  const docTypeLabels: Record<string, string> = {
    all: "All",
    earnings_call: "Earnings Calls",
    sec_filing: "SEC Filings",
    quarterly_results: "Quarterly Results",
    press_release: "Press Releases",
    analyst_report: "Analyst Reports"
  };

  // Category labels
  const categoryLabels: Record<string, string> = {
    all: "All",
    earnings: "Earnings",
    financial_performance: "Financial Performance",
    guidance: "Guidance",
    sec_filing: "SEC Filing",
    analyst_coverage: "Analyst Coverage"
  };

  // Apply document type filter
  let docTypeFilteredItems = financialItems;
  if (!selectedDocTypes.has("All")) {
    docTypeFilteredItems = financialItems.filter(item => 
      selectedDocTypes.has(item.document_type)
    );
  }

  // Get category counts from doc-type-filtered items
  const categoryCounts: Record<string, number> = { "All": docTypeFilteredItems.length };
  docTypeFilteredItems.forEach(item => {
    categoryCounts[item.category] = (categoryCounts[item.category] || 0) + 1;
  });

  // Apply category filter
  let filteredItems = docTypeFilteredItems;
  if (!selectedCategories.has("All")) {
    filteredItems = docTypeFilteredItems.filter(item => 
      selectedCategories.has(item.category)
    );
  }

  // Get available document types and categories
  const docTypes = Array.from(new Set(financialItems.map(item => item.document_type)));
  const categories = Array.from(new Set(docTypeFilteredItems.map(item => item.category)));

  // Get doc type counts
  const docTypeCounts: Record<string, number> = { "All": financialItems.length };
  financialItems.forEach(item => {
    docTypeCounts[item.document_type] = (docTypeCounts[item.document_type] || 0) + 1;
  });

  // Handle document type change
  const handleDocTypeChange = (docType: string) => {
    setSelectedDocTypes(prev => {
      const newSet = new Set(prev);
      
      if (docType === "All") {
        return new Set(["All"]);
      }
      
      newSet.delete("All");
      
      if (newSet.has(docType)) {
        newSet.delete(docType);
        if (newSet.size === 0) {
          return new Set(["All"]);
        }
      } else {
        newSet.add(docType);
      }
      
      return newSet;
    });
  };

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

  if (financialItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3">
        <div className="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center">
          <TrendingUp className="w-6 h-6 text-neutral-400" />
        </div>
        <div className="text-center">
          <h3 className="text-sm font-semibold text-neutral-900 mb-1">
            No financial data available
          </h3>
          <p className="text-xs text-neutral-500 max-w-md">
            Financial data for this company hasn&apos;t been collected yet. 
            Run the scraping script to fetch the latest financial information.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4 h-[calc(100vh-240px)]">
      {/* Left/Center: Financial Cards - Scrollable Container */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Filters and Stats Header */}
        <div className="flex items-center justify-between mb-3 flex-shrink-0">
          {/* Left: Stats & Refresh */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-neutral-400" />
              <span className="text-xs font-medium text-neutral-700">
                {filteredItems.length} financial items
              </span>
              {financialNews?.search_date && (
                <>
                  <span className="text-neutral-300">•</span>
                  <span className="text-[10px] text-neutral-500">
                    Updated: {new Date(financialNews.search_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </>
              )}
            </div>
            
            {/* Refresh Data Button */}
            <RefreshDataButton 
              companyName={company.name}
              dataType="financial"
              onRefreshComplete={onRefreshComplete}
            />
          </div>

          {/* Right: Filters */}
          <div className="flex items-center gap-2">
            {/* Document Type Filter */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={cn(
                  "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
                  !selectedDocTypes.has("All")
                    ? "bg-blue-100 text-blue-700 border-blue-300"
                    : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
                )}>
                  Document Type
                  {!selectedDocTypes.has("All") && (
                    <span className="text-blue-600 font-semibold">
                      ({selectedDocTypes.size})
                    </span>
                  )}
                  <ChevronDown className="w-3 h-3 text-neutral-400" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {!selectedDocTypes.has("All") && (
                  <>
                    <button
                      onClick={() => setSelectedDocTypes(new Set(["All"]))}
                      className="w-full text-left px-2 py-1.5 text-xs text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Clear filters
                    </button>
                    <DropdownMenuSeparator />
                  </>
                )}
                <DropdownMenuCheckboxItem
                  checked={selectedDocTypes.has("All")}
                  onCheckedChange={() => handleDocTypeChange("All")}
                  onSelect={(e) => e.preventDefault()}
                  className="text-xs"
                >
                  All
                  <span className="ml-auto text-neutral-400">
                    ({docTypeCounts["All"]})
                  </span>
                </DropdownMenuCheckboxItem>
                {docTypes.map((docType) => (
                  <DropdownMenuCheckboxItem
                    key={docType}
                    checked={selectedDocTypes.has(docType)}
                    onCheckedChange={() => handleDocTypeChange(docType)}
                    onSelect={(e) => e.preventDefault()}
                    className="text-xs"
                  >
                    {docTypeLabels[docType] || docType}
                    <span className="ml-auto text-neutral-400">
                      ({docTypeCounts[docType] || 0})
                    </span>
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Category Filter */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={cn(
                  "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
                  !selectedCategories.has("All")
                    ? "bg-emerald-100 text-emerald-700 border-emerald-300"
                    : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
                )}>
                  Category
                  {!selectedCategories.has("All") && (
                    <span className="text-emerald-600 font-semibold">
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
                      className="w-full text-left px-2 py-1.5 text-xs text-emerald-600 hover:text-emerald-700 font-medium"
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
                    {categoryLabels[category] || category}
                    <span className="ml-auto text-neutral-400">
                      ({categoryCounts[category] || 0})
                    </span>
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Financial Items Grid - Scrollable Area */}
        <div className="flex-1 overflow-y-auto pr-2">
          <div className="grid grid-cols-1 gap-3">
            {filteredItems.map((item, idx) => (
              <FinancialNewsCard 
                key={idx} 
                item={item} 
                onClick={() => setSelectedItem(item)}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Financial Item Detail Modal */}
      <FinancialNewsDetailModal 
        item={selectedItem}
        isOpen={!!selectedItem}
        onClose={() => setSelectedItem(null)}
      />
    </div>
  );
}
