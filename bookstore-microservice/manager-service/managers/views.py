import requests
from rest_framework.response import Response
from rest_framework.views import APIView
STAFF_SERVICE_URL = "http://staff-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"
PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"
CATALOG_SERVICE_URL = "http://catalog-service:8000"
COMMENT_RATE_SERVICE_URL = "http://comment-rate-service:8000"

def _auth_headers(request):
    auth = request.headers.get("Authorization")
    return {"Authorization": auth} if auth else {}

def _count(url, headers):
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return len(data)
    except requests.RequestException:
        return 0
    return 0

class DashboardView(APIView):
    def get(self, request):
        headers = _auth_headers(request)
        return Response({
            "staff_count": _count(f"{STAFF_SERVICE_URL}/staffs/", headers),
            "order_count": _count(f"{ORDER_SERVICE_URL}/orders/", headers),
            "payment_count": _count(f"{PAY_SERVICE_URL}/payments/", headers),
            "shipment_count": _count(f"{SHIP_SERVICE_URL}/shipments/", headers),
            "catalog_product_count": _count(f"{CATALOG_SERVICE_URL}/products/", headers),
            "review_count": _count(f"{COMMENT_RATE_SERVICE_URL}/reviews/", headers),
        })
