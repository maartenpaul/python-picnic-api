import requests
import json
from python_picnic_api import PicnicAPI
from collections import deque

picnic = PicnicAPI(username='fam.paul@outlook.com', password='Nan0f00d!', country_code="NL")
raw_results = picnic._get("/pages/search-page-results?search_term=kaas", add_picnic_headers=True)
#with open('raw_results.json', 'w', encoding='utf-8') as f:
#    json.dump(raw_results, f, ensure_ascii=False, indent=4)

print("Raw results saved to 'raw_results.json'")

search_results = []

def extract_articles(data):
    articles = []
    stack = deque([data.get('body', {})])
        
    while stack:
        item = stack.pop()
          
        if isinstance(item, dict):
            content = item.get('content', {})
            if content.get('type') == 'SELLING_UNIT_TILE' and 'sellingUnit' in content:
                articles.append(content['sellingUnit'])
                
            child = item.get('child')
            if child:
                stack.append(child)
                
            children = item.get('children', [])
            stack.extend(reversed(children))
            
        elif isinstance(item, list):
            stack.extend(reversed(item))

    return articles

# Assuming raw_results is your API response
search_results = extract_articles(raw_results)

print(len(search_results))  # Print the number of articles found
print(search_results[:5])  # Print the first 5 articles (if any)