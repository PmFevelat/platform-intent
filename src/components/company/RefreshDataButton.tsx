"use client";

import { useState } from "react";
import { RefreshCw, Calendar } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

interface RefreshDataButtonProps {
  companyName: string;
  dataType: "news" | "interviews";
  onRefreshComplete?: (stats: { newItemsCount: number; existingItemsCount: number; totalItemsCount: number }) => void;
}

interface RefreshStats {
  newItemsCount: number;
  existingItemsCount: number;
  totalItemsCount: number;
}

export function RefreshDataButton({ companyName, dataType, onRefreshComplete }: RefreshDataButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [refreshStats, setRefreshStats] = useState<RefreshStats | null>(null);

  const periods = [
    { label: "Last 7 days", value: "7d", days: 7 },
    { label: "Last 30 days", value: "30d", days: 30 },
    { label: "Last 3 months", value: "90d", days: 90 },
    { label: "Last 6 months", value: "180d", days: 180 },
  ];

  const handleRefresh = async () => {
    if (!selectedPeriod) return;
    
    setIsRefreshing(true);
    setError(null);

    try {
      const periodData = periods.find(p => p.value === selectedPeriod);
      const requestBody = {
        companyName,
        dataType,
        period: selectedPeriod,
        days: periodData?.days || 7,
      };
      
      console.log("[RefreshData] Sending request:", requestBody);
      
      const response = await fetch("/api/refresh-data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const result = await response.json();

      if (!response.ok) {
        const errorMessage = result.details 
          ? `${result.error}: ${result.details}` 
          : result.error || "Failed to refresh data";
        throw new Error(errorMessage);
      }

      console.log("[RefreshData] Success:", result);

      // Success - show success modal
      setRefreshStats(result.stats);
      setShowSuccess(true);
      setIsOpen(false);
      
      // Call callback to refresh data without page reload
      if (onRefreshComplete && result.stats) {
        onRefreshComplete(result.stats);
      }
    } catch (err) {
      console.error("[RefreshData] Error:", err);
      const errorMessage = err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSelectPeriod = (periodValue: string) => {
    if (!isRefreshing) {
      setSelectedPeriod(periodValue);
      setError(null);
    }
  };

  return (
    <>
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <button
          className={cn(
            "px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors border inline-flex items-center gap-1.5",
            "bg-white text-violet-700 border-violet-300 hover:bg-violet-50"
          )}
        >
          <RefreshCw className="h-3 w-3" />
          Refresh
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[420px]">
        <DialogHeader className="pb-2">
          <DialogTitle className="flex items-center gap-2 text-sm font-semibold">
            <Calendar className="h-4 w-4" />
            Refresh {dataType === "news" ? "Company News" : "Management Interviews"}
          </DialogTitle>
          <DialogDescription className="text-xs text-neutral-500">
            Select a time period to search for new {dataType === "news" ? "articles" : "interviews"} about {companyName}.
            This will scan the web for recent content.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2 mt-2">
          {periods.map((period) => (
            <button
              key={period.value}
              onClick={() => handleSelectPeriod(period.value)}
              disabled={isRefreshing}
              className={cn(
                "w-full flex items-center justify-between px-3 py-2 rounded-md border transition-all text-left",
                "hover:border-violet-300 hover:bg-violet-50",
                selectedPeriod === period.value
                  ? "border-violet-400 bg-violet-50 ring-1 ring-violet-300"
                  : "border-gray-200",
                isRefreshing && "opacity-50 cursor-not-allowed"
              )}
            >
              <span className="font-medium text-xs">{period.label}</span>
              {selectedPeriod === period.value && (
                <div className="h-2 w-2 rounded-full bg-violet-500" />
              )}
            </button>
          ))}
        </div>

        {/* Start Button */}
        <button
          onClick={handleRefresh}
          disabled={!selectedPeriod || isRefreshing}
          className={cn(
            "w-full mt-3 px-3 py-2 rounded-md text-xs font-semibold transition-all",
            selectedPeriod && !isRefreshing
              ? "bg-violet-500 text-white hover:bg-violet-600"
              : "bg-gray-200 text-gray-400 cursor-not-allowed"
          )}
        >
          {isRefreshing ? (
            <span className="flex items-center justify-center gap-2">
              <RefreshCw className="h-3 w-3 animate-spin" />
              Refreshing...
            </span>
          ) : (
            "Start Refresh"
          )}
        </button>

        {error && (
          <div className="mt-2 p-2.5 bg-red-50 border border-red-300 rounded-md">
            <p className="text-xs text-red-700 font-medium break-words">{error}</p>
          </div>
        )}

        {isRefreshing && (
          <div className="mt-2 p-2 bg-violet-50 border border-violet-200 rounded-md">
            <p className="text-xs text-violet-600 flex items-center gap-2">
              <RefreshCw className="h-3 w-3 animate-spin" />
              Searching the web... This may take 30-60 seconds.
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>

      {/* Success Modal */}
      <Dialog open={showSuccess} onOpenChange={setShowSuccess}>
        <DialogContent className="sm:max-w-[380px]">
          <DialogHeader className="pb-2">
            <DialogTitle className="flex items-center gap-2 text-sm font-semibold text-green-700">
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              Refresh Complete
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-3 mt-2">
            {refreshStats && refreshStats.newItemsCount > 0 ? (
              <>
                <p className="text-xs text-neutral-600">
                  Found <span className="font-semibold text-green-600">{refreshStats.newItemsCount} new</span> {dataType === "news" ? "article" : "interview"}{refreshStats.newItemsCount > 1 ? "s" : ""} for <span className="font-semibold">{companyName}</span>
                </p>
                <div className="p-2.5 bg-green-50 border border-green-200 rounded-md">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-neutral-600">New items:</span>
                    <span className="font-semibold text-green-700">{refreshStats.newItemsCount}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] mt-1">
                    <span className="text-neutral-600">Total items:</span>
                    <span className="font-semibold text-neutral-700">{refreshStats.totalItemsCount}</span>
                  </div>
                </div>
              </>
            ) : (
              <>
                <p className="text-xs text-neutral-600">
                  No new {dataType === "news" ? "articles" : "interviews"} found for <span className="font-semibold">{companyName}</span>
                </p>
                <div className="p-2.5 bg-neutral-50 border border-neutral-200 rounded-md">
                  <p className="text-[11px] text-neutral-500">
                    All recent content is already in the database. Try selecting a longer time period.
                  </p>
                </div>
              </>
            )}

            <button
              onClick={() => setShowSuccess(false)}
              className="w-full mt-2 px-3 py-2 rounded-md text-xs font-semibold bg-violet-500 text-white hover:bg-violet-600 transition-colors"
            >
              Close
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

