"use client";

import { ManagementInterviewItem } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Calendar, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface ManagementInterviewCardProps {
  item: ManagementInterviewItem;
  onClick?: () => void;
}

export function ManagementInterviewCard({ item, onClick }: ManagementInterviewCardProps) {
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

      {/* Source, Date & Executive Info on one line */}
      <div className="flex items-center gap-2">
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
        <span className="text-neutral-300">•</span>
        <div className="flex items-center gap-1">
          <User className="w-2.5 h-2.5 text-neutral-400" />
          <span className="text-[10px] font-medium text-neutral-900">{item.executive_name}</span>
        </div>
        <span className="text-neutral-300">•</span>
        <span className="text-[10px] text-neutral-600">{item.executive_title}</span>
      </div>

    </Card>
  );
}
