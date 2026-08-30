import XCTest
@testable import ParkGo

@MainActor
final class ParkGoTests: XCTestCase {
    func testPriceAndDurationFormatting() {
        XCTAssertEqual(ParkGoFormatting.amount(Decimal(84)), "84 ₽")
        XCTAssertEqual(ParkGoFormatting.duration(5_077), "1 ч 24 мин")
        XCTAssertEqual(ParkGoFormatting.duration(5_077, compact: true), "01:24:37")
    }

    func testDemoSessionStateTransitions() async throws {
        let repository = DemoParkingRepository()
        let vehicle = try await repository.vehicles()[0]
        let zone = try await repository.nearby(latitude: 45.03547, longitude: 38.97531, radius: 1_500)[0]
        let started = try await repository.start(vehicleID: vehicle.id, zoneID: zone.id)
        XCTAssertEqual(started.status, .active)
        XCTAssertNotNil(try await repository.currentSession())
        let stopped = try await repository.stop(sessionID: started.id)
        XCTAssertEqual(stopped.status, .completed)
        XCTAssertNil(try await repository.currentSession())
        XCTAssertEqual(try await repository.history().first?.id, started.id)
    }

    func testDefaultVehicleSelection() async throws {
        let repository = DemoParkingRepository()
        let values = try await repository.vehicles()
        XCTAssertEqual(values.first(where: \.isDefault)?.displayName, "Toyota RAV4")
    }

    func testDTOSeparatesWireDecimalFromDomain() throws {
        let dto = ZoneDTO(
            id: UUID(),
            zoneNumber: "1001",
            name: "Demo",
            address: "Краснодар",
            latitude: 45.0,
            longitude: 39.0,
            distanceMeters: 84,
            hourlyRate: "60.00",
            currency: "RUB",
            activeFrom: "08:00",
            activeUntil: "20:00",
            isActive: true
        )
        XCTAssertEqual(try dto.domain().hourlyRate, Decimal(60))
    }
}
