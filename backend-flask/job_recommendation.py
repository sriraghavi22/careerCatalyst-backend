import requests
import time

# Adzuna API credentials
APP_ID = "15342df4"
APP_KEY = "b38d6d910bdc9e6a589efb28ba54ffbd"
BASE_URL = "https://api.adzuna.com/v1/api/jobs"

# API parameters
COUNTRY = "in"
RESULTS_PER_PAGE = 10

# Retry logic for Adzuna API request
def get_job_listings(search_query, retries=3):
    url = f"{BASE_URL}/{COUNTRY}/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": search_query,
    }

    for attempt in range(retries):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for job in data.get("results", []):
                jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name"),
                    "location": job.get("location", {}).get("display_name"),
                    "description": job.get("description"),
                    "url": job.get("redirect_url"),
                })
            return jobs
        elif response.status_code == 503:
            print("503 Error: Server unavailable. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break

    return []