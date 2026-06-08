# SQLify - Natural Language to SQL Query Analyzer

**SQLify** is a premium, locally run web application that translates natural language questions into valid SQL queries, executes them against relational SQLite databases, and presents the output in real-time. It features pre-configured datasets, an interactive database schema visualizer (ERD node renderer), raw SQL editing consoles, and a hybrid translation engine.

---

## Key Features

- **Preset Databases**: Out-of-the-box support for three pre-seeded database schemas with realistic records:
  - **E-Commerce Platform**: Customers, Products, Orders, and Order Items tables.
  - **Company HR & Projects**: Employees, Departments, Projects, and hours allocations.
  - **Music Streaming App**: Artists, Albums, Songs, Users, and listening logs.
- **Custom Database Creator**: Paste any custom DDL/DML script directly into the console to compile and query your own custom schema immediately.
- **Hybrid NLP Engine**:
  - **Local Heuristics**: Matches intent patterns (aggregations, sorting, filters, joins) locally for direct offline execution.
  - **Gemini API Integration**: Hook up a Gemini API Key in the UI settings for deep contextual SQL translations of arbitrary complex schemas.
- **Step-by-Step SQL Explainer**: Deciphers generated queries in clear, step-by-step plain English.
- **Visual ER Diagram Viewer**: Renders table cards dynamically illustrating primary and foreign key constraints.
- **Premium Glassmorphic UI**: High HSL tailored color accents, Outfit typography, smooth CSS transitions, and responsive tables.

---

## Technology Stack

- **Backend**: Python, Flask, SQLite (`sqlite3`)
- **Frontend**: Semantic HTML5, Vanilla CSS (with custom HSL variable gradients & blur backdrops), Vanilla JS ES6
- **NLP Models**: Google Gemini API SDK (`google-generativeai`)
- **Testing**: Python `unittest` framework

---

## Directory Layout

```
.
├── app.py                  # Core Flask server and API router
├── schema_manager.py       # Seeding databases and extracting schemas
├── sql_generator.py       # Heuristic parsing and Gemini SDK caller
├── test_system.py          # Automated unit test assertions suite
├── templates/
│   └── index.html          # Main HTML5 layout structure
└── static/
    ├── css/
    │   └── style.css       # Premium visual stylesheet rules
    └── js/
        └── app.js          # Client-side routing, ERD and table builders
```

---

## Quick Start Setup

### Prerequisites
Make sure you have **Python 3.10+** installed on your system.

1. **Install Dependencies**:
   ```bash
   pip install flask google-generativeai
   ```

2. **Run the Application**:
   Initialize database seeds and start the development server:
   ```bash
   python app.py
   ```

3. **Launch in Browser**:
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

---

## Running Automated Tests

To execute the suite of unit assertions verifying database schema extractions, translation matches, and transaction sandboxing, run:
```bash
python test_system.py
```
Expected output:
```text
Ran 7 tests in 0.225s
OK
```
