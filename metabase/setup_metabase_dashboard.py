import requests
import time

# Metabase instance URL (assumes local container setup)
METABASE_URL = "http://localhost:3000"
USER = "xanderdrakerp@gmail.com"
PASSWORD = "admin1234"  # In production, this would be handled securely (e.g. environment variables or secret management)

# Authenticate and return a session token
def get_session_token():
    res = requests.post(f"{METABASE_URL}/api/session", json={
        "username": USER,
        "password": PASSWORD
    })
    res.raise_for_status()  # Ensures error visibility during development
    return res.json()["id"]  # Returns the session token for authenticated requests

# Fetch the database ID of the "MarketData" DB connected in Metabase
def get_database_id(token):
    res = requests.get(f"{METABASE_URL}/api/database", headers={"X-Metabase-Session": token})
    res.raise_for_status()
    dbs = res.json()

    if isinstance(dbs, dict) and "data" in dbs:
        dbs = dbs["data"]  # Handles case where Metabase wraps DBs in a "data" object

    print("📦 Databases from Metabase:", dbs)

    for db in dbs:
        if db["name"] == "MarketData":  # Match the database connected via Metabase UI
            return db["id"]

    raise Exception("Database 'MarketData' not found.")  # Fail early if DB isn't connected

# Create a collection to group related dashboards and questions
def create_collection(token):
    res = requests.post(f"{METABASE_URL}/api/collection", json={
        "name": "Auto Dashboards"  # Collection name where visualizations will be stored
    }, headers={"X-Metabase-Session": token})
    res.raise_for_status()
    return res.json()["id"]

# Create a question (a.k.a. "card") using a native SQL query
def create_question(token, db_id, collection_id):
    res = requests.post(f"{METABASE_URL}/api/card", json={
        "name": "Avg Price by Ticker",
        "collection_id": collection_id,
        "dataset_query": {
            "type": "native",
            "native": {
                "query": "SELECT ticker, AVG(price) AS avg_price FROM market_data GROUP BY ticker",
                "template_tags": {}  # No parameterization for now — could add dynamic filters later
            },
            "database": db_id 
        },
        "display": "bar"  # Display type: bar chart
    }, headers={"X-Metabase-Session": token})
    res.raise_for_status()
    return res.json()["id"]

# Create a dashboard and add the question to it
def create_dashboard(token, collection_id, card_id):
    # Step 1: Create dashboard
    res = requests.post(f"{METABASE_URL}/api/dashboard", json={
        "name": "Market Overview",
        "collection_id": collection_id
    }, headers={"X-Metabase-Session": token})
    res.raise_for_status()

    dashboard_id = res.json()["id"]
    print(f"Created dashboard ID: {dashboard_id}")

    # Step 2: Wait for Metabase to fully register the dashboard
    print("⏳ Waiting for dashboard to become available...")
    time.sleep(5)  # Simple delay to ensure consistency before next API call

    # Step 3: Attach card using correct key: `card_id`
    res = requests.post(f"{METABASE_URL}/api/dashboard/{dashboard_id}/cards", json={
        "card_id": card_id,
        "sizeX": 4,
        "sizeY": 4,
        "row": 0,
        "col": 0
    }, headers={"X-Metabase-Session": token})
    res.raise_for_status()

    print(f"✅ Dashboard created: {METABASE_URL}/dashboard/{dashboard_id}")

# Entry point: run everything in order
if __name__ == "__main__":
    print("Connecting to Metabase API...")
    token = get_session_token()
    db_id = get_database_id(token)
    collection_id = create_collection(token)
    card_id = create_question(token, db_id, collection_id)
    create_dashboard(token, collection_id, card_id)
