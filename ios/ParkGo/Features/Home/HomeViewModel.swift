import Foundation
import Observation

@Observable
@MainActor
final class HomeViewModel {
    private let repository: any ParkingRepository
    var vehicles: [Vehicle] = []
    var zones: [ParkingZone] = []
    var selectedVehicle: Vehicle?
    var selectedZone: ParkingZone?
    var loading = false
    var error: ParkGoError?

    init(repository: any ParkingRepository) { self.repository = repository }

    func load(latitude: Double, longitude: Double) async {
        loading = true
        defer { loading = false }
        do {
            async let vehicleRequest = repository.vehicles()
            async let zoneRequest = repository.nearby(
                latitude: latitude,
                longitude: longitude,
                radius: 2_000
            )
            let (vehicles, zones) = try await (vehicleRequest, zoneRequest)
            self.vehicles = vehicles
            self.zones = zones
            selectedVehicle = vehicles.first(where: \.isDefault) ?? vehicles.first
            selectedZone = zones.first
            error = zones.isEmpty ? .noParkingNearby : nil
        } catch let value as ParkGoError {
            error = value
        } catch {
            self.error = .server(message: error.localizedDescription)
        }
    }
}
