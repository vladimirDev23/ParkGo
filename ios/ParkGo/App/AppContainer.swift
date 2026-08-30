import Foundation
import Observation

@Observable
@MainActor
final class AppContainer {
    enum AuthenticationState: Equatable {
        case loading, signedOut, signedIn(User)
    }

    let configuration: AppConfiguration
    let repository: any ParkingRepository
    let location: LocationService
    let notificationService: NotificationService
    let biometricService = BiometricService()
    let sessionStore: ParkingSessionStore
    var authentication: AuthenticationState = .loading

    init(configuration: AppConfiguration = .current) {
        self.configuration = configuration
        let repository: any ParkingRepository
        if configuration.offlineDemo {
            repository = DemoParkingRepository()
        } else {
            let tokens = TokenStore()
            let client = APIClient(baseURL: configuration.apiBaseURL, tokenStore: tokens)
            let api = APIParkingRepository(client: client)
            if configuration.presentationMode {
                repository = PresentationRepository(
                    primary: api,
                    fallback: DemoParkingRepository()
                )
            } else {
                repository = api
            }
        }
        self.repository = repository
        let location = LocationService(useDemoLocation: configuration.presentationMode)
        self.location = location
        let notifications = NotificationService()
        notificationService = notifications
        sessionStore = ParkingSessionStore(
            repository: repository,
            liveActivity: LiveActivityService(),
            location: location,
            notifications: notifications
        )
        location.onRegionExit = { [weak notifications] identifier in
            let zone = identifier.replacingOccurrences(of: "parking-", with: "")
            Task { await notifications?.scheduleExitReminder(zoneNumber: zone) }
        }
    }

    func bootstrap() async {
        await notificationService.requestAuthorization()
        if configuration.presentationMode {
            do {
                let user = try await repository.signIn(
                    email: "demo@parkgo.local",
                    password: "DemoPass123!"
                )
                authentication = .signedIn(user)
                await sessionStore.synchronize()
                return
            } catch {
                authentication = .signedOut
                return
            }
        }
        do {
            _ = try await repository.vehicles()
            authentication = .signedIn(User(id: UUID(), email: "", firstName: nil))
            await sessionStore.synchronize()
        } catch {
            authentication = .signedOut
        }
    }

    func signIn(email: String, password: String) async throws {
        let user = try await repository.signIn(email: email, password: password)
        authentication = .signedIn(user)
        await sessionStore.synchronize()
    }

    func register(email: String, password: String, firstName: String?) async throws {
        let user = try await repository.register(
            email: email,
            password: password,
            firstName: firstName
        )
        authentication = .signedIn(user)
    }

    func signOut() async {
        await repository.signOut()
        authentication = .signedOut
    }
}
