"use client";

import { NewsItem } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  ExternalLink, 
  Calendar, 
  Lightbulb
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NewsDetailModalProps {
  news: NewsItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export function NewsDetailModal({ news, isOpen, onClose }: NewsDetailModalProps) {
  if (!news) return null;

  const categoryLabels: Record<NewsItem["category"], string> = {
    // High priority
    digital_transformation: "Digital Transformation",
    catalog_expansion: "Catalog Expansion",
    ecommerce_growth: "E-commerce Growth",
    visual_content_strategy: "Visual Strategy",
    supply_chain_challenges: "Supply Chain",
    international_expansion: "International",
    time_to_market: "Time-to-Market",
    large_catalog_operations: "Large Catalog",
    // Medium priority
    omnichannel_strategy: "Omnichannel",
    product_customization: "Customization",
    private_label: "Private Label",
    technology_innovation: "Tech Innovation",
    product_innovation: "Product Innovation",
    sustainability_initiative: "Sustainability",
    partnership: "Partnership",
    // Supporting
    cost_optimization: "Cost Optimization",
    merger_acquisition: "M&A",
    platform_migration: "Platform",
    marketing_campaigns: "Marketing",
    ai_adoption: "AI Adoption",
    visual_content: "Visual Content",
    ai_investment: "AI Investment",
    hiring: "Hiring",
  };

  const categoryColors: Record<NewsItem["category"], string> = {
    // High priority - Warm/Strong colors
    digital_transformation: "bg-purple-50 text-purple-700 border-purple-200",
    catalog_expansion: "bg-red-50 text-red-700 border-red-200",
    ecommerce_growth: "bg-emerald-50 text-emerald-700 border-emerald-200",
    visual_content_strategy: "bg-pink-50 text-pink-700 border-pink-200",
    supply_chain_challenges: "bg-orange-50 text-orange-700 border-orange-200",
    international_expansion: "bg-rose-50 text-rose-700 border-rose-200",
    time_to_market: "bg-amber-50 text-amber-700 border-amber-200",
    large_catalog_operations: "bg-red-50 text-red-600 border-red-200",
    // Medium priority - Purple/Blue
    omnichannel_strategy: "bg-violet-50 text-violet-700 border-violet-200",
    product_customization: "bg-purple-50 text-purple-600 border-purple-200",
    private_label: "bg-indigo-50 text-indigo-700 border-indigo-200",
    technology_innovation: "bg-blue-50 text-blue-700 border-blue-200",
    product_innovation: "bg-pink-50 text-pink-600 border-pink-200",
    sustainability_initiative: "bg-green-50 text-green-700 border-green-200",
    partnership: "bg-cyan-50 text-cyan-700 border-cyan-200",
    // Supporting - Neutral
    cost_optimization: "bg-slate-50 text-slate-700 border-slate-200",
    merger_acquisition: "bg-zinc-50 text-zinc-700 border-zinc-200",
    platform_migration: "bg-neutral-50 text-neutral-700 border-neutral-200",
    marketing_campaigns: "bg-stone-50 text-stone-700 border-stone-200",
    ai_adoption: "bg-gray-50 text-gray-700 border-gray-200",
    visual_content: "bg-blue-50 text-blue-700 border-blue-200",
    ai_investment: "bg-violet-50 text-violet-700 border-violet-200",
    hiring: "bg-amber-50 text-amber-600 border-amber-200",
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-sm font-semibold text-neutral-900 pr-6">
            {news.title}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-3">
          {/* Metadata */}
          <div className="flex items-center flex-wrap gap-2 text-xs">
            <Badge 
              variant="outline" 
              className={cn(
                "text-[10px] font-medium border h-5",
                categoryColors[news.category]
              )}
            >
              {categoryLabels[news.category]}
            </Badge>
            <div className="flex items-center gap-1 text-neutral-500 text-[10px]">
              <Calendar className="w-3 h-3" />
              {new Date(news.published_date).toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
              })}
            </div>
            <span className="text-neutral-300">•</span>
            <span className="text-neutral-600 font-medium text-[10px]">{news.source}</span>
          </div>

          {/* Full Summary */}
          <div>
            <h4 className="text-[10px] font-semibold text-neutral-700 mb-1.5">Summary</h4>
            <p className="text-xs text-neutral-600 leading-relaxed">
              {news.summary}
            </p>
          </div>

          {/* Sales Insights */}
          {(news.relevance_reason || (news.key_insights && news.key_insights.length > 0)) && (
            <div className="bg-violet-50 border border-violet-200 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <Lightbulb className="w-3.5 h-3.5 text-violet-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-[10px] font-semibold text-violet-900 mb-2">
                    Sales Insights
                  </h4>
                  
                  {/* Main relevance reason */}
                  {news.relevance_reason && (
                    <p className="text-xs text-violet-700 leading-relaxed mb-2.5">
                      {news.relevance_reason}
                    </p>
                  )}
                  
                  {/* Key insights as bullets */}
                  {news.key_insights && news.key_insights.length > 0 && (
                    <ul className="space-y-1.5">
                      {news.key_insights.map((insight, idx) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-violet-600 mt-0.5">•</span>
                          <span className="flex-1 text-xs text-violet-700 leading-relaxed">{insight}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Action Button */}
          <div className="pt-3 border-t border-neutral-200">
            <a
              href={news.url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full"
            >
              <Button className="w-full bg-black hover:bg-neutral-800 text-white text-xs h-8">
                <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
                Read full article on {news.source}
              </Button>
            </a>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

