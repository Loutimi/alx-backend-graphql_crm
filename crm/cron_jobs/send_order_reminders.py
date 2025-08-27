#!/usr/bin/env python3
import sys
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Compute cutoff date (7 days ago)
cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat()

# GraphQL query
query = gql("""
query ($cutoff: Date!) {
  orders(orderDate_Gte: $cutoff, status: "PENDING") {
    id
    customer {
      email
    }
    orderDate
  }
}
""")

params = {"cutoff": cutoff_date}

try:
    result = client.execute(query, variable_values=params)
    orders = result.get("orders", [])
except Exception as e:
    sys.stderr.write(f"GraphQL query failed: {e}\n")
    sys.exit(1)

# Log file
log_file = "/tmp/order_reminders_log.txt"
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(log_file, "a") as f:
    for order in orders:
        line = f"{timestamp} - Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n"
        f.write(line)

print("Order reminders processed!")

