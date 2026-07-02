import pytest


@pytest.fixture
def record_case(request):
    def _record(**case):
        request.node.user_properties.append(("case_record", case))

    return _record

