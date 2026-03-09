import pytest
from rfp_mapper.mapper import Mapper

# We use the module level for the tests
@pytest.fixture
def mapper():
    # Allow testing without an LLM running locally unless specifically configured for it
    return Mapper(use_llm=False)

def test_example_1(mapper):
    columns = [
        "Orig Port",
        "Destination",
        "20GP",
        "40HQ Rate",
        "ETD",
        "Transit (days)",
        "Currency"
    ]
    
    result = mapper.map_columns(columns)
    mapped_dict = {m.input_column: m.mapped_target_field for m in result.mappings}
    
    # Exact heuristic matches
    assert mapped_dict.get("Orig Port") == "origin_port"
    assert mapped_dict.get("Destination") == "destination_port"
    assert mapped_dict.get("20GP") == "container_type_20gp_rate"
    assert mapped_dict.get("40HQ Rate") == "container_type_40hq_rate"
    assert mapped_dict.get("ETD") == "estimated_time_of_departure"
    assert mapped_dict.get("Transit (days)") == "transit_time_days"
    assert mapped_dict.get("Currency") == "currency"

def test_example_2(mapper):
    columns = [
        "POL", 
        "POD", 
        "Rate_20", 
        "Rate_40HC", 
        "Departure", 
        "T/T", 
        "Curr"
    ]
    result = mapper.map_columns(columns)
    mapped_dict = {m.input_column: m.mapped_target_field for m in result.mappings}
    
    assert mapped_dict.get("POL") == "origin_port"
    assert mapped_dict.get("POD") == "destination_port"
    assert mapped_dict.get("Departure") == "estimated_time_of_departure"
    assert mapped_dict.get("T/T") == "transit_time_days"
    assert mapped_dict.get("Curr") == "currency"
    
    # LLM dependent assertions
    if mapper.use_llm:
        assert mapped_dict.get("Rate_20") == "container_type_20gp_rate"
        assert mapped_dict.get("Rate_40HC") == "container_type_40hq_rate"

def test_example_3(mapper):
    columns = [
        "Load Port",
        "Discharge Port",
        "20’",
        "40’ HC",
        "Sailing Date",
        "Duration",
        "Rate Currency"
    ]
    result = mapper.map_columns(columns)
    mapped_dict = {m.input_column: m.mapped_target_field for m in result.mappings}
    
    assert mapped_dict.get("Load Port") == "origin_port"
    assert mapped_dict.get("Discharge Port") == "destination_port"
    assert mapped_dict.get("Sailing Date") == "estimated_time_of_departure"
    assert mapped_dict.get("Duration") == "transit_time_days"
    assert mapped_dict.get("Rate Currency") == "currency"
    
    if mapper.use_llm:
        assert mapped_dict.get("20’") == "container_type_20gp_rate"
        assert mapped_dict.get("40’ HC") == "container_type_40hq_rate"

def test_example_4_complex(mapper):
    columns = [
        "From",
        "To",
        "20FT USD",
        "40FT",
        "ETD (YYYYMMDD)",
        "Transit",
        "CCY"
    ]
    result = mapper.map_columns(columns)
    
    # We want to inspect the full mapping objects here
    mapped_dict = {m.input_column: m.mapped_target_field for m in result.mappings}
    meta_dict = {m.input_column: m.extracted_metadata for m in result.mappings}

    assert mapped_dict.get("CCY") == "currency"
    
    if mapper.use_llm:
        assert mapped_dict.get("From") == "origin_port"
        assert mapped_dict.get("To") == "destination_port"
        assert mapped_dict.get("20FT USD") == "container_type_20gp_rate"
        assert mapped_dict.get("40FT") == "container_type_40hq_rate"
        # Verify LLM metadata extraction
        assert "USD" in str(meta_dict.get("20FT USD", "")).upper()
        # Ensure regex or LLM handles ETD
        etd_target = mapped_dict.get("ETD (YYYYMMDD)")
        assert etd_target == "estimated_time_of_departure"
