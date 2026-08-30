import ActivityKit
import Foundation

struct ParkingActivityAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        let startedAt: Date
        let estimatedAmount: Decimal
    }

    let sessionID: UUID
    let zoneNumber: String
    let vehicleName: String
    let plateNumber: String
    let hourlyRate: Decimal
}
