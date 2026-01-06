"use client";

import { ManagementInterviewItem } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface ManagementInterviewCardProps {
  item: ManagementInterviewItem;
  onClick?: () => void;
}

export function ManagementInterviewCard({ item, onClick }: ManagementInterviewCardProps) {
  // Format labels and colors
  const formatStyles: Record<string, string> = {
    interview: "bg-blue-50 text-blue-700 border-blue-200",
    podcast: "bg-purple-50 text-purple-700 border-purple-200",
    keynote: "bg-red-50 text-red-700 border-red-200",
    article: "bg-gray-50 text-gray-700 border-gray-200",
    panel: "bg-green-50 text-green-700 border-green-200",
    LinkedIn_post: "bg-indigo-50 text-indigo-700 border-indigo-200",
    webinar: "bg-cyan-50 text-cyan-700 border-cyan-200",
    profile: "bg-amber-50 text-amber-700 border-amber-200",
  };

  const formatLabels: Record<string, string> = {
    interview: "Interview",
    podcast: "Podcast",
    keynote: "Keynote",
    article: "Article",
    panel: "Panel",
    LinkedIn_post: "LinkedIn",
    webinar: "Webinar",
    profile: "Profile",
  };

  // Format date
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
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
        {item.title}
      </h3>

      {/* Executive Info */}
      <div className="flex items-center gap-2 mb-2">
        <div className="flex items-center gap-1">
          <User className="w-2.5 h-2.5 text-neutral-400" />
          <span className="text-[10px] font-medium text-neutral-900">{item.executive_name}</span>
        </div>
        <span className="text-neutral-300">•</span>
        <span className="text-[10px] text-neutral-600">{item.executive_title}</span>
      </div>

      {/* Source & Date */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] font-medium text-neutral-600">{item.source}</span>
        {item.published_date && (
          <>
            <span className="text-neutral-300">•</span>
            <div className="flex items-center gap-0.5 text-[9px] text-neutral-500">
              <Calendar className="w-2.5 h-2.5" />
              {formatDate(item.published_date)}
            </div>
          </>
        )}
      </div>

      {/* Format Badge */}
      <div className="mb-2">
        <Badge 
          variant="outline" 
          className={cn(
            "text-[9px] font-medium border h-4 px-1.5",
            formatStyles[item.format] || "bg-gray-50 text-gray-700 border-gray-200"
          )}
        >
          {formatLabels[item.format] || item.format}
        </Badge>
      </div>

      {/* Summary */}
      <p className="text-[10px] text-neutral-600 line-clamp-3 leading-relaxed">
        {item.summary}
      </p>
    </Card>
  );
}
