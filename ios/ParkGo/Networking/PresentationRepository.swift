import Foundation

actor PresentationRepository: ParkingRepository {
    private let primary: any ParkingRepository
    private let fallback: any ParkingRepository
    private var usingFallback = false

    init(primary: any ParkingRepository, fallback: any ParkingRepository) {
        self.primary = primary
        self.fallback = fallback
    }

    func signIn(email: String, password: String) async throws -> User {
        do {
            return try await primary.signIn(email: email, password: password)
        } catch {
            usingFallback = true
            return try await fallback.signIn(email: email, password: password)
        }
    }

    func register(email: String, password: String, firstName: String?) async throws -> User {
        if usingFallback {
            return try await fallback.register(
                email: email,
                password: password,
                firstName: firstName
            )
        }
        return try await primary.register(email: email, password: password, firstName: firstName)
    }

    func signOut() async {
        if usingFallback { await fallback.signOut() } else { await primary.signOut() }
    }

    func vehicles() async throws -> [Vehicle] {
        try await selected.vehicles()
    }

    func addVehicle(plate: String, region: String, name: String) async throws -> Vehicle {
        try await selected.addVehicle(plate: plate, region: region, name: name)
    }

    func nearby(latitude: Double, longitude: Double, radius: Int) async throws -> [ParkingZone] {
        try await selected.nearby(latitude: latitude, longitude: longitude, radius: radius)
    }

    func currentSession() async throws -> ParkingSession? {
        try await selected.currentSession()
    }

    func start(vehicleID: UUID, zoneID: UUID) async throws -> ParkingSession {
        try await selected.start(vehicleID: vehicleID, zoneID: zoneID)
    }

    func stop(sessionID: UUID) async throws -> ParkingSession {
        try await selected.stop(sessionID: sessionID)
    }

    func history() async throws -> [ParkingSession] {
        try await selected.history()
    }

    func stats() async throws -> ParkingStats {
        try await selected.stats()
    }

    private var selected: any ParkingRepository {
        usingFallback ? fallback : primary
    }
}
