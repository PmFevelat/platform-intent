import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

interface ScrapingRequest {
  company: string;
  website: string;
  scriptType: 'companyNews' | 'managementInterviews' | 'jobOffers' | 'financialNews' | 'addToDatabase';
}

const SCRIPT_MAPPING = {
  companyNews: 'scrape_company_news_async.py',
  managementInterviews: 'scrape_management_interviews.py',
  jobOffers: 'analyze_jobs_detailed.py',
  financialNews: 'scrape_financial_news_async.py',
  addToDatabase: 'add_pet_care_companies.py'
};

export async function POST(request: NextRequest) {
  try {
    const body: ScrapingRequest = await request.json();
    const { company, website, scriptType } = body;

    if (!company || !website || !scriptType) {
      return NextResponse.json(
        { error: 'Paramètres manquants: company, website, et scriptType sont requis' },
        { status: 400 }
      );
    }

    const scriptName = SCRIPT_MAPPING[scriptType];
    if (!scriptName) {
      return NextResponse.json(
        { error: `Type de script non supporté: ${scriptType}` },
        { status: 400 }
      );
    }

    // Chemin vers le dossier database
    const databasePath = path.join(process.cwd(), 'database');
    const scriptPath = path.join(databasePath, scriptName);

    // Log pour débuggage
    console.log(`Lancement du script: ${scriptPath} pour ${company} (${website})`);

    // Préparer les arguments selon le type de script
    let scriptArgs: string[] = [];
    
    switch (scriptType) {
      case 'companyNews':
        scriptArgs = [company];
        break;
      case 'managementInterviews':
        scriptArgs = [company];
        break;
      case 'jobOffers':
        scriptArgs = [company, website];
        break;
      case 'financialNews':
        scriptArgs = [company];
        break;
      case 'addToDatabase':
        scriptArgs = []; // Pas d'arguments nécessaires
        break;
    }

    // Lancer le script Python de manière asynchrone
    const pythonProcess = spawn('python3', [scriptPath, ...scriptArgs], {
      cwd: databasePath,
      stdio: 'pipe'
    });

    // Collecter les logs
    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    // Retourner immédiatement une réponse de succès
    // Le script continuera à tourner en arrière-plan
    return NextResponse.json({
      success: true,
      message: `Script ${scriptType} lancé pour ${company}`,
      scriptType,
      company,
      website,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Erreur lors du lancement du script:', error);
    return NextResponse.json(
      { error: 'Erreur interne du serveur' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'API de scraping temporaire pour les entreprises Pet Care',
    availableScripts: Object.keys(SCRIPT_MAPPING),
    usage: 'POST avec { company, website, scriptType }'
  });
}