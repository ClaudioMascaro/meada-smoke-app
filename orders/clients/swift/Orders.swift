import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

private func ordersBase() -> String {
    ProcessInfo.processInfo.environment["SMOKE_ORDERS_URL"]!
}

func sendOrder() async throws {
    var order = URLRequest(url: URL(string: ordersBase() + "/orders")!)
    order.httpMethod = "POST"
    _ = try await URLSession.shared.data(for: order)
}
