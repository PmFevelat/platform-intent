"use client";

import { useState } from "react";
import { Company, Job } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  LayoutGrid, 
  List, 
  ExternalLink,
  TrendingUp,
  ChevronLeft,
  ChevronRight,
  ChevronDown
} from "lucide-react";
import { cn } from "@/lib/utils";
import { JobDetailModal } from "./JobDetailModal";
import { HiringTrendsChart } from "./HiringTrendsChart";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

interface OverviewTabProps {
  company: Company;
}

// Categorize jobs with 6 main categories
function categorizeJob(jobTitle: string, description?: string): string {
  const title = jobTitle.toLowerCase();
  const text = `${jobTitle} ${description || ''}`.toLowerCase();
  
  // Leadership (priority - first to catch Directors/VPs before other categories)
  if (title.includes('director') || title.includes('vp') || title.includes('vice president') ||
      title.includes('chief') || title.includes('head of') || title.includes('president')) {
    return 'Leadership';
  }
  
  // Sales
  if (title.includes('sales') || title.includes('account manager') || title.includes('business development')) {
    return 'Sales';
  }
  
  // E-commerce
  if (text.includes('ecommerce') || text.includes('e-commerce') || 
      text.includes('digital commerce') || text.includes('online commerce')) {
    return 'E-commerce';
  }
  
  // Retail
  if (title.includes('retail') || title.includes('store') || title.includes('showroom') ||
      title.includes('merchandis') || title.includes('category manager')) {
    return 'Retail';
  }
  
  // Creative (includes design, content, production)
  if (title.includes('creative') || title.includes('design') || title.includes('art director') || 
      title.includes('graphic') || title.includes('visual designer') ||
      title.includes('content') || title.includes('production') ||
      title.includes('photo') || title.includes('video') ||
      title.includes('producer') || title.includes('3d')) {
    return 'Creative';
  }
  
  // Marketing (includes brand, digital marketing, growth)
  if (title.includes('marketing') || title.includes('brand') ||
      title.includes('growth') || title.includes('digital marketing') ||
      title.includes('performance marketing') || title.includes('sem') || title.includes('seo') ||
      title.includes('paid media') || title.includes('campaign')) {
    return 'Marketing';
  }
  
  return 'Other';
}

// Map job categories to chart categories (5 categories, excluding Leadership)
function mapToChartCategory(jobCategory: string): 'sales' | 'marketing' | 'ecommerce' | 'retail' | 'creative' | null {
  const categoryMap: Record<string, 'sales' | 'marketing' | 'ecommerce' | 'retail' | 'creative'> = {
    'Sales': 'sales',
    'Marketing': 'marketing',
    'E-commerce': 'ecommerce',
    'Retail': 'retail',
    'Creative': 'creative'
  };
  
  return categoryMap[jobCategory] || null;
}

// Get notes/badges for a job and extract AI-related snippets
function getJobNotes(job: Job): { label: string; color: string; snippet?: string }[] {
  const notes: { label: string; color: string; snippet?: string }[] = [];
  
  // AI-related check with strict pattern matching
  const title = job.job_title;
  const description = job.description || '';
  
  // Define strict AI-related patterns
  const aiPatterns = [
    /\bAI\b/i,                           // AI as a standalone word
    /\bA\.I\./i,                         // A.I. with dots
    /\bartificial intelligence\b/i,      // Artificial Intelligence
    /\bAI[\s-]tools?\b/i,                // AI tool, AI-tool, AI tools, AI-tools
    /\bAI[\s-]powered\b/i,               // AI powered, AI-powered
    /\bAI[\s-]driven\b/i,                // AI driven, AI-driven
    /\bAI[\s-]generated?\b/i,            // AI generate, AI-generate, AI generated
    /\bAI[\s-]generation\b/i,            // AI generation, AI-generation
    /\bAI[\s-]use\b/i,                   // AI use, AI-use
    /\bAI[\s-]based\b/i,                 // AI based, AI-based
    /\bAI[\s-]enabled\b/i,               // AI enabled, AI-enabled
    /\bgenerate with AI\b/i,             // generate with AI
    /\busing AI\b/i,                     // using AI
    /\bleverage AI\b/i,                  // leverage AI
    /\bAI solutions?\b/i,                // AI solution, AI solutions
    /\bAI technologies\b/i,              // AI technologies
    /\bAI systems?\b/i,                  // AI system, AI systems
    /\bmachine learning\b/i,             // machine learning
    /\bdeep learning\b/i,                // deep learning
    /\bgenerative AI\b/i,                // generative AI
  ];
  
  // Check title first
  let foundInTitle = false;
  let snippet = '';
  
  for (const pattern of aiPatterns) {
    if (pattern.test(title)) {
      foundInTitle = true;
      snippet = title;
      break;
    }
  }
  
  if (foundInTitle) {
    notes.push({ label: 'AI-related', color: 'bg-purple-50 text-purple-700', snippet });
  } else {
    // Check description
    const sentences = description.split(/[.!?]\s+/);
    
    for (const sentence of sentences) {
      let matched = false;
      for (const pattern of aiPatterns) {
        if (pattern.test(sentence)) {
          matched = true;
          snippet = sentence.trim();
          // Limit snippet length
          if (snippet.length > 200) {
            snippet = snippet.slice(0, 200) + '...';
          }
          break;
        }
      }
      if (matched) break;
    }
    
    if (snippet) {
      notes.push({ label: 'AI-related', color: 'bg-purple-50 text-purple-700', snippet });
    }
  }
  
  return notes;
}

