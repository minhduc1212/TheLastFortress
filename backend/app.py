from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from typing import List, Optional

app = FastAPI()

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fmhy_all_data.json")

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Load data into memory on startup
data = load_data()

@app.get("/api/categories")
async def get_categories():
    return [item["category_name"] for item in data]

@app.get("/api/data")
async def get_data(category: Optional[str] = None):
    if category:
        return [item for item in data if item["category_name"] == category]
    return data

@app.get("/api/search")
async def search(q: str = Query(..., min_length=1)):
    q = q.lower()
    results = []
    for category in data:
        matching_sections = []
        content = category.get("content", {})
        sections = content.get("sections", [])
        
        for section in sections:
            # Check heading
            if q in section.get("heading", "").lower():
                matching_sections.append(section)
                continue
            
            # Check text explanations
            found_in_text = False
            for text in section.get("text_explanations", []):
                if q in text.lower():
                    found_in_text = True
                    break
            if found_in_text:
                matching_sections.append(section)
                continue
                
            # Check resource items
            found_in_resources = False
            for item in section.get("resource_items", []):
                if q in item.get("full_text", "").lower():
                    found_in_resources = True
                    break
                for link in item.get("links", []):
                    if q in link.get("name", "").lower() or q in link.get("url", "").lower():
                        found_in_resources = True
                        break
                if found_in_resources:
                    break
            if found_in_resources:
                matching_sections.append(section)

        if matching_sections:
            results.append({
                "category_name": category["category_name"],
                "content": {
                    "url": content.get("url"),
                    "title": content.get("title"),
                    "sections": matching_sections
                }
            })
            
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
