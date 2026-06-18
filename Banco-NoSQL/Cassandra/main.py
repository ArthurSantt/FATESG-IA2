import requests

DATABASE_ID = "9e0d65dd-2ad2-4bb4-a663-695e38fa52dc"
REGION = "us-east-2"
TOKEN = "Token da cassandra"

url = f"https://{DATABASE_ID}-{REGION}.apps.astra.datastax.com/api/rest/v2/keyspaces/default_keyspace/leituras_sensor"

headers = {
    "X-Cassandra-Token": TOKEN,
    "Content-Type": "application/json"
}

params = {
    "where": '{"sensor_id":{"$eq":"sensor-001"},"data_leitura":{"$eq":"2026-05-22"}}'
}

response = requests.get(url, headers=headers, params=params)

print(response.status_code)
print(response.text)