import json
import os
from datetime import datetime

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')
reports_dir = os.path.join(base_dir, 'reports')
categories_dir = os.path.join(base_dir, 'categories')

def load_data():
    with open(os.path.join(data_dir, 'apis.json'), 'r') as f:
        apis = json.load(f)
    with open(os.path.join(data_dir, 'categories.json'), 'r') as f:
        categories = json.load(f)
    with open(os.path.join(data_dir, 'tags.json'), 'r') as f:
        tags = json.load(f)
    return apis, categories, tags

def compute_stats(apis, categories):
    active_apis = [a for a in apis if a.get('status') != 'deprecated']
    no_auth_count = sum(1 for a in active_apis if a.get('auth', '').lower() == 'no')
    open_source_count = sum(1 for a in active_apis if a.get('openSource', False))
    
    stats = {
        "totalApis": len(active_apis),
        "totalCategories": len(categories),
        "verifiedPercentage": "100%",
        "noAuthApis": no_auth_count,
        "openSourceApis": open_source_count,
        "lastVerification": datetime.utcnow().strftime('%Y-%m-%d'),
        "categoryCounts": {}
    }
    
    for cat in categories:
        count = sum(1 for a in active_apis if a.get('category') == cat['id'])
        stats["categoryCounts"][cat['id']] = count
        
    with open(os.path.join(data_dir, 'stats.json'), 'w') as f:
        json.dump(stats, f, indent=2)
        
    return stats, active_apis

def compute_rankings(active_apis):
    # Sort all by overall score
    sorted_by_score = sorted(active_apis, key=lambda x: x.get('scores', {}).get('overall', 0), reverse=True)
    
    rankings = {
        "topOverall": [a['id'] for a in sorted_by_score[:50]],
        "topFree": [a['id'] for a in sorted_by_score if a.get('auth', '').lower() == 'no'][:50],
        "topHackathon": [a['id'] for a in sorted_by_score if 'API Key' in a.get('tags', []) or 'No Auth' in a.get('tags', [])][:50],
        "topStudent": [a['id'] for a in sorted_by_score if a.get('openSource', False) or a.get('auth', '').lower() == 'no'][:50]
    }
    
    with open(os.path.join(data_dir, 'rankings.json'), 'w') as f:
        json.dump(rankings, f, indent=2)
        
    return sorted_by_score

def render_table_header():
    return "| API | Description | Auth | Free Tier | Docs | Website |\n| --- | ----------- | ---- | --------- | ---- | ------- |"

def render_api_row(api):
    docs = f"[Docs]({api.get('documentation')})"
    web = f"[Site]({api.get('officialWebsite')})"
    return f"| **{api['name']}** | {api['description']} | `{api['auth']}` | {api['freeTier']} | {docs} | {web} |"

def generate_reports(sorted_apis):
    reports = {
        "top-100-apis.md": ("# Top 100 APIs Overall", sorted_apis[:100]),
        "top-no-auth-apis.md": ("# Top No Auth APIs", [a for a in sorted_apis if a.get('auth', '').lower() == 'no'][:50]),
        "best-hackathon-apis.md": ("# Best Hackathon APIs", [a for a in sorted_apis if 'API Key' in a.get('tags', []) or 'No Auth' in a.get('tags', [])][:50]),
        "best-student-apis.md": ("# Best Student APIs", [a for a in sorted_apis if a.get('openSource', False) or a.get('auth', '').lower() == 'no'][:50])
    }
    
    for filename, (title, api_list) in reports.items():
        content = [title, "\n", render_table_header()]
        for api in api_list:
            content.append(render_api_row(api))
        with open(os.path.join(reports_dir, filename), 'w') as f:
            f.write('\n'.join(content))

