#!/usr/bin/env python3
"""
Send Order Reminders Script
Uses GraphQL to query for pending orders from the last 7 days and logs reminders.
"""

import datetime
import sys
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def get_pending_orders():
    """
    Query GraphQL endpoint for orders with order_date within the last 7 days
    """
    # Calculate date 7 days ago
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    date_filter = seven_days_ago.strftime("%Y-%m-%d")

    # GraphQL endpoint
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL query for orders within the last 7 days
    query = gql(
        """
        query GetPendingOrders($dateFilter: String!) {
            orders(where: {order_date: {_gte: $dateFilter}}) {
                id
                customer_email
                order_date
            }
        }
    """
    )

    # Execute query
    variables = {"dateFilter": date_filter}
    result = client.execute(query, variable_values=variables)

    return result.get("orders", [])


def log_order_reminder(order_id, customer_email):
    """
    Log order ID and customer email to /tmp/order_reminders_log.txt with timestamp
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Order ID: {order_id}, Customer: {customer_email}\n"

    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        log_file.write(log_entry)


def send_order_reminders():
    """
    Main function to process order reminders
    """
    try:
        # Get pending orders from GraphQL
        orders = get_pending_orders()

        # Log each order
        for order in orders:
            log_order_reminder(order["id"], order["customer_email"])

        # Print confirmation
        print("Order reminders processed!")

    except Exception as e:
        print(f"Error processing order reminders: {e}")
        sys.exit(1)


if __name__ == "__main__":
    send_order_reminders()
