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

if __name__ == "__main__":
    log_crm_heartbeat()
