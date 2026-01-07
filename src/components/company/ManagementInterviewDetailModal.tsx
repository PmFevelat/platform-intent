"use client";

import { ManagementInterviewItem } from "@/lib/types";
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
  Lightbulb,
  User,
  MessageSquare
} from "lucide-react";

interface ManagementInterviewDetailModalProps {
  interview: ManagementInterviewItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ManagementInterviewDetailModal({ interview, isOpen, onClose }: ManagementInterviewDetailModalProps) {
  if (!interview) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-sm font-semibold text-neutral-900 pr-6">
            {interview.title}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-3">
          {/* Metadata */}
          <div className="flex items-center flex-wrap gap-2 text-xs">
            <div className="flex items-center gap-1 text-neutral-500 text-[10px]">
              <Calendar className="w-3 h-3" />
              {new Date(interview.published_date).toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
              })}
            </div>
            <span className="text-neutral-300">•</span>
            <span className="text-neutral-600 font-medium text-[10px]">{interview.source}</span>
          </div>

          {/* Executive Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-2.5">
            <div className="flex items-center gap-2">
              <User className="w-3.5 h-3.5 text-blue-600" />
              <div>
                <div className="text-xs font-semibold text-blue-900">
                  {interview.executive_name}
                </div>
                <div className="text-[10px] text-blue-700">
                  {interview.executive_title}
                </div>
              </div>
            </div>
          </div>

          {/* Full Summary */}
          <div>
            <h4 className="text-[10px] font-semibold text-neutral-700 mb-1.5">Summary</h4>
            <p className="text-xs text-neutral-600 leading-relaxed">
              {interview.summary}
            </p>
          </div>

          {/* Key Quotes */}
          {interview.key_quotes && interview.key_quotes.length > 0 && (
            <div>
              <h4 className="text-[10px] font-semibold text-neutral-700 mb-2 flex items-center gap-1">
                <MessageSquare className="w-3 h-3" />
                Key Quotes
              </h4>
              <div className="space-y-2">
                {interview.key_quotes.map((quote, idx) => (
                  <div
                    key={idx}
                    className="bg-neutral-50 border-l-2 border-blue-400 pl-3 pr-2 py-2 rounded"
                  >
                    <p className="text-xs italic text-neutral-700 leading-relaxed">
                      &ldquo;{quote}&rdquo;
                    </p>
                    <p className="text-[10px] text-neutral-500 mt-1">
                      — {interview.executive_name}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Topics Discussed */}
          {interview.topics_discussed && interview.topics_discussed.length > 0 && (
            <div>
              <h4 className="text-[10px] font-semibold text-neutral-700 mb-1.5">Topics Discussed</h4>
              <div className="flex flex-wrap gap-1.5">
                {interview.topics_discussed.map((topic, idx) => (
                  <Badge
                    key={idx}
                    variant="outline"
                    className="text-[9px] bg-neutral-50 border-neutral-200 text-neutral-700"
                  >
                    {topic}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Sales Insights */}
          {(interview.relevance_reason || (interview.sales_insights && interview.sales_insights.length > 0)) && (
            <div className="bg-violet-50 border border-violet-200 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <Lightbulb className="w-3.5 h-3.5 text-violet-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-[10px] font-semibold text-violet-900 mb-2">
                    Sales Insights
                  </h4>
                  
                  {/* Main relevance reason */}
                  {interview.relevance_reason && (
                    <p className="text-xs text-violet-700 leading-relaxed mb-2.5">
                      {interview.relevance_reason}
                    </p>
                  )}
                  
                  {/* Key insights as bullets */}
                  {interview.sales_insights && interview.sales_insights.length > 0 && (
                    <ul className="space-y-1.5">
                      {interview.sales_insights.map((insight, idx) => (
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
              href={interview.url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full"
            >
              <Button className="w-full bg-violet-600 hover:bg-violet-700 text-white text-xs h-8">
                <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
                View full interview on {interview.source}
              </Button>
            </a>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
