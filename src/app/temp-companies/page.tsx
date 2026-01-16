"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, Play, CheckCircle, Clock, AlertCircle, Database, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

interface TempCompany {
  name: string;
  website: string;
  status: "pending" | "running" | "completed" | "error";
  lastRun?: string;
  scripts: {
    companyNews: "pending" | "running" | "completed" | "error";
    managementInterviews: "pending" | "running" | "completed" | "error";
    jobOffers: "pending" | "running" | "completed" | "error";
    financialNews: "pending" | "running" | "completed" | "error";
  };
}

const initialCompanies: TempCompany[] = [
  {
    name: "Chewy",
    website: "https://www.chewy.com/",
    status: "pending",
    scripts: {
      companyNews: "pending",
      managementInterviews: "pending",
      jobOffers: "pending",
      financialNews: "pending",
    },
  },
  {
    name: "Petco",
    website: "https://www.petco.com/shop/en/petcostore",
    status: "pending",
    scripts: {
      companyNews: "pending",
      managementInterviews: "pending",
      jobOffers: "pending",
      financialNews: "pending",
    },
  },
  {
    name: "Petmate",
    website: "https://www.petmate.com/",
    status: "pending",
    scripts: {
      companyNews: "pending",
      managementInterviews: "pending",
      jobOffers: "pending",
      financialNews: "pending",
    },
  },
  {
    name: "Petsmart",
    website: "https://www.petsmart.com/",
    status: "pending",
    scripts: {
      companyNews: "pending",
      managementInterviews: "pending",
      jobOffers: "pending",
      financialNews: "pending",
    },
  },
];

const getStatusIcon = (status: string) => {
  switch (status) {
    case "completed":
      return <CheckCircle className="w-4 h-4 text-green-600" />;
    case "running":
      return <Clock className="w-4 h-4 text-blue-600 animate-spin" />;
    case "error":
      return <AlertCircle className="w-4 h-4 text-red-600" />;
    default:
      return <Clock className="w-4 h-4 text-gray-400" />;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "completed":
      return <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">Terminé</Badge>;
    case "running":
      return <Badge variant="default" className="bg-blue-100 text-blue-800 border-blue-200">En cours</Badge>;
    case "error":
      return <Badge variant="destructive">Erreur</Badge>;
    default:
      return <Badge variant="secondary">En attente</Badge>;
  }
};

