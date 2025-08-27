#!/usr/bin/env python3
"""
CRM Cron Jobs
Contains cron job functions for CRM system monitoring and maintenance.
"""

import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Log CRM heartbeat message to /tmp/crm_heartbeat_log.txt
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    And queries GraphQL hello field to verify endpoint responsiveness.
    """
    # Get current timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Base heartbeat message
    heartbeat_message = f"{timestamp} CRM is alive"
    
    # Test GraphQL endpoint responsiveness
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Query hello field to test endpoint
        query = gql("""
            query {
                hello
            }
        """)
        
        result = client.execute(query)
        hello_response = result.get("hello", "No response")
        
        # Append GraphQL status to message
        heartbeat_message += f" - GraphQL: {hello_response}"
        
    except Exception as e:
        # Log GraphQL error but don't fail the heartbeat
        heartbeat_message += f" - GraphQL Error: {str(e)}"
    
    # Append message to log file
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(heartbeat_message + '\n')


def update_low_stock():
    """
    Run the UpdateLowStockProducts mutation and log results.

    Executes the GraphQL mutation 'UpdateLowStockProducts' to refresh stock data.
    Logs updated product names and new stock levels with a timestamp.

    Log file: /tmp/low_stock_updates_log.txt
    Format:
        DD/MM/YYYY-HH:MM:SS - Updated ProductName: NewStockLevel
    """
    # Get current timestamp for log entries
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Define mutation to update low stock products
        mutation = gql("""
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    name
                    stock
                }
            }
        }
        """)

        # Execute mutation
        result = client.execute(mutation)
        updated_products = (
            result.get("updateLowStockProducts", {})
                  .get("updatedProducts", [])
        )

        # Write results to log
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            if updated_products:
                for product in updated_products:
                    name = product.get("name", "Unknown")
                    stock = product.get("stock", "N/A")
                    log_file.write(f"{timestamp} - Updated {name}: {stock}\n")
            else:
                log_file.write(f"{timestamp} - No products updated\n")

    except Exception as e:
        # Log any errors to the same file
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} - Error: {str(e)}\n")


if __name__ == "__main__":
    log_crm_heartbeat()
    update_low_stock()