"use client";

import { Job } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ExternalLink, MapPin, Calendar, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface JobDetailModalProps {
  job: Job | null;
  jobNotes: { label: string; color: string; snippet?: string }[];
  onClose: () => void;
}

// Function to parse and structure job description
function parseJobDescription(description: string) {
  const sections = [];
  
  // Common section headers
  const sectionHeaders = [
    'Company Description',
    'Job Description',
    'Duties And Responsibilities',
    'Responsibilities',
    'Qualifications',
    'Requirements',
    'Additional Information',
    'What We Offer',
    'Benefits',
    'About Us',
    'About the Role',
    'About the Company'
  ];
  
  let currentText = description;
  let lastIndex = 0;
  
  // Find all section headers and their positions
  const foundSections: { header: string; index: number }[] = [];
  
  sectionHeaders.forEach(header => {
    const index = currentText.indexOf(header);
    if (index !== -1) {
      foundSections.push({ header, index });
    }
  });
  
  // Sort by position
  foundSections.sort((a, b) => a.index - b.index);
  
  if (foundSections.length === 0) {
    // No sections found, return as single block
    return [{ title: null, content: description }];
  }
  
  // Extract sections
  foundSections.forEach((section, i) => {
    const nextSection = foundSections[i + 1];
    const start = section.index;
    const end = nextSection ? nextSection.index : currentText.length;
    
    const content = currentText.slice(start + section.header.length, end).trim();
    sections.push({
      title: section.header,
      content: content
    });
  });
  
  // Add any text before first section
  if (foundSections[0].index > 0) {
    const intro = currentText.slice(0, foundSections[0].index).trim();
    if (intro) {
      sections.unshift({ title: null, content: intro });
    }
  }
  
  return sections;
}

export function JobDetailModal({ job, jobNotes, onClose }: JobDetailModalProps) {
  if (!job) return null;

  const score = job.analysis?.relevance_score || 0;
  const sections = parseJobDescription(job.description || "No description available");
  
  // Check if job is AI-related
  const hasAINote = jobNotes.some(note => note.label === 'AI-related');
  
  // AI patterns for highlighting (same as in OverviewTab)
  const aiPatterns = [
    /\bAI\b/gi,
    /\bA\.I\./gi,
    /\bartificial intelligence\b/gi,
    /\bAI[\s-]tools?\b/gi,
    /\bAI[\s-]powered\b/gi,
    /\bAI[\s-]driven\b/gi,
    /\bAI[\s-]generated?\b/gi,
    /\bAI[\s-]generation\b/gi,
    /\bAI[\s-]use\b/gi,
    /\bAI[\s-]based\b/gi,
    /\bAI[\s-]enabled\b/gi,
    /\bgenerate with AI\b/gi,
    /\busing AI\b/gi,
    /\bleverage AI\b/gi,
    /\bAI solutions?\b/gi,
    /\bAI technologies\b/gi,
    /\bAI systems?\b/gi,
    /\bmachine learning\b/gi,
    /\bdeep learning\b/gi,
    /\bgenerative AI\b/gi,
  ];
  
  // Function to highlight AI keywords in text
  const highlightAIKeywords = (text: string) => {
    if (!hasAINote || !text) return text;
    
    let result: (string | JSX.Element)[] = [text];
    
    // Apply each pattern
    aiPatterns.forEach((pattern) => {
      const newResult: (string | JSX.Element)[] = [];
      
      result.forEach((part, idx) => {
        // Only process strings, not already highlighted parts
        if (typeof part === 'string') {
          const matches = [...part.matchAll(pattern)];
          
          if (matches.length > 0) {
            let lastIndex = 0;
            
            matches.forEach((match, matchIdx) => {
              const matchIndex = match.index!;
              const matchText = match[0];
              
              // Add text before match
              if (matchIndex > lastIndex) {
                newResult.push(part.slice(lastIndex, matchIndex));
              }
              
              // Add highlighted match
              newResult.push(
                <span 
                  key={`${idx}-${matchIdx}-${matchIndex}`} 
                  className="bg-purple-100 text-purple-900 px-2 py-1 rounded border-2 border-purple-400 font-medium"
                >
                  {matchText}
                </span>
              );
              
              lastIndex = matchIndex + matchText.length;
            });
            
            // Add remaining text after last match
            if (lastIndex < part.length) {
              newResult.push(part.slice(lastIndex));
            }
          } else {
            newResult.push(part);
          }
        } else {
          newResult.push(part);
        }
      });
      
      result = newResult;
    });
    
    return <>{result}</>;
  };

  return (
    <Dialog open={!!job} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-3xl max-h-[85vh] p-0">
        <DialogHeader className="p-4 pb-3 border-b border-neutral-200">
          <div className="flex items-start justify-between gap-3">
            <div>
              <DialogTitle className="text-base font-semibold text-neutral-900">
                {job.job_title}
              </DialogTitle>
              <div className="flex items-center gap-2.5 mt-1.5 text-xs text-neutral-500">
                <div className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {job.location || "N/A"}
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {(job.date_creation || job.date)?.slice(0, 10) || "N/A"}
                </div>
                <div className={cn(
                  "flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
                  score >= 8 ? "bg-green-50 text-green-700" :
                  score >= 6 ? "bg-amber-50 text-amber-700" :
                  "bg-neutral-100 text-neutral-600"
                )}>
                  <TrendingUp className="w-3 h-3" />
                  {score}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <a href={job.job_board_url || job.job_url} target="_blank" rel="noopener noreferrer">
                <Button size="sm" className="gap-1.5 h-7 text-xs">
                  <ExternalLink className="w-3 h-3" />
                  Original
                </Button>
              </a>
            </div>
          </div>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh]">
          <div className="p-4 space-y-4">
            {/* Structured Description */}
            {sections.map((section, index) => (
              <div key={index}>
                {section.title && (
                  <h3 className="text-sm font-semibold text-neutral-900 mb-2 pb-1 border-b border-neutral-200">
                    {section.title}
                  </h3>
                )}
                <div className={cn(
                  "text-xs text-neutral-700 leading-relaxed whitespace-pre-wrap",
                  !section.title && "bg-neutral-50 rounded-lg p-3"
                )}>
                  {highlightAIKeywords(section.content)}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}

