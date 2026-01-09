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
  ChevronRight,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

export default function JobsPage() {
  const [data, setData] = useState<DataStore | null>(null);
  const [viewMode, setViewMode] = useState<"table" | "grid">("table");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isKeyAccountsOpen, setIsKeyAccountsOpen] = useState(true);
  const [isOtherAccountsOpen, setIsOtherAccountsOpen] = useState(true);

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

  // Get all companies
  const allCompanies = data?.companies ? Object.values(data.companies) : [];
  
  // Normalize company names for comparison (lowercase, remove special chars, suffixes)
  const normalizeCompanyName = (name: string): string => {
    return name
      .toLowerCase()
      .replace(/[,\.\-]/g, '') // Remove commas, dots, and hyphens
      .replace(/\s+(inc|llc|ltd|incorporated|industries|corp|corporation)\.?\s*$/gi, '') // Remove common suffixes
      .replace(/\s+/g, ' ') // Normalize spaces
      .replace(/&/g, 'and') // Normalize ampersand
      .trim();
  };
  
  // Jerrica's key accounts - exact names as they appear in data.json
  const jerricaAccountNames = [
    "La-Z-Boy",
    "Williams Sonoma",
    "Millerknoll",
    "Palliser Furniture Ltd.",
    "Rooms to Go",
    "Article",
    "American Leather",
    "Serena & Lily",
    "Anthropologie Home",
    "Rowe Furniture",
    "Room & Board",
    "Bassett Furniture",
    "Living Spaces",
    "Jonathan Louis",
    "Theodore Alexander",
    "Kimball International",
    "Ballard Designs",
    "Design Within Reach",
    "Saks Global",
    "Costco"
  ];
  
  // Other top companies (not in Jerrica's list)
  const otherAccountNames = [
    "Target",
    "Home Depot",
    "California Closets",
    "Balsam Brands",
    "Ashley Furniture Industries",
    "Arhaus"
  ];
  
  // Create normalized lookup sets for faster matching
  const normalizedJerricaAccounts = new Set(jerricaAccountNames.map(normalizeCompanyName));
  const normalizedOtherAccounts = new Set(otherAccountNames.map(normalizeCompanyName));
  
  // Filter companies into Jerrica's accounts and Other accounts
  const keyAccounts = allCompanies.filter(company => 
    normalizedJerricaAccounts.has(normalizeCompanyName(company.name))
  );
  
  const otherAccounts = allCompanies.filter(company => 
    normalizedOtherAccounts.has(normalizeCompanyName(company.name))
  );
  
  // Sort by job count
  const sortedKeyAccounts = [...keyAccounts].sort((a, b) => b.jobs.length - a.jobs.length);
  const sortedOtherAccounts = [...otherAccounts].sort((a, b) => b.jobs.length - a.jobs.length);

  const totalCompanies = keyAccounts.length + otherAccounts.length;
  const totalJobs = keyAccounts.reduce((acc, c) => acc + c.jobs.length, 0) + 
                    otherAccounts.reduce((acc, c) => acc + c.jobs.length, 0);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-white sticky top-0 z-10 border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-6 py-2.5">
          <div className="flex items-center justify-between min-h-[52px]">
            <div>
              <h1 className="text-base font-semibold text-neutral-900">Companies</h1>
              <p className="text-xs text-neutral-500 mt-0.5">
                {totalCompanies} companies · {totalJobs} jobs analyzed
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-4 space-y-4">
        {viewMode === "table" ? (
          <>
            {/* Jerrica's Key Accounts */}
            <Collapsible open={isKeyAccountsOpen} onOpenChange={setIsKeyAccountsOpen}>
              <div className="border border-neutral-200 rounded-lg overflow-hidden bg-white">
                <CollapsibleTrigger className="w-full">
                  <div className="flex items-center justify-between px-4 py-3 bg-violet-50/50 hover:bg-violet-50 transition-colors">
                    <div className="flex items-center gap-2">
                      <h2 className="text-sm font-semibold text-neutral-900">Jerrica&apos;s key accounts</h2>
                      <Badge variant="secondary" className="font-normal text-[9px] h-4">
                        {sortedKeyAccounts.length} companies
                      </Badge>
                    </div>
                    {isKeyAccountsOpen ? (
                      <ChevronUp className="w-4 h-4 text-neutral-500" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-neutral-500" />
                    )}
                  </div>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-neutral-50/50 hover:bg-neutral-50/50">
                        <TableHead className="font-medium text-[10px] h-7">Company</TableHead>
                        <TableHead className="font-medium text-[10px] h-7">Industry</TableHead>
                        <TableHead className="font-medium text-[10px] h-7 text-center">Jobs</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {sortedKeyAccounts.map((company) => {
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
                                    <div className="font-medium text-neutral-900 text-xs">{company.name}</div>
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
                </CollapsibleContent>
              </div>
            </Collapsible>

            {/* Other Accounts */}
            <Collapsible open={isOtherAccountsOpen} onOpenChange={setIsOtherAccountsOpen}>
              <div className="border border-neutral-200 rounded-lg overflow-hidden bg-white">
                <CollapsibleTrigger className="w-full">
                  <div className="flex items-center justify-between px-4 py-3 bg-neutral-50/50 hover:bg-neutral-50 transition-colors">
                    <div className="flex items-center gap-2">
                      <h2 className="text-sm font-semibold text-neutral-900">Other accounts</h2>
                      <Badge variant="secondary" className="font-normal text-[9px] h-4">
                        {sortedOtherAccounts.length} companies
                      </Badge>
                    </div>
                    {isOtherAccountsOpen ? (
                      <ChevronUp className="w-4 h-4 text-neutral-500" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-neutral-500" />
                    )}
                  </div>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-neutral-50/50 hover:bg-neutral-50/50">
                        <TableHead className="font-medium text-[10px] h-7">Company</TableHead>
                        <TableHead className="font-medium text-[10px] h-7">Industry</TableHead>
                        <TableHead className="font-medium text-[10px] h-7 text-center">Jobs</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {sortedOtherAccounts.map((company) => {
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
                                    <div className="font-medium text-neutral-900 text-xs">{company.name}</div>
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
                </CollapsibleContent>
              </div>
            </Collapsible>
          </>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {[...sortedKeyAccounts, ...sortedOtherAccounts].map((company) => {
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
      </div>
    </div>
  );
}

