"use client";

import { FinancialItem } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Calendar, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface FinancialNewsCardProps {
  item: FinancialItem;
  onClick?: () => void;
}

export function FinancialNewsCard({ item, onClick }: FinancialNewsCardProps) {
  const documentTypeLabels: Record<FinancialItem["document_type"], string> = {
    earnings_call: "Earnings Call",
    sec_filing: "SEC Filing",
    quarterly_results: "Quarterly Results",
    press_release: "Press Release",
    analyst_report: "Analyst Report"
  };

  const documentTypeColors: Record<FinancialItem["document_type"], string> = {
    earnings_call: "bg-violet-50 text-violet-700 border-violet-200",
    sec_filing: "bg-blue-50 text-blue-700 border-blue-200",
    quarterly_results: "bg-emerald-50 text-emerald-700 border-emerald-200",
    press_release: "bg-amber-50 text-amber-700 border-amber-200",
    analyst_report: "bg-purple-50 text-purple-700 border-purple-200"
  };

  const categoryLabels: Record<FinancialItem["category"], string> = {
    earnings: "Earnings",
    financial_performance: "Financial Performance",
    guidance: "Guidance",
    sec_filing: "SEC Filing",
    analyst_coverage: "Analyst Coverage"
  };

  const categoryColors: Record<FinancialItem["category"], string> = {
    earnings: "bg-violet-50 text-violet-700 border-violet-200",
    financial_performance: "bg-emerald-50 text-emerald-700 border-emerald-200",
    guidance: "bg-amber-50 text-amber-700 border-amber-200",
    sec_filing: "bg-blue-50 text-blue-700 border-blue-200",
    analyst_coverage: "bg-purple-50 text-purple-700 border-purple-200"
  };

  return (
    <Card 
      className={cn(
        "p-3 hover:shadow-md transition-all cursor-pointer border-neutral-200 bg-white",
        onClick && "hover:border-emerald-300"
      )}
      onClick={onClick}
    >
      {/* Title */}
      <h3 className="font-semibold text-xs text-neutral-900 line-clamp-2 mb-2">
        {item.title}
      </h3>

      {/* Source, Period, Document Type & Date */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-[10px] font-medium text-neutral-600">{item.source}</span>
        
        {/* Period Badge */}
        <Badge 
          variant="outline" 
          className="text-[9px] font-medium border h-4 px-1.5 bg-neutral-50 text-neutral-700 border-neutral-200"
        >
          {item.period}
        </Badge>

        {/* Document Type Badge */}
        <Badge 
          variant="outline" 
          className={cn(
            "text-[9px] font-medium border h-4 px-1.5",
            documentTypeColors[item.document_type]
          )}
        >
          {documentTypeLabels[item.document_type]}
        </Badge>
        
        {item.published_date && (
          <>
            <span className="text-neutral-300">•</span>
            <div className="flex items-center gap-0.5 text-[9px] text-neutral-500">
              <Calendar className="w-2.5 h-2.5" />
              {new Date(item.published_date).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
              })}
            </div>
          </>
        )}
      </div>
    </Card>
  );
}
