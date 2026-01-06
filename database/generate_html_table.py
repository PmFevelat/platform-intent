#!/usr/bin/env python3
import csv
import html

def generate_html_table():
    """Génère un fichier HTML avec un tableau formaté des entreprises US"""
    
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entreprises Prospects - United States</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .table-wrapper {
            overflow-x: auto;
            padding: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        thead {
            background: #f8f9fa;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        th {
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }
        
        tbody tr {
            transition: background-color 0.2s;
        }
        
        tbody tr:hover {
            background-color: #f8f9fa;
        }
        
        tbody tr:nth-child(even) {
            background-color: #fafafa;
        }
        
        tbody tr:nth-child(even):hover {
            background-color: #f0f0f0;
        }
        
        a {
            color: #667eea;
            text-decoration: none;
            transition: color 0.2s;
        }
        
        a:hover {
            color: #764ba2;
            text-decoration: underline;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            background: #e9ecef;
            color: #495057;
        }
        
        .company-name {
            font-weight: 500;
            color: #212529;
        }
        
        .link-cell {
            max-width: 250px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .stats {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Entreprises Prospects</h1>
            <div class="subtitle">United States - Liste complète</div>
        </header>
        
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Nom de l'entreprise</th>
                        <th>Website</th>
                        <th>LinkedIn</th>
                        <th>Industrie</th>
                        <th>Employés</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Lire le CSV original et filtrer
    with open('TAM.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        
        for row in reader:
            if row.get('Country', '').strip() == 'United States':
                count += 1
                company_name = html.escape(row.get('CompanyName', ''))
                website = html.escape(row.get('Website', '').strip())
                linkedin = html.escape(row.get('LinkedIn', '').strip())
                industry = html.escape(row.get('Sub Industry', ''))
                employees = html.escape(row.get('Employees', ''))
                
                # Créer les liens
                website_link = f'<a href="{website}" target="_blank" rel="noopener noreferrer">{website}</a>' if website else '-'
                linkedin_link = f'<a href="{linkedin}" target="_blank" rel="noopener noreferrer">{linkedin}</a>' if linkedin else '-'
                
                html_content += f"""                    <tr>
                        <td class="company-name">{company_name}</td>
                        <td class="link-cell">{website_link}</td>
                        <td class="link-cell">{linkedin_link}</td>
                        <td><span class="badge">{industry}</span></td>
                        <td>{employees}</td>
                    </tr>
"""
    
    html_content += """                </tbody>
            </table>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">""" + str(count) + """</div>
                <div class="stat-label">Entreprises</div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Écrire le fichier HTML
    with open('TAM_US_table.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Fichier HTML généré avec succès ! ({count} entreprises)")

if __name__ == '__main__':
    generate_html_table()

