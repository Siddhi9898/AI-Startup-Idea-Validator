# Web Search Agent

## Overview

The Web Search Agent is a module of the AI Startup Idea Validator project. It retrieves live web search results based on a startup idea entered by the user. The module uses DuckDuckGo Search (DDGS) to gather relevant information and displays the results using a Streamlit interface.

## Features

- Accepts a startup idea as user input
- Improves the search query before searching
- Retrieves live search results using DuckDuckGo
- Cleans and formats the search results
- Displays results in a simple Streamlit interface

## Project Structure

```
web_search_agent/
│── app.py
│── web_search.py
│── query_planner.py
│── cleaner.py
│── requirements.txt
└── README.md
```

## File Description

### app.py
Creates the Streamlit user interface and displays the search results.

### web_search.py
Performs the DuckDuckGo search and returns the search results.

### query_planner.py
Improves the user's query by adding relevant search keywords.

### cleaner.py
Processes and formats the search results before displaying them.

### requirements.txt
Contains the required Python packages.

## Installation

Clone the repository and install the dependencies.

```bash
pip install -r requirements.txt
```

## Running the Application

Navigate to the `web_search_agent` folder and run:

```bash
streamlit run app.py
```

## Workflow

```
User Startup Idea
        │
        ▼
Query Planner
        │
        ▼
DuckDuckGo Search
        │
        ▼
Result Cleaner
        │
        ▼
Display Results in Streamlit
```

## Example

### Input

```
AI Startup
```

### Output

The application displays:

- Relevant startup websites
- Competitor information
- Industry articles
- Market-related resources

## Technologies Used

- Python
- Streamlit
- DDGS (DuckDuckGo Search)

## Future Improvements

- Add filtering and ranking of search results
- Integrate the module with the Orchestrator Agent
- Support multiple search providers
- Improve relevance using AI-based query planning

## Author

Niharika