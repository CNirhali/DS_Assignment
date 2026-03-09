import re
from typing import List, Dict, Tuple, Optional
import os

from rfp_mapper.models import RFPMappingResult, ColumnMapping, TargetFieldAlias
import json

# --- Heuristic Exact Match Dictionaries ---
# These are used for fast, high-confidence mapping without involving the LLM.

EXACT_MATCH_DICT: Dict[str, TargetFieldAlias] = {
    # Port of Loading
    "pol": "origin_port",
    "port of loading": "origin_port",
    "load port": "origin_port",
    "orig port": "origin_port",
    # Port of Discharge
    "pod": "destination_port",
    "port of discharge": "destination_port",
    "discharge port": "destination_port",
    "destination": "destination_port",
    # Rates
    "20gp": "container_type_20gp_rate",
    "40hq rate": "container_type_40hq_rate",
    # Dates
    "etd": "estimated_time_of_departure",
    "departure": "estimated_time_of_departure",
    "sailing date": "estimated_time_of_departure",
    # Transit
    "t/t": "transit_time_days",
    "transit (days)": "transit_time_days",
    "duration": "transit_time_days",
    # Currency
    "curr": "currency",
    "ccy": "currency",
    "rate currency": "currency",
    "currency": "currency"
}

def clean_column_name(col: str) -> str:
    """Normalize string for exact matching (lowercase, strip whitespace)."""
    return col.strip().lower()

class Mapper:
    def __init__(self, use_llm: bool = True, model_name: str = "llama3"):
        """
        Initializes the hybrid mapper. 
        Uses local Ollama for the LLM component.
        """
        self.use_llm = use_llm
        self.model_name = model_name
        if self.use_llm:
            try:
                import ollama
                self.ollama = ollama
            except ImportError:
                print("Warning: ollama library not found. Falling back to heuristics only.")
                self.use_llm = False
            
    def map_columns(self, columns: List[str]) -> RFPMappingResult:
        """
        Maps a list of incoming columns to the target schema using heuristics first, 
        then falling back to the LLM for complex/ambiguous cases.
        """
        result_mappings = []
        unmapped_columns = []
        
        # 1. First Pass: Heuristic Exact Matching
        for col in columns:
            cleaned_col = clean_column_name(col)
            if cleaned_col in EXACT_MATCH_DICT:
                target_field = EXACT_MATCH_DICT[cleaned_col]
                result_mappings.append(
                    ColumnMapping(
                        input_column=col,
                        mapped_target_field=target_field,
                        confidence_score=1.0,
                        reasoning=f"Exact heuristic match for '{cleaned_col}'"
                    )
                )
            else:
                unmapped_columns.append(col)
                
        # 2. Second Pass: LLM Semantic Mapping (for remaining columns)
        if unmapped_columns and self.use_llm:
           llm_mappings = self._call_llm(unmapped_columns, context_columns=columns)
           result_mappings.extend(llm_mappings)
        elif unmapped_columns and not self.use_llm:
           # Graceful fallback if no LLM is available
           for col in unmapped_columns:
               result_mappings.append(
                   ColumnMapping(
                       input_column=col,
                       mapped_target_field="unmapped",
                       confidence_score=0.0,
                       reasoning="LLM mapping is disabled or unavailable. No exact heuristic match found."
                   )
               )

        return RFPMappingResult(mappings=result_mappings)

    def _call_llm(self, target_columns: List[str], context_columns: List[str]) -> List[ColumnMapping]:
        """
        Helper method to isolate LLM interaction.
        Uses structured outputs to guarantee schema alignment.
        """
        prompt = f"""
You are an expert logistics data engineer. Your task is to map completely arbitrary and non-standard Request for Proposal (RFP) column headers to a strict internal target schema.

The full list of all columns in the RFP is: {context_columns}. 
(Use this full list to understand context. E.g., if you see "From" and "To", they likely represent origin and destination).

Your goal is to map the follow specific, uniquely unmapped columns: {target_columns}

Your target schema allows ONLY the following fields:
- origin_port
- destination_port
- container_type_20gp_rate
- container_type_40hq_rate
- estimated_time_of_departure
- transit_time_days
- currency
- unmapped (if it genuinely doesn't fit any)

Rules:
1. Provide a confidence score (0.0 to 1.0).
2. For complex columns like "20FT USD", it maps to a rate ("container_type_20gp_rate"), but the "USD" is implicit metadata. Extract "USD" into the `extracted_metadata` field. 
3. "20FT" or "20'" typically means "container_type_20gp_rate". 
4. "40FT" or "40' HC" typically means "container_type_40hq_rate".
5. Make sure the output exactly matches the JSON schema requested.
"""
        try:
            response = self.ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format=RFPMappingResult.model_json_schema(),
                options={'temperature': 0.1}
            )

            # Use model_validate_json to parse the strong typed pydantic response
            llm_result = RFPMappingResult.model_validate_json(response['message']['content'])
            return llm_result.mappings
        except Exception as e:
           # Fallback mechanism if structure breaks
           print(f"Failed to parse Ollama JSON output: {e}")
           return []
