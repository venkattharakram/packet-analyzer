# Persistor Service — README

## Overview
The Persistor Service inserts packets into PostgreSQL.  
It is the **first service that permanently stores data**.

## Data Flow
- **Input**:  
  - JSON from **Parser Service** (`/store`)  
- **Output**:  
  - Inserts rows into PostgreSQL `packets` table.  
- **Storage**:  
  - ✅ Yes, all packet data is stored permanently in PostgreSQL.  

## Database Schema
| Column   | Type    | Description                     |
|----------|---------|---------------------------------|
| id       | SERIAL  | Unique ID (auto-increment)      |
| src_ip   | TEXT    | Source IP address               |
| dst_ip   | TEXT    | Destination IP address          |
| protocol | TEXT    | Classified protocol (TCP/UDP/ICMP/DNS/Unknown) |
| summary  | TEXT    | Human-readable packet summary   |

## Lifecycle
- Runs continuously as a Flask web service on port `5002`.  

## Logs
- **persistor.log** shows:  
  - Flask startup message (`Running on http://127.0.0.1:5002`)  
  - Inserts success/failures (`✅ Inserted packet into DB` or error stacktrace).  
