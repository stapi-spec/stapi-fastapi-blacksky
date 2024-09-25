# STAPI FastAPI - Blacksky

This is an example implementation for `https://github.com/stapi-spec/stapi-fastapi` proxying to the Blacksky tasking API.


Start the server locally

```sh
poetry run blacksky
```

GET all products
```sh
curl http://127.0.0.1:8000/products
```

POST to opportunities
```sh
export BLACKSKY_BACKEND_TOKEN=...
curl -d '{"geometry": {"type": "Point", "coordinates": [13.4, 52.5]}, "product_id": "BS-Test:Standard", "datetime": "2024-05-01T00:00:00Z/2024-05-12T00:00:00Z"}' -H "Content-Type: application/json; Authorization: $BLACKSKY_BACKEND_TOKEN" -X POST http://127.0.0.1:8000/opportunities
```
