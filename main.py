from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import asyncio

app = FastAPI()

PARSERS = {
    "gorzdrav": "http://gorzdrav_parser:8000/search",
    "zdravcity": "http://zdravcity-parser:8000/search"
}

async def fetch_parser_data(url: str, query: str):
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params={"query": query})
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"❌ Ошибка запроса к {url}: {e}")
        return {"results": [], "error": str(e)}


@app.get("/searchAndAggregate", summary="Общий поиск", tags=["Aggregator"])
async def search_all(query: str = Query(...)):
    tasks = [fetch_parser_data(url, query) for url in PARSERS.values()]
    results = await asyncio.gather(*tasks)

    all_items = []
    for result in results:
        if isinstance(result, dict):
            all_items.extend(result.get("results", []))
        elif isinstance(result, list):
            all_items.extend(result)

    return JSONResponse(content={"query": query, "results": all_items})
