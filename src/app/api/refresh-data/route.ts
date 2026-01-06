import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";
import fs from "fs/promises";

const execAsync = promisify(exec);

// Helper function to escape shell arguments
function escapeShellArg(arg: string): string {
  return `'${arg.replace(/'/g, "'\\''")}'`;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { companyName, dataType, period, days } = body;

    if (!companyName || !dataType || !period || !days) {
      return NextResponse.json(
        { error: "Missing required parameters" },
        { status: 400 }
      );
    }

    // Validate dataType
    if (dataType !== "news" && dataType !== "interviews") {
      return NextResponse.json(
        { error: "Invalid dataType. Must be 'news' or 'interviews'" },
        { status: 400 }
      );
    }

    // Path to database directory
    const databaseDir = path.join(process.cwd(), "database");
    
    // Determine which script to run
    const scriptName =
      dataType === "news"
        ? "scrape_company_news_async.py"
        : "scrape_management_interviews.py";
    
    const scriptPath = path.join(databaseDir, scriptName);

    // Check if script exists
    try {
      await fs.access(scriptPath);
    } catch {
      return NextResponse.json(
        { error: `Script not found: ${scriptName}` },
        { status: 404 }
      );
    }

    // Prepare file paths for later use
    const testFileName =
      dataType === "news"
        ? "company_news_test.json"
        : "management_interviews_test.json";
    
    const outputFileName =
      dataType === "news"
        ? "news_data.json"
        : "management_interviews.json";
    
    const sourceFile = path.join(databaseDir, testFileName);
    const destFile = path.join(process.cwd(), "public", outputFileName);

    // Activate virtual environment and run the script
    const pythonPath = path.join(databaseDir, "venv_async", "bin", "python");

    // Run the scraping script with parameters - escape all paths with spaces
    const command = `cd ${escapeShellArg(databaseDir)} && ${escapeShellArg(pythonPath)} ${escapeShellArg(scriptPath)} --company ${escapeShellArg(companyName)} --days ${days}`;

    console.log(`[API] Running command: ${command}`);
    console.log(`[API] Company: ${companyName}, DataType: ${dataType}, Days: ${days}`);
    console.log(`[API] Will look for source file: ${sourceFile}`);

    const { stdout, stderr } = await execAsync(command, {
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      timeout: 120000, // 2 minutes timeout
    });

    if (stderr && !stderr.includes("DeprecationWarning")) {
      console.error(`[API] Script stderr:`, stderr);
    }

    console.log(`[API] Script stdout:`, stdout);

    // After successful scraping, merge with existing data

    try {
      // Read the new data from the test file
      const newDataRaw = await fs.readFile(sourceFile, 'utf-8');
      const newData = JSON.parse(newDataRaw);
      
      // Read existing data from public directory
      let existingData: any = {};
      try {
        const existingDataRaw = await fs.readFile(destFile, 'utf-8');
        existingData = JSON.parse(existingDataRaw);
      } catch {
        console.log(`[API] No existing data found, will create new file`);
      }

      // Merge the data for the specific company
      const companyData = newData[companyName];
      if (!companyData) {
        throw new Error(`No data found for company: ${companyName}`);
      }

      // Get existing items for this company
      const existingCompanyData = existingData[companyName];
      const itemsKey = dataType === "news" ? "news_items" : "management_items";
      const existingItems = existingCompanyData?.[itemsKey] || [];
      const newItems = companyData[itemsKey] || [];

      // Merge: keep existing items and add new ones that don't exist
      // Use URL as unique identifier to avoid duplicates
      const existingUrls = new Set(existingItems.map((item: any) => item.url));
      const uniqueNewItems = newItems.filter((item: any) => !existingUrls.has(item.url));

      // Combine and sort by date (newest first)
      const mergedItems = [...existingItems, ...uniqueNewItems].sort((a: any, b: any) => {
        const dateA = new Date(a.published_date).getTime();
        const dateB = new Date(b.published_date).getTime();
        return dateB - dateA; // Descending order
      });

      // Merge key_executives_identified (for management interviews)
      let mergedExecutives = existingCompanyData?.key_executives_identified || [];
      if (dataType === "interviews" && companyData.key_executives_identified) {
        const existingExecMap = new Map(mergedExecutives.map((e: any) => [e.name, e]));
        const newExecsData = companyData.key_executives_identified || [];
        
        // Process each executive from new data
        newExecsData.forEach((newExec: any) => {
          const existingExec: any = existingExecMap.get(newExec.name);
          
          if (existingExec) {
            // Executive exists - update their data
            existingExecMap.set(newExec.name, {
              ...existingExec,
              title: newExec.title || existingExec.title, // Update title if changed
              relevance: newExec.relevance || existingExec.relevance, // Update relevance
              content_count: (existingExec.content_count || 0) + (newExec.content_count || 0), // Add counts
            });
          } else {
            // New executive - add to map
            existingExecMap.set(newExec.name, newExec);
          }
        });
        
        // Convert map back to array
        mergedExecutives = Array.from(existingExecMap.values());
        
        console.log(`[API] Merged executives: ${mergedExecutives.length} total (${newExecsData.length} in new data)`);
      }

      // Build merged company data - preserve ALL existing structure
      const mergedCompanyData = {
        ...(existingCompanyData || {}),  // Start with existing data (preserves everything)
        company_name: companyData.company_name || existingCompanyData?.company_name || companyName,
        [itemsKey]: mergedItems,  // Use merged items
        search_date: new Date().toISOString().split('T')[0], // Update search date
        scrape_metadata: companyData.scrape_metadata || existingCompanyData?.scrape_metadata,
      };

      // For management interviews, preserve and merge metadata
      if (dataType === "interviews") {
        // Update executives (merged)
        if (mergedExecutives.length > 0) {
          mergedCompanyData.key_executives_identified = mergedExecutives;
        } else if (existingCompanyData?.key_executives_identified) {
          // Keep existing executives if no new ones found
          mergedCompanyData.key_executives_identified = existingCompanyData.key_executives_identified;
        }
        
        // Preserve overall_assessment (don't override unless new data is better)
        if (companyData.overall_assessment) {
          mergedCompanyData.overall_assessment = companyData.overall_assessment;
        } else if (existingCompanyData?.overall_assessment) {
          mergedCompanyData.overall_assessment = existingCompanyData.overall_assessment;
        }
      }

      // For company news, preserve overall_assessment too
      if (dataType === "news") {
        if (companyData.overall_assessment) {
          mergedCompanyData.overall_assessment = companyData.overall_assessment;
        } else if (existingCompanyData?.overall_assessment) {
          mergedCompanyData.overall_assessment = existingCompanyData.overall_assessment;
        }
      }

      // Update the full data object
      existingData[companyName] = mergedCompanyData;

      // Write back to public directory
      await fs.writeFile(destFile, JSON.stringify(existingData, null, 2), 'utf-8');
      console.log(`[API] Merged and saved ${outputFileName} to public directory`);
      console.log(`[API] Added ${uniqueNewItems.length} new items (${existingItems.length} existing, ${newItems.length} found)`);

      return NextResponse.json({
        success: true,
        message: `Successfully refreshed ${dataType} for ${companyName}`,
        period,
        days,
        stats: {
          newItemsCount: uniqueNewItems.length,
          existingItemsCount: existingItems.length,
          totalItemsCount: mergedItems.length,
        },
      });
    } catch (copyError) {
      console.error(`[API] Error merging/copying file:`, copyError);
      return NextResponse.json(
        { error: "Script ran but failed to update frontend data", details: String(copyError) },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error("[API] Error refreshing data:", error);
    return NextResponse.json(
      {
        error: "Failed to refresh data",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}

