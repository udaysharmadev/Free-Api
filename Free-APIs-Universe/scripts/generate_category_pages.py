import json
import os

def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, 'data', 'apis.json'), 'r') as f:
        apis = json.load(f)
    with open(os.path.join(base_dir, 'data', 'categories.json'), 'r') as f:
        categories = json.load(f)
    return apis, categories

def generate_category_pages():
    apis, categories = load_data()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    categories_dir = os.path.join(base_dir, 'categories')
    
    # Filter out deprecated
    active_apis = [api for api in apis if api.get('status') != 'deprecated']
    
    # Group by category
    apis_by_category = {cat['id']: [] for cat in categories}
    for api in active_apis:
        cat_id = api.get('category')
        if cat_id in apis_by_category:
            apis_by_category[cat_id].append(api)
            
    for cat in categories:
        cat_id = cat['id']
        cat_apis = apis_by_category[cat_id]
        
        # Always generate the file, even if empty, to maintain structure
        content = []
        content.append(f"# {cat['name']} APIs\n")
        content.append(f"> {cat['description']}\n")
        content.append(f"Total APIs in this category: **{len(cat_apis)}**\n")
        
        if len(cat_apis) > 0:
            content.append("| API | Description | Auth | Free Tier | Docs |")
            content.append("| --- | ----------- | ---- | --------- | ---- |")
            
            cat_apis.sort(key=lambda x: x['name'].lower())
            
            for api in cat_apis:
                status_icon = "🟢" if api.get('status') == 'verified' else "🟡"
                name = f"**{api['name']}** {status_icon}"
                desc = api['description']
                auth = f"`{api['auth']}`" if api['auth'] and api['auth'] != "No" else "No"
                free_tier = api['freeTier']
                docs = f"[Link]({api['documentation']})"
                
                content.append(f"| {name} | {desc} | {auth} | {free_tier} | {docs} |")
                
        file_path = os.path.join(categories_dir, f"{cat_id}.md")
        with open(file_path, 'w') as f:
            f.write('\n'.join(content))
            
    print(f"Generated {len(categories)} category pages.")

if __name__ == "__main__":
    generate_category_pages()
