from fastapi import FastAPI, HTTPException, Body
from typing import Dict
import uvicorn

app = FastAPI(
    title="GEOJSON MCP Server with Path and Validation",
    description="An MCP server for managing validated GEOJSON files with path-based keys.",
    version="1.2"
)

geojson_store: Dict[str, dict] = {}

def validate_geojson(geojson: dict):
    # Basic validation of GeoJSON structure
    if not isinstance(geojson, dict):
        raise HTTPException(status_code=400, detail="GEOJSON must be a JSON object")
    
    if "type" not in geojson:
        raise HTTPException(status_code=400, detail="GEOJSON must have a 'type' field")
    
    geo_type = geojson["type"]
    if geo_type == "FeatureCollection":
        if "features" not in geojson or not isinstance(geojson["features"], list):
            raise HTTPException(status_code=400, detail="'FeatureCollection' must have a 'features' list")
        for feature in geojson["features"]:
            if not isinstance(feature, dict) or "type" not in feature or feature["type"] != "Feature":
                raise HTTPException(status_code=400, detail="Each feature must be a valid 'Feature' object")
            if "geometry" not in feature:
                raise HTTPException(status_code=400, detail="Each feature must have a 'geometry'")
    elif geo_type in ["Feature", "Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon", "GeometryCollection"]:
        pass  # For brevity, we assume basic types are acceptable
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported GeoJSON type: {geo_type}")

@app.post("/geojson/{path:path}", summary="Create a new GEOJSON at a specific path")
async def create_geojson(path: str, geojson: dict = Body(...)):
    if path in geojson_store:
        raise HTTPException(status_code=409, detail=f"GEOJSON at path '{path}' already exists")
    validate_geojson(geojson)
    geojson_store[path] = geojson
    return {"path": path, "geojson": geojson}

@app.put("/geojson/{path:path}", summary="Update an existing GEOJSON at a path")
async def update_geojson(path: str, updated_geojson: dict = Body(...)):
    if path not in geojson_store:
        raise HTTPException(status_code=404, detail=f"GEOJSON at path '{path}' not found")
    validate_geojson(updated_geojson)
    geojson_store[path] = updated_geojson
    return {"path": path, "geojson": updated_geojson}

@app.get("/geojson/{path:path}", summary="Read a GEOJSON by path")
async def read_geojson(path: str):
    geojson = geojson_store.get(path)
    if not geojson:
        raise HTTPException(status_code=404, detail=f"GEOJSON at path '{path}' not found")
    return {"path": path, "geojson": geojson}

@app.delete("/geojson/{path:path}", summary="Delete a GEOJSON by path")
async def delete_geojson(path: str):
    if path not in geojson_store:
        raise HTTPException(status_code=404, detail=f"GEOJSON at path '{path}' not found")
    del geojson_store[path]
    return {"detail": f"GEOJSON at path '{path}' deleted"}

@app.get("/geojson", summary="List all GEOJSON files with paths")
async def list_geojson():
    return [{"path": p, "geojson": g} for p, g in geojson_store.items()]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
