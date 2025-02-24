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
    {
        "model_year": "2019",
        "signalset": "default.json",
        "tests": [
            ("60DF10562D2400027", {"4SERIES_VSS_INSTR": 39}),
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
