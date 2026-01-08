"use client";

import { useState, useMemo } from "react";
import { ManagementInterviewItem, KeyExecutive } from "@/lib/types";
import { ManagementInterviewCard } from "./ManagementInterviewCard";
import { ManagementInterviewDetailModal } from "./ManagementInterviewDetailModal";
import { RefreshDataButton } from "./RefreshDataButton";
import { 
  MessageSquare,
  ChevronDown,
  Users
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

interface ManagementInterviewsTabProps {
  items: ManagementInterviewItem[];
  companyName: string;
  executives?: KeyExecutive[];
  searchDate?: string;
  onRefreshComplete?: () => void;
}

export function ManagementInterviewsTab({ items: rawItems, companyName, executives: providedExecutives, searchDate, onRefreshComplete }: ManagementInterviewsTabProps) {
  console.log('[ManagementInterviewsTab] Rendering with:', {
    rawItemsCount: rawItems.length,
    companyName,
    executivesCount: providedExecutives?.length,
    searchDate
  });

  // ⚠️ HARD FILTER: Remove all items older than 2020 and sort by date
  const items = rawItems
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

  console.log('[ManagementInterviewsTab] After 2020 filter:', items.length, 'items');

  // Generate executives list from items if not provided
  const executives = useMemo(() => {
    if (providedExecutives && providedExecutives.length > 0) {
      return providedExecutives;
    }
    
    // Generate from items
    const executiveMap = new Map<string, { name: string; title: string; content_count: number }>();
    
    items.forEach(item => {
      if (item.executive_name) {
        const existing = executiveMap.get(item.executive_name);
        if (existing) {
          existing.content_count += 1;
        } else {
          executiveMap.set(item.executive_name, {
            name: item.executive_name,
            title: item.executive_title || '',
            content_count: 1,
          });
        }
      }
    });
    
    // Sort by content_count (descending)
    return Array.from(executiveMap.values()).sort((a, b) => b.content_count - a.content_count);
  }, [providedExecutives, items]);

  const [selectedFormats, setSelectedFormats] = useState<Set<string>>(new Set(["All"]));
  const [selectedDateFilters, setSelectedDateFilters] = useState<Set<string>>(new Set(["All time"]));
  const [selectedInterview, setSelectedInterview] = useState<ManagementInterviewItem | null>(null);

  // Format labels
  const formatLabels: Record<string, string> = {
    interview: "Interview",
    podcast: "Podcast",
    keynote: "Keynote",
    article: "Article",
    panel: "Panel",
    LinkedIn_post: "LinkedIn",
    webinar: "Webinar",
    profile: "Profile",
  };

  // Calculate interview age in days
  const getInterviewAge = (dateString: string): number => {
    if (!dateString || dateString === "Invalid Date") return Infinity;
    const interviewDate = new Date(dateString);
    if (isNaN(interviewDate.getTime())) return Infinity;
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - interviewDate.getTime());
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
  let dateFilteredInterviews = items;
  
  if (!selectedDateFilters.has("All time")) {
    dateFilteredInterviews = items.filter(interview => {
      const interviewAge = getInterviewAge(interview.published_date);
      const interviewDate = new Date(interview.published_date);
      const interviewYear = interviewDate.getFullYear();
      
      // Check if interview matches any selected filter
      return Array.from(selectedDateFilters).some(filterLabel => {
        const option = dateFilterOptions.find(opt => opt.label === filterLabel);
        if (!option) return false;
        
        if (option.type === "days") {
          return interviewAge <= option.value!;
        } else if (option.type === "year") {
          return interviewYear === option.value;
        }
        return false;
      });
    });
  }

  // Count interviews for each date filter
  const dateFilterCounts: Record<string, number> = {};
  dateFilterOptions.forEach(option => {
    if (option.type === "all") {
      dateFilterCounts[option.label] = items.length;
    } else if (option.type === "days") {
      dateFilterCounts[option.label] = items.filter(interview => 
        getInterviewAge(interview.published_date) <= option.value!
      ).length;
    } else if (option.type === "year") {
      dateFilterCounts[option.label] = items.filter(interview => {
        const interviewDate = new Date(interview.published_date);
        return interviewDate.getFullYear() === option.value;
      }).length;
    }
  });

  // Get format counts from date-filtered interviews
  const formatCounts: Record<string, number> = { "All": dateFilteredInterviews.length };
  dateFilteredInterviews.forEach(interview => {
    formatCounts[interview.format] = (formatCounts[interview.format] || 0) + 1;
  });

  // Get available formats sorted by count
  const formats = Array.from(new Set(dateFilteredInterviews.map(item => item.format)))
    .sort((a, b) => formatCounts[b] - formatCounts[a]);

  // Apply format filter
  let filteredInterviews = dateFilteredInterviews;
  if (!selectedFormats.has("All")) {
    filteredInterviews = dateFilteredInterviews.filter(interview => selectedFormats.has(interview.format));
  }

  // Sort by date (newest first) - CRITICAL for proper display order
  filteredInterviews = filteredInterviews.sort((a, b) => {
    const dateA = new Date(a.published_date).getTime();
    const dateB = new Date(b.published_date).getTime();
    return dateB - dateA; // Descending order: newest first
  });

  // Handle format change
  const handleFormatChange = (format: string) => {
    setSelectedFormats(prev => {
      const newSet = new Set(prev);
      
      if (format === "All") {
        return new Set(["All"]);
      }
      
      newSet.delete("All");
      
      if (newSet.has(format)) {
        newSet.delete(format);
        if (newSet.size === 0) {
          return new Set(["All"]);
        }
      } else {
        newSet.add(format);
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

  return (
    <div className="flex gap-4 h-[calc(100vh-240px)]">
      {/* Left/Center: Interview Cards - Scrollable Container */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Filters and Stats Header */}
        <div className="flex items-center justify-between mb-3 flex-shrink-0">
          {/* Left: Stats & Refresh */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <MessageSquare className="w-3.5 h-3.5 text-neutral-400" />
              <span className="text-xs font-medium text-neutral-700">
                {filteredInterviews.length} interviews
              </span>
              {searchDate && (
                <>
                  <span className="text-neutral-300">•</span>
                  <span className="text-[10px] text-neutral-500">
                    Updated: {new Date(searchDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </>
              )}
            </div>
            
            {/* Refresh Data Button */}
            <RefreshDataButton 
              companyName={companyName}
              dataType="interviews"
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

            {/* Format Filters - Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={cn(
                  "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
                  !selectedFormats.has("All")
                    ? "bg-violet-100 text-violet-700 border-violet-300"
                    : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
                )}>
                  Format
                  {!selectedFormats.has("All") && (
                    <span className="text-violet-600 font-semibold">
                      ({selectedFormats.size})
                    </span>
                  )}
                  <ChevronDown className="w-3 h-3 text-neutral-400" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {!selectedFormats.has("All") && (
                  <>
                    <button
                      onClick={() => setSelectedFormats(new Set(["All"]))}
                      className="w-full text-left px-2 py-1.5 text-xs text-violet-600 hover:text-violet-700 font-medium"
                    >
                      Clear filters
                    </button>
                    <DropdownMenuSeparator />
                  </>
                )}
                <DropdownMenuCheckboxItem
                  checked={selectedFormats.has("All")}
                  onCheckedChange={() => handleFormatChange("All")}
                  onSelect={(e) => e.preventDefault()}
                  className="text-xs"
                >
                  All
                  <span className="ml-auto text-neutral-400">
                    ({formatCounts["All"]})
                  </span>
                </DropdownMenuCheckboxItem>
                {formats.map((format) => (
                  <DropdownMenuCheckboxItem
                    key={format}
                    checked={selectedFormats.has(format)}
                    onCheckedChange={() => handleFormatChange(format)}
                    onSelect={(e) => e.preventDefault()}
                    className="text-xs"
                  >
                    {formatLabels[format] || format}
                    <span className="ml-auto text-neutral-400">
                      ({formatCounts[format] || 0})
                    </span>
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Interviews Grid - Scrollable Area */}
        <div className="flex-1 overflow-y-auto pr-2">
          {filteredInterviews.length > 0 ? (
            <div className="grid grid-cols-1 gap-3">
              {filteredInterviews.map((interview, idx) => (
                <ManagementInterviewCard 
                  key={idx} 
                  item={interview} 
                  onClick={() => setSelectedInterview(interview)}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <div className="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-neutral-400" />
              </div>
              <div className="text-center">
                <h3 className="text-sm font-semibold text-neutral-900 mb-1">
                  No management interviews available
                </h3>
                <p className="text-xs text-neutral-500 max-w-md">
                  {items.length === 0 
                    ? "Click the 'Refresh' button above to search for executive interviews and insights." 
                    : "No interviews match your current filters. Try adjusting the time period or format."}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right: Key Executives Panel - Fixed */}
      {executives && executives.length > 0 && (
        <div className="w-72 flex-shrink-0">
          <div className="bg-white border border-neutral-200 rounded-lg p-3">
            <div className="flex items-center gap-1.5 mb-2.5">
              <Users className="w-3.5 h-3.5 text-violet-600" />
              <h3 className="text-xs font-semibold text-neutral-900">Key Executives</h3>
            </div>
            <div className="space-y-2">
              {executives.slice(0, 5).map((exec, idx) => (
                <div key={idx} className="text-xs">
                  <div className="font-medium text-neutral-900">{exec.name}</div>
                  <div className="text-[10px] text-neutral-600">{exec.title}</div>
                  <div className="text-[9px] text-violet-600 mt-0.5">
                    {exec.content_count} {exec.content_count === 1 ? 'interview' : 'interviews'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Interview Detail Modal */}
      <ManagementInterviewDetailModal 
        interview={selectedInterview}
        isOpen={!!selectedInterview}
        onClose={() => setSelectedInterview(null)}
      />
    </div>
  );
}

