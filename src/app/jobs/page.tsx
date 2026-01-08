"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getData, getCompanyStats } from "@/lib/data";
import { DataStore, Company } from "@/lib/types";
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
  Building2, 
  ExternalLink,
  Users,
  Briefcase,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function JobsPage() {
  const [data, setData] = useState<DataStore | null>(null);
  const [viewMode, setViewMode] = useState<"table" | "grid">("table");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  const COMPANIES_PER_PAGE = 20;

  useEffect(() => {
    getData()
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error loading data:", error);
        setError(error.message || "Failed to load data");
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

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  // Only show these 9 Tier 0 companies in the interface
  const tier0CompaniesNames = ['Costco', 'Target', 'Home Depot', "Lowe's", 'La-Z-Boy', 'Pottery Barn', 'Williams Sonoma', 'West Elm', 'California Closets'];
  
  const allCompanies = data?.companies ? Object.values(data.companies) : [];
  
  // Filter to only show Tier 0 companies
  const companies = allCompanies.filter(company => tier0CompaniesNames.includes(company.name));
  
  const priorityCompanies = tier0CompaniesNames;
  
  // Custom sort: priority companies first, then rest by job count
  const sortedCompanies = [...companies].sort((a, b) => {
    const aIsPriority = priorityCompanies.includes(a.name);
    const bIsPriority = priorityCompanies.includes(b.name);
    
    if (aIsPriority && !bIsPriority) return -1;
    if (!aIsPriority && bIsPriority) return 1;
    
    // Both priority: sort by priority order
    if (aIsPriority && bIsPriority) {
      return priorityCompanies.indexOf(a.name) - priorityCompanies.indexOf(b.name);
    }
    
    // Both not priority: sort by job count
    return b.jobs.length - a.jobs.length;
  });

  // Pagination
  const totalPages = Math.ceil(sortedCompanies.length / COMPANIES_PER_PAGE);
  const startIndex = (currentPage - 1) * COMPANIES_PER_PAGE;
  const endIndex = startIndex + COMPANIES_PER_PAGE;
  const paginatedCompanies = sortedCompanies.slice(startIndex, endIndex);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-white sticky top-0 z-10 border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-6 py-2.5">
          <div className="flex items-center justify-between min-h-[52px]">
            <div>
              <h1 className="text-base font-semibold text-neutral-900">Companies</h1>
              <p className="text-xs text-neutral-500 mt-0.5">
                {companies.length} companies · {companies.reduce((acc, c) => acc + c.jobs.length, 0)} jobs analyzed
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        {viewMode === "table" ? (
          <div className="border border-neutral-200 rounded-lg overflow-hidden bg-white">
            <Table>
              <TableHeader>
                <TableRow className="bg-neutral-50/50 hover:bg-neutral-50/50">
                  <TableHead className="font-medium text-[10px] h-7">Company</TableHead>
                  <TableHead className="font-medium text-[10px] h-7">Industry</TableHead>
                  <TableHead className="font-medium text-[10px] h-7 text-center">Jobs</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedCompanies.map((company) => {
                  const stats = getCompanyStats(company);
                  return (
                    <TableRow 
                      key={company.name}
                      className="cursor-pointer hover:bg-neutral-50/50"
                    >
                      <TableCell className="py-1.5">
                        <Link href={`/jobs/${encodeURIComponent(company.name)}`} className="block">
                          <div className="flex items-center gap-2">
                            <div className="w-5 h-5 rounded bg-neutral-100 flex items-center justify-center">
                              <Building2 className="w-3 h-3 text-neutral-500" />
                            </div>
                            <div>
                              <div className="flex items-center gap-1.5">
                                <div className="font-medium text-neutral-900 text-xs">{company.name}</div>
                                <Badge variant="secondary" className="font-normal text-[9px] h-4 bg-green-100 text-green-700 hover:bg-green-100">
                                  Tier 0
                                </Badge>
                              </div>
                              <div className="text-[9px] text-neutral-400">{company.employees} emp.</div>
                            </div>
                          </div>
                        </Link>
                      </TableCell>
                      <TableCell className="py-1.5">
                        <Badge variant="secondary" className="font-normal text-[9px] h-4">
                          {company.industry}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center py-1.5">
                        <div className="flex items-center justify-center gap-1">
                          <Briefcase className="w-2.5 h-2.5 text-neutral-400" />
                          <span className="font-medium text-xs">{stats.totalJobs}</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {paginatedCompanies.map((company) => {
              const stats = getCompanyStats(company);
              return (
                <Link 
                  key={company.name}
                  href={`/jobs/${encodeURIComponent(company.name)}`}
                  className="block"
                >
                  <div className="border border-neutral-200 rounded-lg p-3 hover:border-neutral-300 hover:shadow-sm transition-all bg-white">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-md bg-neutral-100 flex items-center justify-center flex-shrink-0">
                          <Building2 className="w-3.5 h-3.5 text-neutral-500" />
                        </div>
                        <div className="min-w-0">
                          <div className="font-medium text-neutral-900 text-xs truncate">{company.name}</div>
                          <div className="text-[10px] text-neutral-400">{company.industry}</div>
                        </div>
                      </div>
                      <div className={cn(
                        "px-1.5 py-0.5 rounded-full text-[10px] font-medium flex-shrink-0",
                        stats.avgScore >= 8 ? "bg-green-50 text-green-700" :
                        stats.avgScore >= 6 ? "bg-amber-50 text-amber-700" :
                        "bg-neutral-100 text-neutral-600"
                      )}>
                        {stats.avgScore}
                      </div>
                    </div>
                    
                    <div className="mt-2.5 flex items-center gap-3 text-[10px] text-neutral-500">
                      <div className="flex items-center gap-1">
                        <Briefcase className="w-3 h-3" />
                        {stats.totalJobs}
                      </div>
                      <div className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {company.employees}
                      </div>
                    </div>
                    
                    {stats.keyInsights.length > 0 && (
                      <div className="mt-2.5 pt-2.5 border-t border-neutral-100">
                        <p className="text-[10px] text-neutral-600 line-clamp-2">
                          {stats.keyInsights[0]}
                        </p>
                      </div>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-neutral-200">
            <div className="text-xs text-neutral-500">
              Showing {startIndex + 1}-{Math.min(endIndex, sortedCompanies.length)} of {sortedCompanies.length} companies
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
      </div>
    </div>
  );
}

