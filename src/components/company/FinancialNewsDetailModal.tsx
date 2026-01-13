"use client";

import { FinancialItem } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Calendar, ExternalLink, TrendingUp, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

interface FinancialNewsDetailModalProps {
  item: FinancialItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export function FinancialNewsDetailModal({ item, isOpen, onClose }: FinancialNewsDetailModalProps) {
  if (!item) return null;

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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold text-neutral-900 pr-8">
            {item.title}
          </DialogTitle>
        </DialogHeader>

        {/* Meta Information */}
        <div className="space-y-3">
          {/* Badges Row */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Period Badge */}
            <Badge 
              variant="outline" 
              className="text-[10px] font-medium border bg-neutral-50 text-neutral-700 border-neutral-200"
            >
              {item.period}
            </Badge>

            {/* Document Type */}
            <Badge 
              variant="outline"
              className={cn(
                "text-[10px] font-medium border",
                documentTypeColors[item.document_type]
              )}
            >
              {documentTypeLabels[item.document_type]}
            </Badge>

            {/* Category */}
            <Badge 
              variant="outline"
              className="text-[10px] font-medium border bg-slate-50 text-slate-700 border-slate-200"
            >
              {categoryLabels[item.category]}
            </Badge>

            {/* Relevance Score */}
            <Badge 
              variant="outline"
              className={cn(
                "text-[10px] font-bold border",
                item.relevance_score >= 8 
                  ? "bg-green-50 text-green-700 border-green-200"
                  : item.relevance_score >= 6
                  ? "bg-amber-50 text-amber-700 border-amber-200"
                  : "bg-neutral-100 text-neutral-600 border-neutral-200"
              )}
            >
              Score: {item.relevance_score}/10
            </Badge>
          </div>

          {/* Source, Date, Link */}
          <div className="flex items-center gap-3 text-xs text-neutral-600">
            <span className="font-medium">{item.source}</span>
            {item.published_date && (
              <>
                <span className="text-neutral-300">•</span>
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {new Date(item.published_date).toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </div>
              </>
            )}
            <span className="text-neutral-300">•</span>
            <a 
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-emerald-600 hover:text-emerald-700 font-medium"
            >
              View Source
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          {/* Summary */}
          <div className="pt-3 border-t border-neutral-200">
            <p className="text-xs text-neutral-700 leading-relaxed">
              {item.summary}
            </p>
          </div>

          {/* Key Metrics */}
          {item.key_metrics && item.key_metrics.length > 0 && (
            <div className="pt-3 border-t border-neutral-200">
              <h4 className="text-xs font-semibold text-neutral-900 mb-2 flex items-center gap-1.5">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                Key Financial Metrics
              </h4>
              <div className="space-y-1.5">
                {item.key_metrics.map((metric, idx) => (
                  <div 
                    key={idx} 
                    className="flex items-start gap-2 text-xs text-neutral-700 bg-emerald-50 border border-emerald-200 rounded p-2"
                  >
                    <span className="text-emerald-600 font-bold mt-0.5">▸</span>
                    <span className="flex-1 font-medium">{metric}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Strategic Highlights */}
          {item.strategic_highlights && item.strategic_highlights.length > 0 && (
            <div className="pt-3 border-t border-neutral-200">
              <h4 className="text-xs font-semibold text-neutral-900 mb-2 flex items-center gap-1.5">
                <Lightbulb className="w-3.5 h-3.5 text-violet-600" />
                Strategic Highlights
              </h4>
              <ul className="space-y-1.5">
                {item.strategic_highlights.map((highlight, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-neutral-700">
                    <span className="text-violet-600 mt-0.5">•</span>
                    <span className="flex-1">{highlight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
