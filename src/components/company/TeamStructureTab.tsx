"use client";

import { useState, useMemo } from "react";
import { Company, Job } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ChevronDown,
  ChevronUp,
  ExternalLink, 
  Crown,
  ArrowDown
} from "lucide-react";
import { JobDetailModal } from "./JobDetailModal";

interface TeamStructureTabProps {
  company: Company;
}

interface DecisionMaker {
  name: string;
  department: string;
  reportsTo?: string;
  evidence: string;
  job: Job;
}

const departmentColors: Record<string, string> = {
  marketing: "bg-blue-100 text-blue-700 border-blue-200",
  ecommerce: "bg-green-100 text-green-700 border-green-200",
  creative: "bg-purple-100 text-purple-700 border-purple-200",
  product: "bg-orange-100 text-orange-700 border-orange-200",
  sales: "bg-red-100 text-red-700 border-red-200",
  other: "bg-neutral-100 text-neutral-700 border-neutral-200"
};

export function TeamStructureTab({ company }: TeamStructureTabProps) {
  const [expandedDM, setExpandedDM] = useState<Set<string>>(new Set());
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  // Extract decision makers with hierarchy
  const decisionMakers = useMemo(() => {
    const dms: DecisionMaker[] = [];

    company.jobs.forEach(job => {
      if (!job.analysis?.team_structure) return;
      
      const ts = job.analysis.team_structure;
      
      // Extract decision makers from each department
      Object.entries(ts).forEach(([dept, deptData]) => {
        if (!deptData || typeof deptData !== 'object' || 
            !['marketing', 'ecommerce', 'creative', 'product', 'sales', 'other'].includes(dept)) return;
        
        // Key decision makers
        (deptData as any).key_decision_makers?.forEach((item: any) => {
          if (item.role && item.evidence) {
            // Extract "reports to" relationship
            const reportsToMatch = item.evidence.match(/reports?\s+to[:\s]+([^.,;]+)/i);
            
            dms.push({
              name: item.role,
              department: dept,
              reportsTo: reportsToMatch ? reportsToMatch[1].trim() : undefined,
              evidence: item.evidence,
              job
            });
          }
        });
        
        // Managers (also decision makers)
        (deptData as any).managers?.forEach((item: any) => {
          if (item.role && item.evidence) {
            const reportsToMatch = item.evidence.match(/reports?\s+to[:\s]+([^.,;]+)/i);
            
            dms.push({
              name: item.role,
              department: dept,
              reportsTo: reportsToMatch ? reportsToMatch[1].trim() : undefined,
              evidence: item.evidence,
              job
            });
          }
        });
      });
    });

    return dms;
  }, [company]);

  const toggleDM = (id: string) => {
    const newSet = new Set(expandedDM);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedDM(newSet);
  };

  if (decisionMakers.length === 0) {
    return (
      <div className="text-center py-12 text-neutral-400 text-sm">
        No team structure information detected for this company.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center gap-2 pb-2">
        <Crown className="w-3.5 h-3.5 text-amber-500" />
        <h2 className="text-xs font-semibold text-neutral-900">
          Key Decision Makers ({decisionMakers.length})
        </h2>
      </div>

      {/* Decision Makers List */}
      <div className="space-y-2">
        {decisionMakers.map((dm, i) => {
          const dmId = `dm-${i}`;
          const isExpanded = expandedDM.has(dmId);
          
          return (
            <div
              key={dmId}
              className="border border-neutral-200 rounded-lg bg-white overflow-hidden"
            >
              <div
                className="p-2.5 cursor-pointer hover:bg-neutral-50 transition-colors flex items-center justify-between gap-3"
                onClick={() => toggleDM(dmId)}
              >
                <div className="flex items-center gap-2.5 flex-1 min-w-0">
                  <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
                    <Crown className="w-3 h-3 text-amber-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-neutral-900 text-xs truncate">
                      {dm.name}
                    </div>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <Badge 
                        variant="outline" 
                        className={`text-[9px] h-4 px-1.5 capitalize ${departmentColors[dm.department]}`}
                      >
                        {dm.department}
                      </Badge>
                      {dm.reportsTo && (
                        <>
                          <ArrowDown className="w-2.5 h-2.5 text-neutral-400" />
                          <span className="text-[9px] text-neutral-500 truncate">
                            {dm.reportsTo}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 flex-shrink-0">
                  {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </Button>
              </div>

              {isExpanded && (
                <div className="px-2.5 pb-2.5 pt-2 border-t border-neutral-100 bg-neutral-50 space-y-2">
                  <div>
                    <div className="text-[9px] text-neutral-500 mb-1">Evidence:</div>
                    <div className="text-xs text-neutral-600 italic bg-white rounded p-2 border border-neutral-200">
                      &quot;{dm.evidence}&quot;
                    </div>
                  </div>
                  <div className="text-[9px] text-neutral-400">
                    From: {dm.job.job_title}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="h-6 text-[10px] flex-1"
                      onClick={(e) => { e.stopPropagation(); setSelectedJob(dm.job); }}
                    >
                      View Full Job
                    </Button>
                    <a 
                      href={dm.job.job_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                        <ExternalLink className="w-3 h-3" />
                      </Button>
                    </a>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Job Detail Modal */}
      <JobDetailModal job={selectedJob} jobNotes={[]} onClose={() => setSelectedJob(null)} />
    </div>
  );
}
