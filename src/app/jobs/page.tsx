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
  Briefcase
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function JobsPage() {
  const [data, setData] = useState<DataStore | null>(null);
  const [viewMode, setViewMode] = useState<"table" | "grid">("table");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getData().then((d) => {
      setData(d);
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

  const companies = data?.companies ? Object.values(data.companies) : [];
  
  // Priority companies: 8 new ones + California Closets
  const newCompanies = ['Costco', 'Target', 'Home Depot', "Lowe's", 'La-Z-Boy', 'Pottery Barn', 'Williams Sonoma', 'West Elm'];
  const priorityCompanies = [...newCompanies, 'California Closets'];
  
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

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-white sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-2.5">
          <div className="flex items-center justify-between min-h-[52px]">
            <div>
              <h1 className="text-base font-semibold text-neutral-900">Companies</h1>
              <p className="text-xs text-neutral-500 mt-0.5">
                {companies.length} companies · {companies.reduce((acc, c) => acc + c.jobs.length, 0)} jobs analyzed
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center border border-neutral-200 rounded-md p-0.5">
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "h-6 w-6 p-0",
                    viewMode === "table" && "bg-neutral-100"
                  )}
                  onClick={() => setViewMode("table")}
                >
                  <List className="w-3.5 h-3.5" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "h-6 w-6 p-0",
                    viewMode === "grid" && "bg-neutral-100"
                  )}
                  onClick={() => setViewMode("grid")}
                >
                  <LayoutGrid className="w-3.5 h-3.5" />
                </Button>
              </div>
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
                {sortedCompanies.map((company) => {
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
                                {newCompanies.includes(company.name) && (
                                  <Badge variant="secondary" className="font-normal text-[9px] h-4 bg-green-100 text-green-700 hover:bg-green-100">
                                    Tier 0
                                  </Badge>
                                )}
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
            {sortedCompanies.map((company) => {
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

