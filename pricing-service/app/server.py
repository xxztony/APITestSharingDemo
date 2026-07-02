from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection

from app.pricing_service import pricing_pb2, pricing_pb2_grpc, PricingService
from app.tracing import configure_tracing, instrument_grpc_server

configure_tracing("pricing-service")
instrument_grpc_server()


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pricing_pb2_grpc.add_PricingServiceServicer_to_server(PricingService(), server)

    service_names = (
        pricing_pb2.DESCRIPTOR.services_by_name["PricingService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    server.add_insecure_port("[::]:50051")
    server.start()
    print("Pricing gRPC service listening on :50051", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
