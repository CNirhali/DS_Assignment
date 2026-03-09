# DS_Assignment - RFP Column Mapping Project

This project maps arbitrary logistics RFP columns to a standard internal schema using a hybrid LLM + heuristics approach.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Set your Gemini API key:
   ```bash
   $env:GEMINI_API_KEY="your_api_key_here"
   ```

3. Run the mapping test suite:
   ```bash
   pytest tests/test_examples.py -v
   ```
