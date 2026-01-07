"use client";

import { useMemo } from "react";
import { Job } from "@/lib/types";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from "recharts";

interface HiringTrendsChartProps {
  jobs: Job[];
  onCategoryClick?: (category: string) => void;
}

// Categorize jobs into 5 main categories (excluding Leadership)
const categorizeJob = (job: Job): 'sales' | 'marketing' | 'ecommerce' | 'retail' | 'creative' | 'other' => {
  const title = job.job_title.toLowerCase();
  const text = `${job.job_title} ${job.description}`.toLowerCase();
  
  // Skip Leadership roles
  if (title.includes('director') || title.includes('vp') || title.includes('vice president') ||
      title.includes('chief') || title.includes('head of') || title.includes('president')) {
    return 'other'; // Exclude from chart
  }
  
  // Sales
  if (title.includes('sales') || title.includes('account manager') || title.includes('business development')) {
    return 'sales';
  }
  
  // E-commerce
  if (text.includes('ecommerce') || text.includes('e-commerce') || 
      text.includes('digital commerce') || text.includes('online commerce')) {
    return 'ecommerce';
  }
  
  // Retail
  if (title.includes('retail') || title.includes('store') || title.includes('showroom') ||
      title.includes('merchandis') || title.includes('category manager')) {
    return 'retail';
  }
  
  // Creative (includes design, content, production)
  if (title.includes('creative') || title.includes('design') || title.includes('art director') || 
      title.includes('graphic') || title.includes('visual designer') ||
      title.includes('content') || title.includes('production') ||
      title.includes('photo') || title.includes('video') ||
      title.includes('producer') || title.includes('3d')) {
    return 'creative';
  }
  
  // Marketing (includes brand, digital marketing, growth)
  if (title.includes('marketing') || title.includes('brand') ||
      title.includes('growth') || title.includes('digital marketing') ||
      title.includes('performance marketing') || title.includes('sem') || title.includes('seo') ||
      title.includes('paid media') || title.includes('campaign')) {
    return 'marketing';
  }
  
  return 'other';
};

export function HiringTrendsChart({ jobs, onCategoryClick }: HiringTrendsChartProps) {
  const { chartData, categoryTotals } = useMemo(() => {
    // Group jobs by month
    const monthlyData: Record<string, { sales: number; marketing: number; ecommerce: number; retail: number; creative: number }> = {};
    const totals = { sales: 0, marketing: 0, ecommerce: 0, retail: 0, creative: 0 };
    
    jobs.forEach(job => {
      // Use date field
      const dateStr = job.date;
      if (!dateStr) return;
      
      // Parse date and get month
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return;
      
      const monthKey = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = { sales: 0, marketing: 0, ecommerce: 0, retail: 0, creative: 0 };
      }
      
      const category = categorizeJob(job);
      if (category !== 'other') {
        monthlyData[monthKey][category]++;
        totals[category]++;
      }
    });
    
    // Convert to array and sort by date
    const sortedData = Object.entries(monthlyData)
      .map(([month, counts]) => ({
        month,
        sales: counts.sales,
        marketing: counts.marketing,
        ecommerce: counts.ecommerce,
        retail: counts.retail,
        creative: counts.creative,
        date: new Date(month)
      }))
      .sort((a, b) => a.date.getTime() - b.date.getTime())
      .map(({ date, ...rest }) => rest);
    
    return { chartData: sortedData, categoryTotals: totals };
  }, [jobs]);

  if (chartData.length === 0) {
    return (
      <div className="space-y-3 mb-4">
        <h2 className="text-sm font-medium text-neutral-900">Hiring Trends Over Last 3 Months</h2>
        <div className="border border-neutral-200 rounded-lg bg-white p-6">
          <p className="text-xs text-neutral-500">No data available for visualization</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 mb-4">
      <h2 className="text-sm font-medium text-neutral-900">Hiring Trends Over Last 3 Months</h2>
      
      <div className="border border-neutral-200 rounded-lg bg-white shadow-sm p-4">
        <ResponsiveContainer width="100%" height={250}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 20, left: -20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-neutral-100" />
          <XAxis dataKey="month" axisLine={false} tickLine={false} className="text-xs text-neutral-500" />
          <YAxis allowDecimals={false} axisLine={false} tickLine={false} className="text-xs text-neutral-500" />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e5e5',
              borderRadius: '8px',
              padding: '8px 12px',
              fontSize: '12px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
            }}
            cursor={{ strokeDasharray: '3 3' }}
          />
          {categoryTotals.marketing > 0 && (
            <Line
              type="monotone"
              dataKey="marketing"
              name="Marketing"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          )}
          {categoryTotals.ecommerce > 0 && (
            <Line
              type="monotone"
              dataKey="ecommerce"
              name="E-commerce"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          )}
          {categoryTotals.retail > 0 && (
            <Line
              type="monotone"
              dataKey="retail"
              name="Retail"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          )}
          {categoryTotals.creative > 0 && (
            <Line
              type="monotone"
              dataKey="creative"
              name="Creative"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          )}
          {categoryTotals.sales > 0 && (
            <Line
              type="monotone"
              dataKey="sales"
              name="Sales"
              stroke="#ef4444"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      
        {/* Custom Legend - shows all categories with job counts */}
        <div className="flex flex-wrap justify-center gap-4 mt-3">
          {[
            { key: 'marketing', name: 'Marketing', color: '#8b5cf6', total: categoryTotals.marketing },
            { key: 'ecommerce', name: 'E-commerce', color: '#3b82f6', total: categoryTotals.ecommerce },
            { key: 'retail', name: 'Retail', color: '#f59e0b', total: categoryTotals.retail },
            { key: 'creative', name: 'Creative', color: '#10b981', total: categoryTotals.creative },
            { key: 'sales', name: 'Sales', color: '#ef4444', total: categoryTotals.sales },
          ].map((category) => (
            <button
              key={category.key}
              onClick={() => onCategoryClick?.(category.key)}
              className="flex items-center gap-1.5 text-xs hover:opacity-80 transition-opacity cursor-pointer"
              style={{
                opacity: category.total > 0 ? 1 : 0.4,
                color: category.total > 0 ? '#374151' : '#9ca3af'
              }}
            >
              <div
                className="w-3 h-0.5 rounded"
                style={{ backgroundColor: category.color }}
              />
              <span>{category.name}</span>
              <span className="font-semibold">({category.total})</span>
            </button>
          ))}
        </div>
      
        <p className="text-xs text-neutral-500 mt-2 text-center">
          Click on a category to filter jobs below
        </p>
      </div>
    </div>
  );
}
