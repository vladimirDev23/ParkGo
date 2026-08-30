import Foundation

private func decimal(from value: String) throws -> Decimal {
    guard let decimal = Decimal(string: value, locale: Locale(identifier: "en_US_POSIX")) else {
        throw DecodingError.dataCorrupted(
            .init(codingPath: [], debugDescription: "Invalid decimal value: \(value)")
        )
    }
    return decimal
}

struct UserDTO: Codable, Sendable {
    let id: UUID
    let email: String
    let firstName: String?

    func domain() -> User { User(id: id, email: email, firstName: firstName) }
}

struct TokenPairDTO: Codable, Sendable {
    let accessToken: String
    let refreshToken: String
    let expiresIn: Int
    let user: UserDTO
}

struct VehicleDTO: Codable, Sendable {
    let id: UUID
    let plateNumber: String
    let regionCode: String
    let displayName: String
    let brand: String?
    let model: String?
    let color: String?
    let isDefault: Bool

    func domain() -> Vehicle {
        Vehicle(
            id: id,
            plateNumber: plateNumber,
            regionCode: regionCode,
            displayName: displayName,
            brand: brand,
            model: model,
            color: color,
            isDefault: isDefault
        )
    }
}

struct ZoneDTO: Codable, Sendable {
    let id: UUID
    let zoneNumber: String
    let name: String
    let address: String
    let latitude: Double
    let longitude: Double
    let distanceMeters: Int?
    let hourlyRate: String
    let currency: String
    let activeFrom: String?
    let activeUntil: String?
    let isActive: Bool

    func domain() throws -> ParkingZone {
        ParkingZone(
            id: id,
            zoneNumber: zoneNumber,
            name: name,
            address: address,
            latitude: latitude,
            longitude: longitude,
            distanceMeters: distanceMeters,
            hourlyRate: try decimal(from: hourlyRate),
            currency: currency,
            activeFrom: activeFrom,
            activeUntil: activeUntil,
            isActive: isActive
        )
    }
}

struct NearbyZonesDTO: Codable, Sendable { let zones: [ZoneDTO] }
struct HistoryDTO: Codable, Sendable { let sessions: [SessionDTO] }

struct SessionDTO: Codable, Sendable {
    let id: UUID
    let startedAt: Date
    let finishedAt: Date?
    let status: ParkingStatus
    let calculatedAmount: String
    let paidAmount: String
    let currency: String
    let paymentStatus: PaymentStatus
    let vehicle: VehicleDTO
    let parkingZone: ZoneDTO

    func domain() throws -> ParkingSession {
        ParkingSession(
            id: id,
            startedAt: startedAt,
            finishedAt: finishedAt,
            status: status,
            calculatedAmount: try decimal(from: calculatedAmount),
            paidAmount: try decimal(from: paidAmount),
            currency: currency,
            paymentStatus: paymentStatus,
            vehicle: vehicle.domain(),
            parkingZone: try parkingZone.domain()
        )
    }
}

struct StatsDTO: Codable, Sendable {
    let period: String
    let parkingCount: Int
    let totalDurationSeconds: Int
    let totalSpent: String
    let averageAmount: String
    let mostUsedZoneNumber: String?

    func domain() throws -> ParkingStats {
        ParkingStats(
            period: period,
            parkingCount: parkingCount,
            totalDurationSeconds: totalDurationSeconds,
            totalSpent: try decimal(from: totalSpent),
            averageAmount: try decimal(from: averageAmount),
            mostUsedZoneNumber: mostUsedZoneNumber
        )
    }
}

struct ErrorEnvelopeDTO: Codable, Sendable {
    struct Body: Codable, Sendable {
        let code: String
        let message: String
    }
    let error: Body
}
