import json
import os

def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, 'data', 'apis.json'), 'r') as f:
        apis = json.load(f)
    with open(os.path.join(base_dir, 'data', 'categories.json'), 'r') as f:
        categories = json.load(f)
    return apis, categories

def generate_readme():
    apis, categories = load_data()
    
    # Filter out deprecated
    active_apis = [api for api in apis if api.get('status') != 'deprecated']
    
    # Group by category
    apis_by_category = {cat['id']: [] for cat in categories}
    for api in active_apis:
        cat_id = api.get('category')
        if cat_id in apis_by_category:
            apis_by_category[cat_id].append(api)
    
    readme_content = []
    
    # Header
    readme_content.append("<div align=\"center\">")
    readme_content.append("  <h1>🌍 Free APIs Universe</h1>")
    readme_content.append("  <p><b>The world's largest actively maintained catalog of free and freemium APIs.</b></p>")
    readme_content.append(f"  <p><img src=\"https://img.shields.io/badge/Total%20APIs-{len(active_apis)}-brightgreen?style=for-the-badge\" alt=\"API Count\"></p>")
    readme_content.append("</div>\n")
    
    readme_content.append("Welcome to the **Free APIs Universe**. A massive, automatically verified catalog of developer APIs.\n")
    
    # Table of Contents
    readme_content.append("## 📑 Table of Contents\n")
    for cat in categories:
        if len(apis_by_category[cat['id']]) > 0:
            link = cat['name'].lower().replace(' ', '-').replace('&', '')
            readme_content.append(f"- [{cat['name']}](#{link})")
    readme_content.append("\n---")
    
    # Categories
    for cat in categories:
        cat_apis = apis_by_category[cat['id']]
        if len(cat_apis) == 0:
            continue
            
        readme_content.append(f"\n## {cat['name']}\n")
        readme_content.append(f"{cat['description']}\n")
        readme_content.append("| API | Description | Auth | Free Tier | Docs |")
        readme_content.append("| --- | ----------- | ---- | --------- | ---- |")
        
        # Sort APIs alphabetically
        cat_apis.sort(key=lambda x: x['name'].lower())
        
        for api in cat_apis:
            status_icon = "🟢" if api.get('status') == 'verified' else "🟡"
            name = f"**{api['name']}** {status_icon}"
            desc = api['description']
            auth = f"`{api['auth']}`" if api['auth'] and api['auth'] != "No" else "No"
            free_tier = api['freeTier']
            docs = f"[Link]({api['documentation']})"
            
            readme_content.append(f"| {name} | {desc} | {auth} | {free_tier} | {docs} |")
            
    # Write to README.md
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(base_dir, 'README.md')
    
    with open(readme_path, 'w') as f:
        f.write('\n'.join(readme_content))
    
    print(f"Generated README.md with {len(active_apis)} APIs.")

if __name__ == "__main__":
    generate_readme()