export function OverviewTab({ company }: OverviewTabProps) {
  const [viewMode, setViewMode] = useState<"table" | "grid">("table");
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set(["All"]));
  const [selectedDateFilters, setSelectedDateFilters] = useState<Set<string>>(new Set(["All time"]));
  const [showOnlyAI, setShowOnlyAI] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  
  const JOBS_PER_PAGE = 10;

  const sortedJobs = [...company.jobs].sort((a, b) => 
    (b.analysis?.relevance_score || 0) - (a.analysis?.relevance_score || 0)
  );

  // Calculate job age in days
  const getJobAge = (dateString: string | undefined): number => {
    if (!dateString || dateString.trim() === '') return Infinity;
    const jobDate = new Date(dateString);
    if (isNaN(jobDate.getTime())) return Infinity;
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - jobDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // Date filter options with counts
    const dateFilterOptions = [
      { label: "All time", days: Infinity },
      { label: "Last 7 days", days: 7 },
      { label: "Last 14 days", days: 14 },
      { label: "Last 30 days", days: 30 },
      { label: "Last 3 months", days: 90 },
    ];

  // Count jobs for each date filter
  const dateFilterCounts: Record<string, number> = {};
  dateFilterOptions.forEach(option => {
    dateFilterCounts[option.label] = sortedJobs.filter(job => 
      getJobAge(job.date_creation || job.date) <= option.days
    ).length;
  });

  // Apply date filter first (with multi-select support)
  let dateFilteredJobs = sortedJobs;
  
  if (!selectedDateFilters.has("All time")) {
    // Get all selected date ranges
    const selectedOptions = dateFilterOptions.filter(opt => selectedDateFilters.has(opt.label));
    
    // If multiple filters selected, combine them (union - OR logic)
    dateFilteredJobs = sortedJobs.filter(job => {
      const jobAge = getJobAge(job.date_creation || job.date);
      // Job passes if it matches ANY of the selected date filters
      return selectedOptions.some(opt => jobAge <= opt.days);
    });
  }

  // Get all categories and their counts (including special filters) - based on date-filtered jobs
  const categoryCounts: Record<string, number> = { "All": dateFilteredJobs.length };
  
  // Standard categories
  dateFilteredJobs.forEach(job => {
    const category = categorizeJob(job.job_title, job.description);
    categoryCounts[category] = (categoryCounts[category] || 0) + 1;
  });
  
  // Sort categories by count
  const categories = ["All", ...Object.keys(categoryCounts)
    .filter(cat => cat !== "All")
    .sort((a, b) => categoryCounts[b] - categoryCounts[a])
  ];

  // Filter jobs by category (from date-filtered jobs)
  let filteredJobs = dateFilteredJobs;
  
  if (!selectedCategories.has("All")) {
    filteredJobs = dateFilteredJobs.filter(job => 
      selectedCategories.has(categorizeJob(job.job_title, job.description))
    );
  }
  
  // Apply AI filter if enabled
  if (showOnlyAI) {
    filteredJobs = filteredJobs.filter(job => {
      const notes = getJobNotes(job);
      return notes.some(note => note.label === 'AI-related');
    });
  }
  
  // Count AI-related jobs in filtered results (before AI filter)
  const aiRelatedCount = (showOnlyAI ? filteredJobs : dateFilteredJobs.filter(job => {
    if (!selectedCategories.has("All")) {
      if (!selectedCategories.has(categorizeJob(job.job_title, job.description))) {
        return false;
      }
    }
    const notes = getJobNotes(job);
    return notes.some(note => note.label === 'AI-related');
  })).length;
  
  // Pagination
  const totalPages = Math.ceil(filteredJobs.length / JOBS_PER_PAGE);
  const startIndex = (currentPage - 1) * JOBS_PER_PAGE;
  const endIndex = startIndex + JOBS_PER_PAGE;
  const paginatedJobs = filteredJobs.slice(startIndex, endIndex);
  
  // Reset to page 1 when category changes
  const handleCategoryChange = (category: string) => {
    setSelectedCategories(prev => {
      const newSet = new Set(prev);
      
      if (category === "All") {
        return new Set(["All"]);
      }
      
      // Remove "All" if selecting specific category
      newSet.delete("All");
      
      // Toggle the category
      if (newSet.has(category)) {
        newSet.delete(category);
        // If no categories left, select "All"
        if (newSet.size === 0) {
          return new Set(["All"]);
        }
      } else {
        newSet.add(category);
      }
      
      return newSet;
    });
    setCurrentPage(1);
  };
  
  // Reset to page 1 when date filter changes
  const handleDateFilterChange = (dateFilter: string) => {
    setSelectedDateFilters(prev => {
      const newSet = new Set(prev);
      
      if (dateFilter === "All time") {
        return new Set(["All time"]);
      }
      
      // Remove "All time" if selecting specific filter
      newSet.delete("All time");
      
      // Toggle the filter
      if (newSet.has(dateFilter)) {
        newSet.delete(dateFilter);
        // If no filters left, select "All time"
        if (newSet.size === 0) {
          return new Set(["All time"]);
        }
      } else {
        newSet.add(dateFilter);
      }
      
      return newSet;
    });
    setCurrentPage(1);
  };

  // Handle chart category click - select specific category
  const handleChartCategoryClick = (chartCategory: string) => {
    // Map chart category to table category
    const categoryMap: Record<string, string> = {
      'sales': 'Sales',
      'marketing': 'Marketing',
      'ecommerce': 'E-commerce',
      'retail': 'Retail',
      'creative': 'Creative'
    };
    
    const tableCategory = categoryMap[chartCategory];
    
    if (tableCategory && categoryCounts[tableCategory] && categoryCounts[tableCategory] > 0) {
      setSelectedCategories(new Set([tableCategory]));
    } else {
      setSelectedCategories(new Set(['All']));
    }
    setCurrentPage(1);
  };

  return (
    <div className="space-y-4">
      {/* Hiring Trends Chart */}
      <HiringTrendsChart 
        jobs={sortedJobs} 
        onCategoryClick={handleChartCategoryClick}
      />

      {/* Jobs Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-neutral-900">
            Job Offers Detected 
            <span className="text-neutral-400 ml-1.5">({filteredJobs.length})</span>
          </h2>
          
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
            <DropdownMenuContent align="start" className="w-48">
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
                Job Categories
                {!selectedCategories.has("All") && (
                  <span className="text-violet-600 font-semibold">
                    ({selectedCategories.size})
                  </span>
                )}
                <ChevronDown className="w-3 h-3 text-neutral-400" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-48">
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
              {categories.map((category) => (
                <DropdownMenuCheckboxItem
                  key={category}
                  checked={selectedCategories.has(category)}
                  onCheckedChange={() => handleCategoryChange(category)}
                  onSelect={(e) => e.preventDefault()}
                  className="text-xs"
                >
                  {category}
                  <span className="ml-auto text-neutral-400">
                    ({categoryCounts[category]})
                  </span>
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* AI Related Filter - Toggle Button */}
          <button
            onClick={() => {
              setShowOnlyAI(!showOnlyAI);
              setCurrentPage(1);
            }}
            className={cn(
              "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
              showOnlyAI
                ? "bg-purple-100 text-purple-700 border-purple-300"
                : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
            )}
          >
            AI Related
            {showOnlyAI && (
              <span className="text-purple-600 font-semibold">
                ({aiRelatedCount})
              </span>
            )}
          </button>

            {/* View Mode Selectors */}
            <div className="flex items-center border border-neutral-200 rounded-md p-0.5">
              <Button
                variant="ghost"
                size="sm"
                className={cn("h-6 w-6 p-0", viewMode === "table" && "bg-neutral-100")}
                onClick={() => setViewMode("table")}
              >
                <List className="w-3.5 h-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className={cn("h-6 w-6 p-0", viewMode === "grid" && "bg-neutral-100")}
                onClick={() => setViewMode("grid")}
              >
                <LayoutGrid className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        </div>

        {viewMode === "table" ? (
          <div className="border border-neutral-200 rounded-lg overflow-hidden bg-white">
            <Table>
              <TableHeader>
                <TableRow className="bg-neutral-50/50 hover:bg-neutral-50/50">
                  <TableHead className="font-medium text-xs h-8">Job Title</TableHead>
                  <TableHead className="font-medium text-xs h-8">Location</TableHead>
                  <TableHead className="font-medium text-xs h-8">Date</TableHead>
                  <TableHead className="font-medium text-xs h-8">Source</TableHead>
                  <TableHead className="font-medium text-xs h-8">AI Related</TableHead>
                  <TableHead className="w-8 h-8"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedJobs.map((job, i) => (
                  <TableRow 
                    key={i} 
                    className="cursor-pointer hover:bg-neutral-50/50"
                    onClick={() => setSelectedJob(job)}
                  >
                    <TableCell className="py-2">
                      <div className="font-medium text-neutral-900 text-xs">{job.job_title}</div>
                    </TableCell>
                    <TableCell className="text-neutral-600 text-xs py-2">{job.location || "N/A"}</TableCell>
                    <TableCell className="text-neutral-600 text-xs py-2">
                      {(job.date_creation || job.date) ? new Date(job.date_creation || job.date || '').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : "N/A"}
                    </TableCell>
                    <TableCell className="py-2">
                      <Badge variant="outline" className="font-normal capitalize text-[10px] h-5">
                        {job.job_board}
                      </Badge>
                    </TableCell>
                    <TableCell className="py-2">
                      <div className="flex flex-wrap gap-1">
                        {getJobNotes(job).map((note, idx) => (
                          <Badge key={idx} className={cn("text-[10px] h-5 px-1.5", note.color)}>
                            {note.label}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="py-2">
                      <a 
                        href={job.job_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                          <ExternalLink className="w-3.5 h-3.5 text-neutral-400" />
                        </Button>
                      </a>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {paginatedJobs.map((job, i) => (
              <div 
                key={i}
                className="border border-neutral-200 rounded-lg p-3 hover:border-neutral-300 hover:shadow-sm transition-all cursor-pointer bg-white"
                onClick={() => setSelectedJob(job)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-neutral-900 text-xs line-clamp-2">{job.job_title}</div>
                    <div className="text-[10px] text-neutral-400 mt-1">{job.location}</div>
                  </div>
                  <div className={cn(
                    "px-1.5 py-0.5 rounded-full text-[10px] font-medium flex-shrink-0",
                    (job.analysis?.relevance_score || 0) >= 8 ? "bg-green-50 text-green-700" :
                    (job.analysis?.relevance_score || 0) >= 6 ? "bg-amber-50 text-amber-700" :
                    "bg-neutral-100 text-neutral-600"
                  )}>
                    {job.analysis?.relevance_score || 0}
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2.5 pt-2.5 border-t border-neutral-100">
                  <Badge variant="outline" className="text-[10px] font-normal capitalize h-4 px-1.5">
                    {job.job_board}
                  </Badge>
                  <span className="text-[10px] text-neutral-400">
                    {(job.date_creation || job.date) ? new Date(job.date_creation || job.date || '').toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : "N/A"}
                  </span>
                </div>
                {getJobNotes(job).length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {getJobNotes(job).map((note, idx) => (
                      <Badge key={idx} className={cn("text-[10px] h-4 px-1.5", note.color)}>
                        {note.label}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-neutral-100">
            <div className="text-xs text-neutral-500">
              Showing {startIndex + 1}-{Math.min(endIndex, filteredJobs.length)} of {filteredJobs.length} jobs
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
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
                variant="outline"
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
      </div>

      {/* Job Detail Modal */}
      <JobDetailModal 
        job={selectedJob} 
        jobNotes={selectedJob ? getJobNotes(selectedJob) : []}
        onClose={() => setSelectedJob(null)} 
      />
    </div>
  );
}


