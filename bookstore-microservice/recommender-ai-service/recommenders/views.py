from collections import defaultdict
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
COMMENT_RATE_SERVICE_URL = "http://comment-rate-service:8000"
BOOK_SERVICE_URL = "http://book-service:8000"

def _forward_auth_header(request):
    auth = request.headers.get("Authorization")
    if auth:
        return {"Authorization": auth}
    return {}

class RecommendView(APIView):
    def get(self, request, customer_id):
        headers = _forward_auth_header(request)
        scored = defaultdict(lambda: {"sum": 0, "count": 0})
        recommendations = []
        try:
            r = requests.get(f"{COMMENT_RATE_SERVICE_URL}/reviews/", headers=headers, timeout=5)
            if r.status_code == 200:
                reviews = r.json()
                for rv in reviews:
                    product_id = rv.get("product_id")
                    rating = int(rv.get("rating", 0))
                    if product_id is None:
                        continue
                    scored[product_id]["sum"] += rating
                    scored[product_id]["count"] += 1
                ranked = sorted(scored.items(), key=lambda kv: (kv[1]["sum"] / max(kv[1]["count"], 1), kv[1]["count"]), reverse=True)
                recommendations = [pid for pid, _ in ranked[:5]]
        except requests.RequestException:
            recommendations = []

        fallback_books = []
        try:
            b = requests.get(f"{BOOK_SERVICE_URL}/books/", headers=headers, timeout=5)
            if b.status_code == 200:
                fallback_books = b.json()[:5]
        except requests.RequestException:
            fallback_books = []

        return Response({
            "customer_id": customer_id,
            "recommended_product_ids": recommendations,
            "fallback_books": fallback_books,
        })
