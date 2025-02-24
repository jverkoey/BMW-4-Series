import glob
import os
import pytest
from pathlib import Path
from typing import Dict, Any

# These will be imported from the schemas repository
from schemas.python.can_frame import CANIDFormat
from schemas.python.json_formatter import format_file
from schemas.python.signals_testing import obd_testrunner

REPO_ROOT = Path(__file__).parent.parent.absolute()

TEST_CASES = [
    # TODO: Implement real tests below with vehicle data.
    # 2019 model year
    {
        "model_year": "2019",
        "signalset": "default.json",
        "tests": [
            ("60DF106621000000000", {"UNK_1000": 0}),

            ("60DF10662D223000101", {"UNK_D223": 0}),
            
            ("60DF10562D23B0001", {"UNK_D23B": 0}),
            
            ("60DF10562D2400027", {"UNK_D240": 0}),
            
            ("60DF10562D24100FD", {"UNK_D241": 0}),
            
            ("60DF10562D2420000", {"UNK_D242": 0}),
            
            ("60DF10562D2430000", {"UNK_D243": 0}),
            
            ("60DF10562D2440000", {"UNK_D244": 0}),
            
            ("60DF10562D2450001", {"UNK_D245": 0}),
            
            ("60DF10562D2460000", {"UNK_D246": 0}),
            
            ("60DF10562D24C0001", {"UNK_D24C": 0}),
            
            ("60DF10562D3000001", {"UNK_D300": 0}),
            
            ("60DF10562D3030000", {"UNK_D303": 0}),
            
            ("""60DF1100A62D31C3C44
                60DF1212814110B0EFF""", {"UNK_D31C": 60}),
                
            ("""60DF1100B62D3770000
                60DF121000000000000""", {"UNK_D377": 0}),
                
            ("60DF10562D84A0000", {"UNK_D84A": 0}),
            
            ("""60DF1100762F1000181
                60DF1210001FFFFFFFF""", {"UNK_F100": 1}),
                
            ("""60DF1103462F1010101
                60DF12100041712088B
                60DF122009601000010
                60DF123000000010000
                60DF1242FA901000006
                60DF12500002FAD0900
                60DF1260108000041FD
                60DF127030803050000
                60DF1285710040000FF""", {"UNK_F101": 1}),
                
            ("""60DF1102C62F1020101
                60DF12100031712088B
                60DF122009601000010
                60DF123000000010000
                60DF1242FA901000006
                60DF12500002FAD0900
                60DF1260108000041FD
                60DF127030803FFFFFF""", {"UNK_F102": 1})
        ]
    },
]

def load_signalset(filename: str) -> str:
    """Load a signalset JSON file from the standard location."""
    signalset_path = REPO_ROOT / "signalsets" / "v3" / filename
    with open(signalset_path) as f:
        return f.read()

@pytest.mark.parametrize(
    "test_group",
    TEST_CASES,
    ids=lambda test_case: f"MY{test_case['model_year']}"
)
def test_signals(test_group: Dict[str, Any]):
    """Test signal decoding against known responses."""
    signalset_json = load_signalset(test_group["signalset"])

    # Run each test case in the group
    for response_hex, expected_values in test_group["tests"]:
        try:
            obd_testrunner(
                signalset_json,
                response_hex,
                expected_values,
                can_id_format=CANIDFormat.ELEVEN_BIT,
                extended_addressing_enabled=True
            )
        except Exception as e:
            pytest.fail(
                f"Failed on response {response_hex} "
                f"(Model Year: {test_group['model_year']}, "
                f"Signalset: {test_group['signalset']}): {e}"
            )

def get_json_files():
    """Get all JSON files from the signalsets/v3 directory."""
    signalsets_path = os.path.join(REPO_ROOT, 'signalsets', 'v3')
    json_files = glob.glob(os.path.join(signalsets_path, '*.json'))
    # Convert full paths to relative filenames
    return [os.path.basename(f) for f in json_files]

@pytest.mark.parametrize("test_file",
    get_json_files(),
    ids=lambda x: x.split('.')[0].replace('-', '_')  # Create readable test IDs
)
def test_formatting(test_file):
    """Test signal set formatting for all vehicle models in signalsets/v3/."""
    signalset_path = os.path.join(REPO_ROOT, 'signalsets', 'v3', test_file)

    formatted = format_file(signalset_path)

    with open(signalset_path) as f:
        assert f.read() == formatted

if __name__ == '__main__':
    pytest.main([__file__])
