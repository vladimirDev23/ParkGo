import Foundation

protocol ParkingRepository: Sendable {
    func signIn(email: String, password: String) async throws -> User
    func register(email: String, password: String, firstName: String?) async throws -> User
    func signOut() async
    func vehicles() async throws -> [Vehicle]
    func addVehicle(plate: String, region: String, name: String) async throws -> Vehicle
    func nearby(latitude: Double, longitude: Double, radius: Int) async throws -> [ParkingZone]
    func currentSession() async throws -> ParkingSession?
    func start(vehicleID: UUID, zoneID: UUID) async throws -> ParkingSession
    func stop(sessionID: UUID) async throws -> ParkingSession
    func history() async throws -> [ParkingSession]
    func stats() async throws -> ParkingStats
}

final class APIParkingRepository: ParkingRepository, Sendable {
    private let client: APIClient

    init(client: APIClient) { self.client = client }

    func signIn(email: String, password: String) async throws -> User {
        let endpoint = try Endpoint<TokenPairDTO>.json(
            path: "auth/login",
            method: .post,
            body: ["email": email, "password": password],
            authenticated: false
        )
        let pair = try await client.send(endpoint)
        try await client.store(pair)
        return pair.user.domain()
    }

    func register(email: String, password: String, firstName: String?) async throws -> User {
        struct Body: Encodable, Sendable {
            let email: String
            let password: String
            let firstName: String?
        }
        let endpoint = try Endpoint<TokenPairDTO>.json(
            path: "auth/register",
            method: .post,
            body: Body(email: email, password: password, firstName: firstName),
            authenticated: false
        )
        let pair = try await client.send(endpoint)
        try await client.store(pair)
        return pair.user.domain()
    }

    func signOut() async { await client.logout() }

    func vehicles() async throws -> [Vehicle] {
        try await client.send(Endpoint<[VehicleDTO]>(path: "vehicles")).map { $0.domain() }
    }

    func addVehicle(plate: String, region: String, name: String) async throws -> Vehicle {
        struct Body: Encodable, Sendable {
            let plateNumber: String
            let regionCode: String
            let displayName: String
        }
        let dto = try await client.send(
            Endpoint<VehicleDTO>.json(
                path: "vehicles",
                method: .post,
                body: Body(plateNumber: plate, regionCode: region, displayName: name)
            )
        )
        return dto.domain()
    }

    func nearby(latitude: Double, longitude: Double, radius: Int) async throws -> [ParkingZone] {
        let dto = try await client.send(
            Endpoint<NearbyZonesDTO>(
                path: "parking/nearby",
                query: [
                    URLQueryItem(name: "latitude", value: latitude.formatted(.number.precision(.fractionLength(6)))),
                    URLQueryItem(name: "longitude", value: longitude.formatted(.number.precision(.fractionLength(6)))),
                    URLQueryItem(name: "radius", value: String(radius))
                ]
            )
        )
        return try dto.zones.map { try $0.domain() }
    }

    func currentSession() async throws -> ParkingSession? {
        let dto = try await client.send(Endpoint<SessionDTO?>(path: "parking/sessions/current"))
        return try dto?.domain()
    }

    func start(vehicleID: UUID, zoneID: UUID) async throws -> ParkingSession {
        struct Body: Encodable, Sendable {
            let vehicleID: UUID
            let parkingZoneID: UUID
        }
        let dto = try await client.send(
            Endpoint<SessionDTO>.json(
                path: "parking/sessions",
                method: .post,
                body: Body(vehicleID: vehicleID, parkingZoneID: zoneID)
            )
        )
        return try dto.domain()
    }

    func stop(sessionID: UUID) async throws -> ParkingSession {
        let dto = try await client.send(
            Endpoint<SessionDTO>(path: "parking/sessions/\(sessionID)/stop", method: .post)
        )
        return try dto.domain()
    }

    func history() async throws -> [ParkingSession] {
        let dto = try await client.send(Endpoint<HistoryDTO>(path: "parking/history"))
        return try dto.sessions.map { try $0.domain() }
    }

    func stats() async throws -> ParkingStats {
        try await client.send(Endpoint<StatsDTO>(path: "parking/stats")).domain()
    }
}
