import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import asyncio

app = FastAPI(title="Aggregator API", version="1.0")

PARSERS = {
    "gorzdrav": {
        "url": "http://gorzdrav-parser:8000/search",
        "param": "text"
    },
    "zdravcity": {
        "url": "http://zdravcity-parser:8000/search",
        "param": "what"
    }
}

async def fetch_parser_data(url: str, param_name: str, query: str):
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params={param_name: query})
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"❌ Ошибка запроса ккк {url}: {e}")
        return {"results": [], "error": str(e)}

@app.get("/searchAndAggregate", summary="Общий поиск", tags=["Aggregator"])
async def search_all(query: str = Query(..., description="Поисковый запрос")):
    tasks = [
        fetch_parser_data(parser["url"], parser["param"], query)
        for parser in PARSERS.values()
    ]
    results = await asyncio.gather(*tasks)

    all_items = []
    for result in results:
        if isinstance(result, dict):
            all_items.extend(result.get("results", []))
        elif isinstance(result, list):
            all_items.extend(result)

    return JSONResponse(content={"query": query, "results": all_items})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)