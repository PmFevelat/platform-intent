"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSidebarState } from "@/lib/sidebar-state";
import { 
  Briefcase, 
  Target, 
  ChevronLeft, 
  ChevronRight,
  PanelLeftClose,
  PanelLeft
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navigation = [
  {
    name: "Companies",
    href: "/jobs",
    icon: Briefcase,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { collapsed, toggle } = useSidebarState();

  return (
    <TooltipProvider delayDuration={0}>
      <aside 
        className={cn(
          "fixed left-0 top-0 h-screen border-r border-neutral-200 bg-white flex flex-col transition-all duration-300 ease-in-out z-50",
          collapsed ? "w-[50px]" : "w-[200px]"
        )}
      >
        {/* Logo */}
        <div className={cn(
          "px-3 py-2.5 border-b border-neutral-200 flex items-center h-[52px] relative group",
          collapsed ? "justify-center px-2" : "justify-between"
        )}>
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <Target className="w-3.5 h-3.5 text-white" />
            </div>
            {!collapsed && (
              <div className="overflow-hidden">
                <span className="font-semibold text-neutral-900 text-xs">presti.ai</span>
                <p className="text-[9px] text-neutral-400">Sales Intelligence</p>
              </div>
            )}
          </Link>

          {/* Collapse toggle on hover of header border */}
          <button
            onClick={toggle}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className={cn(
              "absolute -right-3 top-1/2 -translate-y-1/2 rounded-full border border-neutral-200 bg-white shadow-sm",
              "p-1 text-neutral-500 hover:text-neutral-800 hover:border-neutral-300 transition",
              "opacity-0 group-hover:opacity-100"
            )}
          >
            {collapsed ? (
              <PanelLeft className="w-3.5 h-3.5" />
            ) : (
              <PanelLeftClose className="w-3.5 h-3.5" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-1.5 pt-2">
          <div className="space-y-0.5">
            {navigation.map((item) => {
              const isActive = pathname.startsWith(item.href);
              
              if (collapsed) {
                return (
                  <Tooltip key={item.name}>
                    <TooltipTrigger asChild>
                      <Link
                        href={item.href}
                        className={cn(
                          "flex items-center justify-center p-2 rounded-md transition-colors",
                          isActive
                            ? "bg-neutral-100 text-neutral-900"
                            : "text-neutral-500 hover:bg-neutral-100/50 hover:text-neutral-900"
                        )}
                      >
                        <item.icon className="w-4 h-4" />
                      </Link>
                    </TooltipTrigger>
                    <TooltipContent side="right" sideOffset={10}>
                      {item.name}
                    </TooltipContent>
                  </Tooltip>
                );
              }
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors",
                    isActive
                      ? "bg-neutral-100 text-neutral-900"
                      : "text-neutral-600 hover:bg-neutral-100/50 hover:text-neutral-900"
                  )}
                >
                  <item.icon className="w-3.5 h-3.5" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>

      </aside>
    </TooltipProvider>
  );
}
