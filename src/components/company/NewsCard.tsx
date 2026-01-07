"use client";

import { NewsItem } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

interface NewsCardProps {
  news: NewsItem;
  onClick?: () => void;
}

export function NewsCard({ news, onClick }: NewsCardProps) {
  const categoryLabels: Record<NewsItem["category"], string> = {
    // High priority (🔥)
    digital_transformation: "Digital Transform",
    catalog_expansion: "Catalog Expansion",
    ecommerce_growth: "E-commerce",
    visual_content_strategy: "Visual Strategy",
    supply_chain_challenges: "Supply Chain",
    international_expansion: "International",
    time_to_market: "Time-to-Market",
    large_catalog_operations: "Large Catalog",
    // Medium priority (💡)
    omnichannel_strategy: "Omnichannel",
    product_customization: "Customization",
    private_label: "Private Label",
    technology_innovation: "Tech Innovation",
    product_innovation: "Innovation",
    sustainability_initiative: "Sustainability",
    partnership: "Partnership",
    // Supporting (🔍)
    cost_optimization: "Cost Optimization",
    merger_acquisition: "M&A",
    platform_migration: "Platform",
    marketing_campaigns: "Marketing",
    ai_adoption: "AI Adoption",
    visual_content: "Visual",
    ai_investment: "AI",
    hiring: "Hiring",
  };

  // Color coding based on priority: High = Red/Orange/Purple, Medium = Purple/Blue, Supporting = Neutral/Gray
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
    // Medium priority - Purple/Blue colors
    omnichannel_strategy: "bg-violet-50 text-violet-700 border-violet-200",
    product_customization: "bg-purple-50 text-purple-600 border-purple-200",
    private_label: "bg-indigo-50 text-indigo-700 border-indigo-200",
    technology_innovation: "bg-blue-50 text-blue-700 border-blue-200",
    product_innovation: "bg-pink-50 text-pink-600 border-pink-200",
    sustainability_initiative: "bg-green-50 text-green-700 border-green-200",
    partnership: "bg-cyan-50 text-cyan-700 border-cyan-200",
    // Supporting - Neutral/Gray colors
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
    <Card 
      className={cn(
        "p-3 hover:shadow-md transition-all cursor-pointer border-neutral-200 bg-white",
        onClick && "hover:border-violet-300"
      )}
      onClick={onClick}
    >
      {/* Title */}
      <h3 className="font-semibold text-xs text-neutral-900 line-clamp-2 mb-2">
        {news.title}
      </h3>

      {/* Source, Category Badge & Date */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] font-medium text-neutral-600">{news.source}</span>
        
        {/* Category Badge - right after source */}
        <Badge 
          variant="outline" 
          className={cn(
            "text-[9px] font-medium border h-4 px-1.5",
            categoryColors[news.category]
          )}
        >
          {categoryLabels[news.category]}
        </Badge>
        
        {news.published_date && (
          <>
            <span className="text-neutral-300">•</span>
            <div className="flex items-center gap-0.5 text-[9px] text-neutral-500">
              <Calendar className="w-2.5 h-2.5" />
              {new Date(news.published_date).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
              })}
            </div>
          </>
        )}
      </div>

      {/* Summary */}
      <p className="text-[10px] text-neutral-600 line-clamp-3 leading-relaxed">
        {news.summary}
      </p>
    </Card>
  );
}

