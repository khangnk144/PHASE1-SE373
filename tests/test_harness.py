import pytest

from evals.cases import CASES


@pytest.mark.parametrize("name,case", CASES, ids=[name for name, _ in CASES])
def test_phase1_case(tmp_path, name, case):
    case(tmp_path / name)
