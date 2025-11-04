# Cricbuzz LiveStats - Cricket Analytics Scaffold

This project is a starter scaffold for a Cricket Analytics Dashboard using:
- Python (Streamlit)
- SQL (SQLAlchemy, DB-agnostic)
- REST API (requests) — Cricbuzz unofficial + provider pattern
- JSON for snapshot storage

## Quick start
1. Create a virtual environment and activate it.
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate    # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables (create `.env` or export vars):
   - `DATABASE_URL` e.g. `sqlite:///./cricket.db`
   - `CRICKET_PROVIDER` (optional) e.g. `cricbuzz_unofficial` or `sportmonks`
   - `SPORTMONKS_API_KEY` if using SportMonks
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Project structure
See files under `pages/` and `utils/`. Fill API keys and switch provider in `.env` for live data.

## Notes
- The scaffold includes an unofficial Cricbuzz driver for prototyping. Use it only for development.
- For production, use a paid/official provider (SportMonks, CricketData, RapidAPI providers).