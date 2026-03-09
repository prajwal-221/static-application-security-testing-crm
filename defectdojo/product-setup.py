import requests
import sys
from datetime import datetime, timedelta

BASE_URL = "https://demo.defectdojo.org"
USERNAME = "admin"
PASSWORD = "1Defectdojo@demo#appsec"

PRODUCT_NAME = "IDURAR-CRM"
ENGAGEMENT_NAME = "IDURAR-CRM-Engagement"

session = requests.Session()

def get_api_token():
    url = f"{BASE_URL}/api/v2/api-token-auth/"
    response = session.post(url, data={
        "username": USERNAME,
        "password": PASSWORD
    })

    if response.status_code != 200:
        print("Authentication failed")
        sys.exit(1)

    token = response.json()["token"]
    session.headers.update({"Authorization": f"Token {token}"})
    return token


def create_product():
    url = f"{BASE_URL}/api/v2/products/"
    response = session.post(url, json={
        "name": PRODUCT_NAME,
        "description": "Auto-created via API",
        "prod_type": 1  # Default product type (usually 1 in demo)
    })

    if response.status_code not in [200, 201]:
        print("Product creation failed:", response.text)
        sys.exit(1)

    return response.json()["id"]


def create_engagement(product_id):
    url = f"{BASE_URL}/api/v2/engagements/"

    today = datetime.today().date()
    end_date = today + timedelta(days=30)

    response = session.post(url, json={
        "name": ENGAGEMENT_NAME,
        "description": "CI/CD Engagement created via API",
        "product": product_id,
        "target_start": str(today),
        "target_end": str(end_date),
        "engagement_type": "CI/CD"
    })

    if response.status_code not in [200, 201]:
        print("Engagement creation failed:", response.text)
        sys.exit(1)

    return response.json()["id"]


if __name__ == "__main__":
    print("Authenticating...")
    token = get_api_token()

    print("Creating Product...")
    product_id = create_product()

    print("Creating Engagement...")
    engagement_id = create_engagement(product_id)

    print(f"\n✅ Engagement Created Successfully!")
    print(f"Engagement ID: {engagement_id}")
