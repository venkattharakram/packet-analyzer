# Analyzer Service — README

## Overview
The Analyzer Service queries PostgreSQL and exposes packet summaries and lists to the UI.

## Data Flow
- **Input**:  
  - Reads packets from PostgreSQL `packets` table  
- **Output**:  
  - Provides APIs for UI:  
    - `/protocol_summary` → count of packets by protocol  
    - `/packets` → last 50 packets  
    - `/filter?protocol=XYZ` → filtered packets  
- **Storage**:  
  - ❌ No storage. Only queries DB.  

## Lifecycle
- Runs continuously as a Flask web service on port `5003`.  

## Logs
- **analyzer.log** shows:  
  - SQL queries executed (`Running query: SELECT ...`)  
  - DB connection status (`✅ Connected to PostgreSQL database`)  
  - Results retrieved (`✅ Retrieved 50 packets`).  
- Logs also show HTTP requests from the UI (`127.0.0.1 - - [..] "GET /packets HTTP/1.1" 200 -`).  
