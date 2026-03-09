from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

# These are the absolute exact Target Schema Fields defined in the objective.
TargetFieldAlias = Literal[
    "origin_port",
    "destination_port",
    "container_type_20gp_rate",
    "container_type_40hq_rate",
    "estimated_time_of_departure",
    "transit_time_days",
    "currency",
    "unmapped" # For columns that do not map to the target schema
]

class ColumnMapping(BaseModel):
    """Represents a single input column mapped to a standard target field."""
    input_column: str = Field(description="The original column name from the RFP.")
    mapped_target_field: TargetFieldAlias = Field(description="The standardized target field name.")
    confidence_score: float = Field(
        description="Confidence score between 0.0 and 1.0. 1.0 is highest confidence.",
        ge=0.0, le=1.0
    )
    reasoning: str = Field(description="Brief explanation of why this mapping was chosen.")
    extracted_metadata: Optional[str] = Field(
        description="Any implicit metadata extracted from the column name itself (e.g. 'USD' from '20FT USD').",
        default=None
    )

class RFPMappingResult(BaseModel):
    """The complete mapping result for a set of columns."""
    mappings: List[ColumnMapping] = Field(description="The list of mapped columns.")
