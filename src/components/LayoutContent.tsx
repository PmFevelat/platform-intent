"use client";

import { Sidebar } from "@/components/Sidebar";
import { useSidebarState } from "@/lib/sidebar-state";
import { cn } from "@/lib/utils";

export function LayoutContent({ children }: { children: React.ReactNode }) {
  const { collapsed } = useSidebarState();

  return (
    <>
      {/* Left Sidebar - Fixed */}
      <Sidebar />
      
      {/* Main content - with margin for sidebar */}
      <main 
        className={cn(
          "min-h-screen transition-all duration-300 ease-in-out",
          collapsed ? "ml-[50px]" : "ml-[200px]"
        )}
      >
        {children}
      </main>
    </>
  );
}

