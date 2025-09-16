# UI Service — README

## Overview
The UI Service is a Flask + HTML dashboard.  
It calls Analyzer APIs and renders the results in a browser.

## Data Flow
- **Input**:  
  - Calls Analyzer Service (`/protocol_summary`, `/packets`, `/filter`)  
- **Output**:  
  - Renders HTML dashboard for users.  
- **Storage**:  
  - ❌ No storage. Only displays.  

## Lifecycle
- Runs continuously as a Flask web service on port `5000`.  

## Logs
- **ui.log** shows:  
  - Flask startup message (`Running on http://127.0.0.1:5000`)  
  - Page access logs (`127.0.0.1 - - [..] "GET / HTTP/1.1" 200 -`).  
- ❌ Does not log DB or packets (that’s Analyzer’s job).  
