# Parser Service — README

## Overview
The Parser Service receives packets from Capture, classifies them (TCP, UDP, ICMP, DNS, etc.), and forwards them to Persistor.  
It does not store data locally.

## Data Flow
- **Input**:  
  - JSON from **Capture Service** (`/parse`)  
- **Output**:  
  - Sends enriched JSON to **Persistor Service**:  
    ```
    POST http://127.0.0.1:5002/store
    ```
- **Storage**:  
  - ❌ No storage (forwards only).  

## Lifecycle
- Runs continuously as a Flask web service on port `5001`.  

## Logs
- **parser.log** shows:  
  - Requests received from Capture (`127.0.0.1 - - [..] "POST /parse HTTP/1.1" 200 -`)  
  - Errors if Persistor is unreachable (`Error sending to persistor ...`)  
  - No raw packet dump (kept lightweight).  