export default function TempCompaniesPage() {
  const [companies, setCompanies] = useState<TempCompany[]>(initialCompanies);
  const [isRunningAll, setIsRunningAll] = useState(false);
  const [isAddingToDatabase, setIsAddingToDatabase] = useState(false);

  const runScript = async (companyName: string, scriptType: keyof TempCompany['scripts']) => {
    const company = companies.find(c => c.name === companyName);
    if (!company) return;

    setCompanies(prev => prev.map(c => 
      c.name === companyName 
        ? {
            ...c,
            scripts: {
              ...c.scripts,
              [scriptType]: "running"
            }
          }
        : c
    ));

    try {
      const response = await fetch('/api/temp-scraping', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company: companyName,
          website: company.website,
          scriptType: scriptType
        }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        console.log(`Script ${scriptType} lancé avec succès pour ${companyName}`);
        
        // Marquer comme terminé après un délai (le script tourne en arrière-plan)
        setTimeout(() => {
          setCompanies(prev => prev.map(c => 
            c.name === companyName 
              ? {
                  ...c,
                  scripts: {
                    ...c.scripts,
                    [scriptType]: "completed"
                  },
                  lastRun: new Date().toISOString()
                }
              : c
          ));
        }, 5000); // 5 secondes pour simuler le temps de traitement
        
      } else {
        throw new Error(result.error || 'Erreur lors du lancement du script');
      }
    } catch (error) {
      console.error(`Erreur lors du lancement du script ${scriptType} pour ${companyName}:`, error);
      setCompanies(prev => prev.map(c => 
        c.name === companyName 
          ? {
              ...c,
              scripts: {
                ...c.scripts,
                [scriptType]: "error"
              }
            }
          : c
      ));
    }
  };

  const runAllScripts = async (companyName: string) => {
    const company = companies.find(c => c.name === companyName);
    if (!company) return;

    setCompanies(prev => prev.map(c => 
      c.name === companyName 
        ? { ...c, status: "running" }
        : c
    ));

    const scriptTypes: (keyof TempCompany['scripts'])[] = [
      'companyNews', 
      'managementInterviews', 
      'jobOffers', 
      'financialNews'
    ];

    for (const scriptType of scriptTypes) {
      await runScript(companyName, scriptType);
    }

    setCompanies(prev => prev.map(c => 
      c.name === companyName 
        ? { ...c, status: "completed" }
        : c
    ));
  };

  const runAllCompanies = async () => {
    setIsRunningAll(true);
    
    for (const company of companies) {
      await runAllScripts(company.name);
    }
    
    setIsRunningAll(false);
  };

  const addToDatabase = async () => {
    setIsAddingToDatabase(true);
    
    try {
      const response = await fetch('/api/temp-scraping', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company: 'PetCareCompanies',
          website: '',
          scriptType: 'addToDatabase'
        }),
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        console.log('Entreprises ajoutées à la base de données avec succès');
        alert('✅ Entreprises Pet Care ajoutées à la base de données!');
      } else {
        throw new Error(result.error || 'Erreur lors de l\'ajout à la base de données');
      }
    } catch (error) {
      console.error('Erreur lors de l\'ajout à la base de données:', error);
      alert('❌ Erreur lors de l\'ajout à la base de données');
    } finally {
      setIsAddingToDatabase(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Entreprises Pet Care - Interface Temporaire
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Gestion du scraping pour les nouvelles entreprises du secteur des animaux de compagnie
          </p>
        </div>
        <div className="flex gap-3">
          <Button 
            onClick={addToDatabase}
            disabled={isAddingToDatabase}
            variant="outline"
            className="border-green-200 text-green-700 hover:bg-green-50"
          >
            {isAddingToDatabase ? (
              <>
                <Clock className="w-4 h-4 mr-2 animate-spin" />
                Ajout en cours...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 mr-2" />
                Ajouter à la DB
              </>
            )}
          </Button>
          <Button 
            onClick={runAllCompanies}
            disabled={isRunningAll}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isRunningAll ? (
              <>
                <Clock className="w-4 h-4 mr-2 animate-spin" />
                Scraping en cours...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Lancer tout le scraping
              </>
            )}
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Entreprises à traiter</CardTitle>
          <CardDescription>
            4 entreprises du secteur pet care à analyser avec nos scripts de scraping
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Entreprise</TableHead>
                <TableHead>Site Web</TableHead>
                <TableHead>Company News</TableHead>
                <TableHead>Management Interviews</TableHead>
                <TableHead>Job Offers</TableHead>
                <TableHead>Financial News</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {companies.map((company) => (
                <TableRow key={company.name}>
                  <TableCell className="font-medium">{company.name}</TableCell>
                  <TableCell>
                    <a 
                      href={company.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                    >
                      <ExternalLink className="w-3 h-3" />
                      Visiter
                    </a>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(company.scripts.companyNews)}
                      {getStatusBadge(company.scripts.companyNews)}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => runScript(company.name, 'companyNews')}
                        disabled={company.scripts.companyNews === 'running'}
                        className="ml-2"
                      >
                        <Play className="w-3 h-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(company.scripts.managementInterviews)}
                      {getStatusBadge(company.scripts.managementInterviews)}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => runScript(company.name, 'managementInterviews')}
                        disabled={company.scripts.managementInterviews === 'running'}
                        className="ml-2"
                      >
                        <Play className="w-3 h-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(company.scripts.jobOffers)}
                      {getStatusBadge(company.scripts.jobOffers)}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => runScript(company.name, 'jobOffers')}
                        disabled={company.scripts.jobOffers === 'running'}
                        className="ml-2"
                      >
                        <Play className="w-3 h-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(company.scripts.financialNews)}
                      {getStatusBadge(company.scripts.financialNews)}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => runScript(company.name, 'financialNews')}
                        disabled={company.scripts.financialNews === 'running'}
                        className="ml-2"
                      >
                        <Play className="w-3 h-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button
                      size="sm"
                      onClick={() => runAllScripts(company.name)}
                      disabled={company.status === 'running'}
                      className="bg-green-600 hover:bg-green-700 text-white"
                    >
                      {company.status === 'running' ? (
                        <>
                          <Clock className="w-3 h-3 mr-1 animate-spin" />
                          En cours
                        </>
                      ) : (
                        <>
                          <Play className="w-3 h-3 mr-1" />
                          Tout lancer
                        </>
                      )}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Instructions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-sm text-gray-600">
              <p><strong>Étape 1 - Ajouter à la base de données :</strong></p>
              <p className="ml-4 text-xs">Cliquez sur "Ajouter à la DB" pour ajouter ces entreprises au fichier TAM.csv</p>
            </div>
            <div className="text-sm text-gray-600">
              <p><strong>Étape 2 - Scripts de scraping :</strong></p>
              <ul className="list-disc list-inside ml-4 space-y-1 text-xs">
                <li><strong>Company News :</strong> Scraping des actualités de l'entreprise</li>
                <li><strong>Management Interviews :</strong> Recherche d'interviews du management</li>
                <li><strong>Job Offers :</strong> Analyse des offres d'emploi avec Mantiks</li>
                <li><strong>Financial News :</strong> Collecte des données financières</li>
              </ul>
            </div>
            <div className="text-sm text-gray-600">
              <p><strong>Actions disponibles :</strong></p>
              <ul className="list-disc list-inside ml-4 space-y-1 text-xs">
                <li>Boutons <Play className="w-3 h-3 inline" /> : lancer un script individuel</li>
                <li>"Tout lancer" : exécuter tous les scripts d'une entreprise</li>
                <li>"Lancer tout le scraping" : traiter toutes les entreprises</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Entreprises Pet Care</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm text-gray-600">
              <p><strong>Secteur :</strong> Animaux de compagnie</p>
              <p><strong>Nombre d'entreprises :</strong> 4</p>
            </div>
            <div className="space-y-2">
              {companies.map((company) => (
                <div key={company.name} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="font-medium text-sm">{company.name}</span>
                  <a 
                    href={company.website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-xs"
                  >
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}