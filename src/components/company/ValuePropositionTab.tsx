"use client";

import { useState } from "react";
import { Company, Job } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { 
  ChevronDown, 
  ChevronRight,
  ChevronUp,
  ExternalLink, 
  Zap,
  TrendingUp,
  DollarSign,
  Sparkles,
  Palette,
  Camera,
  Copy,
  Check
} from "lucide-react";
import { JobDetailModal } from "./JobDetailModal";

interface ValuePropositionTabProps {
  company: Company;
}

interface InsightItem {
  job: Job;
  insight: string;
  evidence: string;
  relevance?: string;
}

export function ValuePropositionTab({ company }: ValuePropositionTabProps) {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["volume", "speed", "conversion", "brand", "creative", "photography"])
  );
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [copied, setCopied] = useState(false);

  // Collect insights from new structure
  const volumeScaleInsights: InsightItem[] = [];
  const speedInsights: InsightItem[] = [];
  const conversionInsights: InsightItem[] = [];
  const brandInsights: InsightItem[] = [];
  const creativeInsights: InsightItem[] = [];
  const photographyInsights: InsightItem[] = [];

  company.jobs.forEach(job => {
    if (!job.analysis?.value_proposition) return;
    
    const vp = job.analysis.value_proposition;
    
    // Efficiency & Conversion
    vp.efficiency_conversion?.volume_scale?.forEach(item => {
      if (item.insight && item.evidence) {
        volumeScaleInsights.push({ 
          job, 
          insight: item.insight, 
          evidence: item.evidence,
          relevance: item.relevance 
        });
      }
    });
    
    vp.efficiency_conversion?.speed_time_to_market?.forEach(item => {
      if (item.insight && item.evidence) {
        speedInsights.push({ 
          job, 
          insight: item.insight, 
          evidence: item.evidence,
          relevance: item.relevance 
        });
      }
    });
    
    vp.efficiency_conversion?.conversion_revenue?.forEach(item => {
      if (item.insight && item.evidence) {
        conversionInsights.push({ 
          job, 
          insight: item.insight, 
          evidence: item.evidence,
          relevance: item.relevance 
        });
      }
    });
    
    // Brand & Creativity
    vp.brand_creativity?.brand_consistency?.forEach(item => {
      if (item.insight && item.evidence) {
        brandInsights.push({ 
          job, 
          insight: item.insight, 
          evidence: item.evidence,
          relevance: item.relevance 
        });
      }
    });
    
    vp.brand_creativity?.creative_direction?.forEach(item => {
      if (item.insight && item.evidence) {
        creativeInsights.push({ 
          job, 
          insight: item.insight, 
          evidence: item.evidence,
          relevance: item.relevance 
        });
      }
    });
    
    vp.brand_creativity?.photography_staging?.forEach(item => {
      if (item.insight && item.evidence) {
        photographyInsights.push({ 
          job, 
          insight: item.insight, 
          evidence: item.evidence,
          relevance: item.relevance 
        });
      }
    });
  });

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedItems(newExpanded);
  };

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const prestiValueProp = `presti.ai generates realistic photostaging and photoshoot images from product photos.

✅ Intact products in visuals
✅ Respect for brand identity
✅ Scalable across entire catalog
✅ Fast and efficient production`;

  const generateMessage = () => {
    const allInsights = [
      ...volumeScaleInsights,
      ...speedInsights,
      ...conversionInsights,
      ...brandInsights,
      ...creativeInsights,
      ...photographyInsights
    ];
    const topInsights = allInsights.slice(0, 2).map(i => i.insight).join(", ");
    
    return `Hello,

I noticed that ${company.name} is hiring for positions related to ${topInsights || "visual content creation"}.

At presti.ai, we help furniture companies generate professional photostaging images from simple product photos.

Our clients face the same challenges: production volume, brand consistency, and speed to market.

Would you be available for a 15-minute call this week?`;
  };

  const copyMessage = () => {
    navigator.clipboard.writeText(generateMessage());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderInsightSection = (
    sectionId: string,
    title: string,
    icon: React.ReactNode,
    insights: InsightItem[],
    iconColor: string
  ) => {
    if (insights.length === 0) return null;
    
    return (
      <Collapsible 
        open={expandedSections.has(sectionId)} 
        onOpenChange={() => toggleSection(sectionId)}
        className="border border-neutral-200 rounded-lg bg-white"
      >
        <CollapsibleTrigger className="w-full">
          <div className="flex items-center justify-between px-3 py-2.5 hover:bg-neutral-50/50 transition-colors rounded-t-lg">
            <div className="flex items-center gap-1.5">
              <span className={iconColor}>{icon}</span>
              <h4 className="font-medium text-neutral-900 text-xs">{title} ({insights.length})</h4>
            </div>
            {expandedSections.has(sectionId) ? (
              <ChevronDown className="w-4 h-4 text-neutral-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-neutral-400" />
            )}
          </div>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="divide-y divide-neutral-100 border-t border-neutral-100">
            {insights.slice(0, 20).map((item, i) => {
              const itemId = `${sectionId}-${i}`;
              const isExpanded = expandedItems.has(itemId);
              return (
                <div key={i} className="p-2.5">
                  <div 
                    className="flex items-start justify-between cursor-pointer"
                    onClick={() => toggleExpand(itemId)}
                  >
                    <div className="flex-1">
                      <div className="font-medium text-neutral-900 text-xs">{item.insight}</div>
                      <div className="text-[10px] text-neutral-400 mt-0.5">
                        From: {item.job.job_title}
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" className="h-6 w-6 p-0 flex-shrink-0 ml-2">
                      {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    </Button>
                  </div>
                  {isExpanded && (
                    <div className="mt-2 p-2 bg-neutral-50 rounded-md">
                      <p className="text-xs text-neutral-600 italic mb-2">&quot;{item.evidence}&quot;</p>
                      {item.relevance && (
                        <p className="text-[10px] text-violet-600 mb-2">
                          💡 {item.relevance}
                        </p>
                      )}
                      <div className="flex items-center gap-1.5">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="h-6 text-[10px] px-2"
                          onClick={(e) => { e.stopPropagation(); setSelectedJob(item.job); }}
                        >
                          View Full Job
                        </Button>
                        <a href={item.job.job_url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="sm" className="h-6 text-[10px] gap-1 px-2">
                            <ExternalLink className="w-2.5 h-2.5" />
                            Original
                          </Button>
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </CollapsibleContent>
      </Collapsible>
    );
  };

  const hasEfficiencyInsights = volumeScaleInsights.length > 0 || speedInsights.length > 0 || conversionInsights.length > 0;
  const hasBrandInsights = brandInsights.length > 0 || creativeInsights.length > 0 || photographyInsights.length > 0;
  const hasAnyInsights = hasEfficiencyInsights || hasBrandInsights;

  return (
    <div className="flex gap-4">
      {/* Main content */}
      <div className="flex-1 space-y-4">
        {!hasAnyInsights && (
          <div className="text-center py-12 text-neutral-400 text-sm">
            No value proposition information detected for this company.
          </div>
        )}

        {/* Efficiency & Conversion Section */}
        {hasEfficiencyInsights && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 px-1">
              <Zap className="w-4 h-4 text-blue-500" />
              <h3 className="font-semibold text-neutral-900 text-sm">Efficiency & Conversion</h3>
            </div>
            
            {renderInsightSection(
              "volume",
              "Volume & Scale",
              <TrendingUp className="w-3.5 h-3.5" />,
              volumeScaleInsights,
              "text-blue-500"
            )}
            
            {renderInsightSection(
              "speed",
              "Speed & Time-to-Market",
              <Zap className="w-3.5 h-3.5" />,
              speedInsights,
              "text-blue-500"
            )}
            
            {renderInsightSection(
              "conversion",
              "Conversion & Revenue",
              <DollarSign className="w-3.5 h-3.5" />,
              conversionInsights,
              "text-blue-500"
            )}
          </div>
        )}

        {/* Brand & Creativity Section */}
        {hasBrandInsights && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 px-1">
              <Palette className="w-4 h-4 text-purple-500" />
              <h3 className="font-semibold text-neutral-900 text-sm">Brand & Creativity</h3>
            </div>
            
            {renderInsightSection(
              "brand",
              "Brand Consistency",
              <Sparkles className="w-3.5 h-3.5" />,
              brandInsights,
              "text-purple-500"
            )}
            
            {renderInsightSection(
              "creative",
              "Creative Direction",
              <Palette className="w-3.5 h-3.5" />,
              creativeInsights,
              "text-purple-500"
            )}
            
            {renderInsightSection(
              "photography",
              "Photography & Staging",
              <Camera className="w-3.5 h-3.5" />,
              photographyInsights,
              "text-purple-500"
            )}
          </div>
        )}
      </div>

      {/* Right sidebar - Value Prop & Message Generator */}
      <div className="w-72 space-y-3">
        <div className="border border-neutral-200 rounded-lg p-3 sticky top-6 bg-white">
          <div className="flex items-center gap-2 text-xs font-medium text-neutral-700 mb-3">
            <Sparkles className="w-3.5 h-3.5 text-violet-500" />
            presti.ai Value Proposition
          </div>
          <div className="text-xs text-neutral-600 whitespace-pre-line bg-violet-50 rounded-md p-2.5">
            {prestiValueProp}
          </div>
          
          <Separator className="my-4" />
          
          <div className="space-y-3">
            <div className="text-xs font-medium text-neutral-700">Generated Outreach Message</div>
            <div className="text-[10px] text-neutral-500 bg-neutral-50 rounded-md p-2.5 whitespace-pre-line max-h-40 overflow-y-auto">
              {generateMessage()}
            </div>
            <Button 
              className="w-full gap-2" 
              size="sm"
              onClick={copyMessage}
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copied ? "Copied!" : "Copy Message"}
            </Button>
          </div>
        </div>
      </div>

      {/* Job Detail Modal */}
      <JobDetailModal job={selectedJob} jobNotes={[]} onClose={() => setSelectedJob(null)} />
    </div>
  );
}
