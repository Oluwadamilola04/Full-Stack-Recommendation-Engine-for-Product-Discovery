# API Examples

Base URL:

```text
http://127.0.0.1:8000/api/v1
```

## Health

```powershell
curl http://127.0.0.1:8000/health
```

## Products

### List products

```powershell
curl "http://127.0.0.1:8000/api/v1/products/?limit=10"
```

### Get one product

```powershell
curl "http://127.0.0.1:8000/api/v1/products/1"
```

## Users

### List seeded users

```powershell
curl "http://127.0.0.1:8000/api/v1/users/?limit=10"
```

### Get one user

```powershell
curl "http://127.0.0.1:8000/api/v1/users/1"
```

## Interactions

### Record a purchase

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/interactions/" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":1,\"product_id\":2,\"interaction_type\":\"purchase\",\"rating\":5.0}"
```

### Get a user’s interactions

```powershell
curl "http://127.0.0.1:8000/api/v1/interactions/user/1?limit=10"
```

## Recommendations

### Hybrid recommendations

```powershell
curl "http://127.0.0.1:8000/api/v1/recommendations/user/1?strategy=hybrid&limit=5"
```

### Collaborative recommendations

```powershell
curl "http://127.0.0.1:8000/api/v1/recommendations/user/1?strategy=collaborative&limit=5"
```

### Content-based recommendations

```powershell
curl "http://127.0.0.1:8000/api/v1/recommendations/user/1?strategy=content&limit=5"
```

### Similar products

```powershell
curl "http://127.0.0.1:8000/api/v1/recommendations/similar/1?limit=5"
```

### Trending products

```powershell
curl "http://127.0.0.1:8000/api/v1/recommendations/trending?limit=5"
```

## Example response

```json
{
  "user_id": 1,
  "recommendations": [
    {
      "product_id": 14,
      "score": 0.91,
      "reason": "Blended from interaction history and product similarity"
    }
  ],
  "strategy": "hybrid",
  "total_recommendations": 1
}
```

## Python example

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

response = requests.get(
    f"{BASE_URL}/recommendations/user/1",
    params={"strategy": "hybrid", "limit": 5},
)

print(response.json())
```

## JavaScript example

```javascript
const baseUrl = "http://127.0.0.1:8000/api/v1";

async function getRecommendations(userId) {
  const response = await fetch(
    `${baseUrl}/recommendations/user/${userId}?strategy=hybrid&limit=5`,
  );
  return response.json();
}
```