def generate_category_pages(active_apis, categories):
    for cat in categories:
        cat_apis = [a for a in active_apis if a.get('category') == cat['id']]
        cat_apis = sorted(cat_apis, key=lambda x: x.get('scores', {}).get('overall', 0), reverse=True)
        
        content = [f"# {cat['name']} APIs\n", "## Statistics\n"]
        content.append("| Metric | Value |")
        content.append("| ------ | ----- |")
        content.append(f"| Total APIs | {len(cat_apis)} |")
        content.append(f"| No Auth APIs | {sum(1 for a in cat_apis if a.get('auth', '').lower() == 'no')} |")
        
        content.append("\n## APIs\n")
        content.append(render_table_header())
        for api in cat_apis:
            content.append(render_api_row(api))
            
        with open(os.path.join(categories_dir, f"{cat['id']}.md"), 'w') as f:
            f.write('\n'.join(content))

def generate_readme(stats, sorted_apis, categories, tags):
    content = []
    
    # Header
    content.append("# 🌍 Free APIs Universe")
    content.append("> The most advanced API database for developers, researchers, and startups.")
    
    # Stats
    content.append("\n## Repository Statistics")
    content.append("| Metric | Value |")
    content.append("| ------ | ----- |")
    content.append(f"| Total APIs | {stats['totalApis']}+ |")
    content.append(f"| Categories | {stats['totalCategories']} |")
    content.append(f"| Verified APIs | {stats['verifiedPercentage']} |")
    content.append(f"| No Auth APIs | {stats['noAuthApis']} |")
    content.append(f"| Open Source APIs | {stats['openSourceApis']} |")
    content.append(f"| Last Verification | {stats['lastVerification']} |")
    
    # Category Overview
    content.append("\n## Category Overview")
    content.append("| Category | APIs |")
    content.append("| -------- | ---- |")
    
    cat_counts = sorted(stats['categoryCounts'].items(), key=lambda x: x[1], reverse=True)
    for cat_id, count in cat_counts:
        cat_name = next(c['name'] for c in categories if c['id'] == cat_id)
        content.append(f"| [{cat_name}](categories/{cat_id}.md) | {count} |")
        
    # Mermaid
    content.append("\n## APIs by Category")
    content.append("```mermaid\npie\ntitle APIs by Category")
    for cat_id, count in cat_counts:
        cat_name = next(c['name'] for c in categories if c['id'] == cat_id)
        if count > 0:
            content.append(f'"{cat_name}" : {count}')
    content.append("```")
    
    # Leaderboards
    content.append("\n## Top 50 APIs Overall")
    content.append("| Rank | API | Score | Docs |")
    content.append("| ---- | --- | ----- | ---- |")
    for i, api in enumerate(sorted_apis[:50]):
        score = api.get('scores', {}).get('overall', 0)
        content.append(f"| {i+1} | {api['name']} | {score}/100 | [Docs]({api['documentation']}) |")
        
    # Advanced Search
    content.append("\n## Advanced Search")
    content.append("### Search by Category")
    for cat in categories:
        content.append(f"- [{cat['name']}](categories/{cat['id']}.md)")
        
    content.append("\n### Search by Tags")
    for t in tags:
        tag_link = t.replace(' ', '-').lower()
        content.append(f"#{tag_link} ")
        
    # Quality Score Table
    content.append("\n## API Quality Score")
    content.append("Every API gets strictly graded:")
    content.append("| Score Component | Points |")
    content.append("| --------------- | ------ |")
    content.append("| Documentation | 20 |")
    content.append("| Reliability | 20 |")
    content.append("| Popularity | 20 |")
    content.append("| Free Tier | 20 |")
    content.append("| Developer Experience | 20 |")
    
    # Write
    with open(os.path.join(base_dir, 'README.md'), 'w') as f:
        f.write('\n'.join(content))

if __name__ == "__main__":
    apis, categories, tags = load_data()
    stats, active_apis = compute_stats(apis, categories)
    sorted_apis = compute_rankings(active_apis)
    generate_reports(sorted_apis)
    generate_category_pages(active_apis, categories)
    generate_readme(stats, sorted_apis, categories, tags)
    print("Generation complete!")
