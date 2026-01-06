"use client";

import { useState } from "react";
import { Company, Job } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { 
  ChevronDown, 
  ChevronRight,
  ExternalLink, 
  Palette,
  Box,
  ShoppingCart
} from "lucide-react";
import { JobDetailModal } from "./JobDetailModal";

interface TechStackTabProps {
  company: Company;
}

interface ToolItem {
  job: Job;
  type: "design" | "3d" | "ecommerce";
  label: string;
  evidence: string;
}

export function TechStackTab({ company }: TechStackTabProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["design", "3d", "photography", "ecommerce", "status_quo"])
  );
  const [activeProof, setActiveProof] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  // Collect all tools from new structure
  const toolItems: ToolItem[] = [];
  
  company.jobs.forEach(job => {
    if (!job.analysis?.tools_ecosystem) return;
    
    // Design tools
    job.analysis.tools_ecosystem.design_tools?.forEach(t => {
      if (t.tool && t.evidence) {
        toolItems.push({
          job,
          type: "design",
          label: t.tool,
          evidence: t.evidence,
        });
      }
    });
    
    // 3D tools
    job.analysis.tools_ecosystem["3d_tools"]?.forEach(t => {
      if (t.tool && t.evidence) {
        toolItems.push({
          job,
          type: "3d",
          label: t.tool,
          evidence: t.evidence,
        });
      }
    });
    
    // E-commerce platforms
    job.analysis.tools_ecosystem.ecommerce_platforms?.forEach(t => {
      if (t.platform && t.evidence) {
        toolItems.push({
          job,
          type: "ecommerce",
          label: t.platform,
          evidence: t.evidence,
        });
      }
    });
  });

  // Group by type
  const designTools = toolItems.filter(e => e.type === "design");
  const tools3d = toolItems.filter(e => e.type === "3d");
  const ecommerceTools = toolItems.filter(e => e.type === "ecommerce");

  // Get unique tools per category
  const getUniqueTools = (tools: ToolItem[]) => {
    const uniqueMap = new Map<string, ToolItem[]>();
    tools.forEach(tool => {
      const key = tool.label.toLowerCase();
      if (!uniqueMap.has(key)) {
        uniqueMap.set(key, []);
      }
      uniqueMap.get(key)!.push(tool);
    });
    return Array.from(uniqueMap.entries()).map(([key, instances]) => ({
      label: instances[0].label,
      count: instances.length,
      instances
    }));
  };

  const uniqueDesignTools = getUniqueTools(designTools);
  const unique3dTools = getUniqueTools(tools3d);
  const uniqueEcommerceTools = getUniqueTools(ecommerceTools);

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const handleToolClick = (toolKey: string) => {
    setActiveProof(activeProof === toolKey ? null : toolKey);
  };

  const renderToolCategory = (
    categoryId: string,
    categoryName: string,
    icon: React.ReactNode,
    iconColor: string,
    uniqueTools: Array<{ label: string; count: number; instances: ToolItem[] }>
  ) => {
    if (uniqueTools.length === 0) return null;

    return (
      <Collapsible 
        open={expandedSections.has(categoryId)} 
        onOpenChange={() => toggleSection(categoryId)}
        className="border border-neutral-200 rounded-lg bg-white"
      >
        <CollapsibleTrigger className="w-full">
          <div className="flex items-center justify-between px-3 py-2.5 hover:bg-neutral-50/50 transition-colors rounded-t-lg">
            <div className="flex items-center gap-1.5">
              <span className={iconColor}>{icon}</span>
              <h4 className="font-medium text-neutral-900 text-xs">{categoryName} ({uniqueTools.length})</h4>
            </div>
            {expandedSections.has(categoryId) ? (
              <ChevronDown className="w-4 h-4 text-neutral-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-neutral-400" />
            )}
          </div>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="p-3 space-y-2">
            {/* Tool chips */}
            <div className="flex flex-wrap gap-1.5">
              {uniqueTools.map((tool, i) => (
                <Badge
                  key={i}
                  variant="outline"
                  className="cursor-pointer hover:bg-neutral-100 transition-colors text-[10px] h-5 px-2"
                  onClick={() => handleToolClick(`${categoryId}-${tool.label}`)}
                >
                  {tool.label}
                  {tool.count > 1 && (
                    <span className="ml-1 text-neutral-400">×{tool.count}</span>
                  )}
                </Badge>
              ))}
            </div>

            {/* Single proof display */}
            {uniqueTools.map((tool, i) => {
              const proofKey = `${categoryId}-${tool.label}`;
              if (activeProof !== proofKey) return null;

              const instance = tool.instances[0];
              return (
                <div key={i} className="mt-3 p-2.5 bg-neutral-50 rounded-md border border-neutral-200">
                  <div className="text-[10px] font-medium text-neutral-700 mb-1">
                    {tool.label} {tool.count > 1 && `(${tool.count} mentions)`}
                  </div>
                  <p className="text-xs text-neutral-600 italic mb-2">
                    &quot;{instance.evidence}&quot;
                  </p>
                  <div className="text-[9px] text-neutral-400 mb-2">
                    From: {instance.job.job_title}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="h-6 text-[10px] px-2"
                      onClick={() => setSelectedJob(instance.job)}
                    >
                      View Full Job
                    </Button>
                    <a href={instance.job.job_url} target="_blank" rel="noopener noreferrer">
                      <Button variant="ghost" size="sm" className="h-6 text-[10px] gap-1 px-2">
                        <ExternalLink className="w-2.5 h-2.5" />
                        Original
                      </Button>
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </CollapsibleContent>
      </Collapsible>
    );
  };

  const hasAnyTools = uniqueDesignTools.length > 0 || unique3dTools.length > 0 || 
                      uniqueEcommerceTools.length > 0;

  return (
    <div className="space-y-3">
      {!hasAnyTools && (
        <div className="text-center py-12 text-neutral-400 text-sm">
          No tools detected for this company.
        </div>
      )}

      {renderToolCategory(
        "design",
        "Design Tools",
        <Palette className="w-3.5 h-3.5" />,
        "text-purple-500",
        uniqueDesignTools
      )}

      {renderToolCategory(
        "3d",
        "3D Tools",
        <Box className="w-3.5 h-3.5" />,
        "text-blue-500",
        unique3dTools
      )}

      {renderToolCategory(
        "ecommerce",
        "E-commerce Platforms",
        <ShoppingCart className="w-3.5 h-3.5" />,
        "text-orange-500",
        uniqueEcommerceTools
      )}

      {/* Job Detail Modal */}
      <JobDetailModal job={selectedJob} jobNotes={[]} onClose={() => setSelectedJob(null)} />
    </div>
  );
}
