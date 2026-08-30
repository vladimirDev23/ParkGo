import Foundation
import Observation

@Observable
@MainActor
final class ParkingSessionStore {
    enum Operation: Equatable { case idle, loading, starting, stopping }

    private let repository: any ParkingRepository
    private let liveActivity: LiveActivityService
    private let location: LocationService
    private let notifications: NotificationService
    private var timerTask: Task<Void, Never>?

    var activeSession: ParkingSession?
    var now = Date.now
    var operation: Operation = .idle
    var error: ParkGoError?
    var completionMessage: String?

    init(
        repository: any ParkingRepository,
        liveActivity: LiveActivityService,
        location: LocationService,
        notifications: NotificationService
    ) {
        self.repository = repository
        self.liveActivity = liveActivity
        self.location = location
        self.notifications = notifications
    }

    deinit { timerTask?.cancel() }

    var elapsed: TimeInterval { activeSession?.duration(at: now) ?? 0 }

    var estimatedAmount: Decimal {
        guard let activeSession else { return 0 }
        let hours = Decimal(max(60, elapsed) / 3_600)
        return activeSession.parkingZone.hourlyRate * hours
    }

    func synchronize() async {
        operation = .loading
        defer { operation = .idle }
        do {
            activeSession = try await repository.currentSession()
            if let activeSession {
                beginMonitoring(activeSession)
                await liveActivity.update(
                    session: activeSession,
                    estimatedAmount: estimatedAmount
                )
            } else {
                stopMonitoring()
            }
            error = nil
        } catch let value as ParkGoError {
            error = value
        } catch {
            self.error = .server(message: error.localizedDescription)
        }
    }

    func start(vehicle: Vehicle, zone: ParkingZone) async throws {
        operation = .starting
        defer { operation = .idle }
        do {
            let session = try await repository.start(vehicleID: vehicle.id, zoneID: zone.id)
            activeSession = session
            error = nil
            beginMonitoring(session)
            await liveActivity.start(session: session)
            await notifications.scheduleActiveReminders(session: session)
        } catch let value as ParkGoError {
            error = value
            throw value
        }
    }

    @discardableResult
    func stop() async throws -> ParkingSession {
        guard let session = activeSession else {
            throw ParkGoError.server(message: "Активная парковка не найдена.")
        }
        operation = .stopping
        defer { operation = .idle }
        do {
            let completed = try await repository.stop(sessionID: session.id)
            activeSession = nil
            stopMonitoring()
            await liveActivity.end(sessionID: session.id, finalAmount: completed.paidAmount)
            await notifications.clearParkingReminders()
            error = nil
            completionMessage = "Реальная оплата не производилась. Парковка добавлена в историю."
            return completed
        } catch let value as ParkGoError {
            error = value
            if value == .paymentFailed {
                let lastEstimate = estimatedAmount
                await synchronize()
                await liveActivity.end(sessionID: session.id, finalAmount: lastEstimate)
            }
            throw value
        }
    }

    private func beginMonitoring(_ session: ParkingSession) {
        location.beginGeofence(for: session.parkingZone)
        timerTask?.cancel()
        timerTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(1))
                guard let self else { return }
                now = .now
                if Int(elapsed).isMultiple(of: 60) {
                    await liveActivity.update(
                        session: session,
                        estimatedAmount: estimatedAmount
                    )
                }
            }
        }
    }

    private func stopMonitoring() {
        timerTask?.cancel()
        timerTask = nil
        location.stopGeofence()
    }
}
