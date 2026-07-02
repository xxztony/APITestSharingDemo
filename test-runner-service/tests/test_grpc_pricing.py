from app.clients.pricing_grpc_client import get_price_call, stream_prices_call


def test_get_price_with_valid_symbol_should_return_bid_ask_mid(record_case):
    call = get_price_call("LME-CA")
    body = call["response_payload"]
    record_case(
        case_id="GRPC-001",
        name="GetPrice with valid symbol should return bid, ask, mid",
        protocol="gRPC",
        service="pricing-service",
        endpoint="PricingService/GetPrice",
        method="UNARY",
        expected_result="OK response with bid/ask/mid",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == "OK"
    assert body["symbol"] == "LME-CA"
    assert {"bid", "ask", "mid"}.issubset(body.keys())


def test_get_price_should_ensure_bid_lower_than_ask(record_case):
    call = get_price_call("LME-AL")
    body = call["response_payload"]
    record_case(
        case_id="GRPC-002",
        name="GetPrice should ensure bid lower than ask",
        protocol="gRPC",
        service="pricing-service",
        endpoint="PricingService/GetPrice",
        method="UNARY",
        expected_result="bid < ask",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == "OK"
    assert body["bid"] < body["ask"]


def test_get_price_should_ensure_mid_is_average(record_case):
    call = get_price_call("LME-ZN")
    body = call["response_payload"]
    expected_mid = round((body["bid"] + body["ask"]) / 2, 4)
    record_case(
        case_id="GRPC-003",
        name="GetPrice should ensure mid equals average of bid and ask",
        protocol="gRPC",
        service="pricing-service",
        endpoint="PricingService/GetPrice",
        method="UNARY",
        expected_result=f"mid equals {expected_mid}",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == "OK"
    assert body["mid"] == expected_mid


def test_get_price_with_invalid_symbol_should_return_not_found(record_case):
    call = get_price_call("BAD-SYMBOL")
    record_case(
        case_id="GRPC-004",
        name="GetPrice with invalid symbol should return NOT_FOUND",
        protocol="gRPC",
        service="pricing-service",
        endpoint="PricingService/GetPrice",
        method="UNARY",
        expected_result="gRPC NOT_FOUND",
        actual_result=str(call["response_payload"]),
        **call,
    )
    assert call["response_status"] == "NOT_FOUND"


def test_stream_prices_should_return_five_price_updates(record_case):
    call = stream_prices_call("LME-NI")
    updates = call["response_payload"]
    record_case(
        case_id="GRPC-005",
        name="StreamPrices should return 5 price updates",
        protocol="gRPC",
        service="pricing-service",
        endpoint="PricingService/StreamPrices",
        method="SERVER_STREAMING",
        expected_result="5 updates",
        actual_result=str(updates),
        **call,
    )
    assert call["response_status"] == "OK"
    assert len(updates) == 5

