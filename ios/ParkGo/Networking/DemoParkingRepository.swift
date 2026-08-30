import Foundation

actor DemoParkingRepository: ParkingRepository {
    private let user = User(id: UUID(), email: "demo@parkgo.local", firstName: "Алексей")
    private var vehicleValues: [Vehicle]
    private let zoneValues: [ParkingZone]
    private var active: ParkingSession?
    private var historyValues: [ParkingSession]

    init() {
        let vehicle = Vehicle(
            id: UUID(),
            plateNumber: "А123АА",
            regionCode: "23",
            displayName: "Toyota RAV4",
            brand: "Toyota",
            model: "RAV4",
            color: "Белый",
            isDefault: true
        )
        let zones = [
        ParkingZone(id: UUID(), zoneNumber: "1001", name: "Красная / Северная", address: "ул. Красная, 122", latitude: 45.0356, longitude: 38.9754, distanceMeters: 24, hourlyRate: 60, currency: "RUB", activeFrom: "08:00", activeUntil: "20:00", isActive: true),
        ParkingZone(id: UUID(), zoneNumber: "1002", name: "Красная / Головатого", address: "ул. Красная, 145", latitude: 45.0391, longitude: 38.9748, distanceMeters: 405, hourlyRate: 60, currency: "RUB", activeFrom: "08:00", activeUntil: "20:00", isActive: true),
        ParkingZone(id: UUID(), zoneNumber: "1003", name: "Театральная площадь", address: "Театральная площадь", latitude: 45.0330, longitude: 38.9747, distanceMeters: 279, hourlyRate: 70, currency: "RUB", activeFrom: "08:00", activeUntil: "22:00", isActive: true)
        ]

        let now = Date.now
        let history = (0..<3).map { index in
            let start = now.addingTimeInterval(Double(-(index + 1) * 86_400 - 6_000))
            return ParkingSession(
                id: UUID(),
                startedAt: start,
                finishedAt: start.addingTimeInterval(Double(3_900 + index * 600)),
                status: .completed,
                calculatedAmount: Decimal(70 + index * 12),
                paidAmount: Decimal(70 + index * 12),
                currency: "RUB",
                paymentStatus: .paid,
                vehicle: vehicle,
                parkingZone: zones[index]
            )
        }
        self.vehicleValues = [vehicle]
        self.zoneValues = zones
        self.historyValues = history
    }

    func signIn(email: String, password: String) async throws -> User { user }
    func register(email: String, password: String, firstName: String?) async throws -> User { user }
    func signOut() async {}
    func vehicles() async throws -> [Vehicle] { vehicleValues }

    func addVehicle(plate: String, region: String, name: String) async throws -> Vehicle {
        let value = Vehicle(id: UUID(), plateNumber: plate.uppercased(), regionCode: region, displayName: name, brand: nil, model: nil, color: nil, isDefault: vehicleValues.isEmpty)
        vehicleValues.append(value)
        return value
    }

    func nearby(latitude: Double, longitude: Double, radius: Int) async throws -> [ParkingZone] {
        zoneValues
    }

    func currentSession() async throws -> ParkingSession? { active }

    func start(vehicleID: UUID, zoneID: UUID) async throws -> ParkingSession {
        guard active == nil else { throw ParkGoError.sessionAlreadyActive }
        guard let vehicle = vehicleValues.first(where: { $0.id == vehicleID }),
              let zone = zoneValues.first(where: { $0.id == zoneID })
        else { throw ParkGoError.server(message: "Автомобиль или парковка не найдены.") }
        let value = ParkingSession(id: UUID(), startedAt: .now, finishedAt: nil, status: .active, calculatedAmount: 0, paidAmount: 0, currency: "RUB", paymentStatus: .pending, vehicle: vehicle, parkingZone: zone)
        active = value
        return value
    }

    func stop(sessionID: UUID) async throws -> ParkingSession {
        guard let current = active, current.id == sessionID else {
            throw ParkGoError.server(message: "Активная парковка не найдена.")
        }
        let elapsed = max(60, Date.now.timeIntervalSince(current.startedAt))
        let amount = current.parkingZone.hourlyRate * Decimal(elapsed / 3_600)
        let completed = ParkingSession(id: current.id, startedAt: current.startedAt, finishedAt: .now, status: .completed, calculatedAmount: amount, paidAmount: amount, currency: current.currency, paymentStatus: .paid, vehicle: current.vehicle, parkingZone: current.parkingZone)
        active = nil
        historyValues.insert(completed, at: 0)
        return completed
    }

    func history() async throws -> [ParkingSession] { historyValues }

    func stats() async throws -> ParkingStats {
        let total = historyValues.reduce(Decimal.zero) { $0 + $1.paidAmount }
        return ParkingStats(
            period: "2026-08",
            parkingCount: historyValues.count,
            totalDurationSeconds: Int(historyValues.reduce(0) { $0 + $1.duration() }),
            totalSpent: total,
            averageAmount: historyValues.isEmpty ? 0 : total / Decimal(historyValues.count),
            mostUsedZoneNumber: "1001"
        )
    }
}
