# Spell Correct

A FastAPI-based service for name spell correction and suggestions.

## Features

- **Name Spell Correction**: Suggests correctly spelled alternatives for input names
- **Country-specific Corrections**: Takes country context into account when making suggestions
- **RESTful API**: Simple API endpoints for integration into other applications
- **Metadata Storage**: Tracks and stores correction requests for future reference

## How It Works

The spell correction process follows a multi-step approach to provide accurate name suggestions:

### 1. Existence Check
First, the system checks if the name has been previously searched and corrected for the given country. If found, it returns the cached suggestions immediately.

### 2. Metaphone-Based Suggestions
If not cached, the system generates suggestions using phonetic algorithms (metaphones) that match names with similar pronunciation patterns, filtered by country context.

### 3. Quality Evaluation
The generated suggestions are evaluated for quality using various criteria such as:
- Similarity scores
- Common name patterns
- Country-specific name validity

### 4. LLM Enhancement
If the initial suggestions don't meet quality thresholds, the system calls a Large Language Model (LLM) to generate more contextually appropriate corrections based on the name and country.

### 5. Background Processing
All correction requests and their results are saved asynchronously in the background for future reference and system improvement.

## Project Structure

```
spell-correct/
├── app/
│   ├── controller/      # Business logic controllers
│   ├── models/          # Database models and Pydantic schemas
│   ├── routes/          # API route definitions
│   ├── services/        # Service layer for external interactions
│   ├── utils/           # Utility functions
│   ├── db_config.py     # Database configuration
│   └── main.py          # FastAPI application entry point
├── data/
│   └── db/              # Database configuration files
├── static/              # Static files (e.g., country data)
├── docker-compose.yml   # Docker Compose configuration
└── requirements.txt     # Python dependencies
```

## Prerequisites

- Python 3.10+
- PostgreSQL
- Docker and Docker Compose (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/spell-correct.git
   cd spell-correct
   ```

2. Use a virtual environment to install all the dependencies `python -m venv venv`


3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database connection in db_config.py.


5. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Getting Started

1. Once the application is running, open your browser and navigate to:
   ```
   http://localhost:8000/docs
   ```

2. This will take you to the FastAPI automatic documentation interface.

3. First, try the `GET /api/` endpoint to verify the API is working and to load the initial dataset.

4. To use the name correction feature:
   - Expand the `POST /api/name-correction` endpoint
   - Click "Try it out"
   - Provide a JSON payload with the required parameters:
     ```json
     {
       "name": "Jhon",
       "country": "USA"
     }
     ```
   - Click "Execute" to see the correction suggestions

5. The API will return properly formatted name suggestions based on the input and country context.


## License

This project is licensed under the MIT License - see the LICENSE file for details.