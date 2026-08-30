import CoreLocation
import Foundation

struct User: Identifiable, Codable, Equatable, Sendable {
    let id: UUID
    let email: String
    let firstName: String?
}

struct Vehicle: Identifiable, Codable, Equatable, Sendable {
    let id: UUID
    var plateNumber: String
    var regionCode: String
    var displayName: String
    var brand: String?
    var model: String?
    var color: String?
    var isDefault: Bool

    var formattedPlate: String {
        regionCode.isEmpty ? plateNumber : "\(plateNumber) \(regionCode)"
    }
}

struct ParkingZone: Identifiable, Codable, Equatable, Sendable {
    let id: UUID
    let zoneNumber: String
    let name: String
    let address: String
    let latitude: Double
    let longitude: Double
    let distanceMeters: Int?
    let hourlyRate: Decimal
    let currency: String
    let activeFrom: String?
    let activeUntil: String?
    let isActive: Bool

    var coordinate: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }
}

enum ParkingStatus: String, Codable, Sendable {
    case active
    case completed
    case cancelled
    case failed
}

enum PaymentStatus: String, Codable, Sendable {
    case pending
    case paid
    case failed
    case refunded
}

struct ParkingSession: Identifiable, Codable, Equatable, Sendable {
    let id: UUID
    let startedAt: Date
    let finishedAt: Date?
    let status: ParkingStatus
    let calculatedAmount: Decimal
    let paidAmount: Decimal
    let currency: String
    let paymentStatus: PaymentStatus
    let vehicle: Vehicle
    let parkingZone: ParkingZone

    func duration(at date: Date = .now) -> TimeInterval {
        max(0, (finishedAt ?? date).timeIntervalSince(startedAt))
    }
}

struct ParkingStats: Codable, Equatable, Sendable {
    let period: String
    let parkingCount: Int
    let totalDurationSeconds: Int
    let totalSpent: Decimal
    let averageAmount: Decimal
    let mostUsedZoneNumber: String?
}
