import json
from rfp_mapper.mapper import Mapper

def run_demo():
    print("=" * 60)
    print("   *** Logistics RFP Column Mapping Engine - LIVE DEMO ***")
    print("=" * 60)
    
    # Initialize the mapper
    # Note: Requires ollama to be running locally with the chosen model installed
    try:
        import ollama
        use_llm = True
    except ImportError:
        print("\n[!] WARNING: `ollama` Python package is not installed.")
        print("The demo will only use exact heuristic matching. The LLM semantic engine will not be active.")
        use_llm = False
    
    mapper = Mapper(use_llm=use_llm, model_name="llama3")

    demo_cases = [
        {
            "name": "Case 1: Standard Abbreviations",
            "columns": ["Orig Port", "Destination", "20GP", "40HQ Rate", "ETD", "Transit (days)", "Currency"]
        },
        {
            "name": "Case 2: Short Acronyms",
            "columns": ["POL", "POD", "Rate_20", "Rate_40HC", "Departure", "T/T", "Curr"]
        },
        {
            "name": "Case 3: Descriptive Labels",
            "columns": ["Load Port", "Discharge Port", "20’", "40’ HC", "Sailing Date", "Duration", "Rate Currency"]
        },
        {
            "name": "Case 4: Complex Case (Embedded Metadata & Context)",
            "columns": ["From", "To", "20FT USD", "40FT", "ETD (YYYYMMDD)", "Transit", "CCY"]
        }
    ]

    for i, case in enumerate(demo_cases, 1):
        print(f"\n\n--- Running {case['name']} ---")
        print(f" Input Columns: {case['columns']}")
        
        result = mapper.map_columns(case['columns'])
        
        print("\n Mapped Output:")
        for mapping in result.mappings:
            metadata_str = f" [Extracted Metadata: '{mapping.extracted_metadata}']" if mapping.extracted_metadata else ""
            print(f"  * '{mapping.input_column}' -> {mapping.mapped_target_field} "
                  f"(Confidence: {mapping.confidence_score:.1f}){metadata_str}")
            print(f"    Reasoning: {mapping.reasoning}")

if __name__ == "__main__":
    run_demo()
