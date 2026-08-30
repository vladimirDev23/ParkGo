import CoreLocation
import Observation

@Observable
@MainActor
final class LocationService: NSObject, CLLocationManagerDelegate {
    enum State: Equatable {
        case idle, requesting, available, denied, unavailable
    }

    private let manager = CLLocationManager()
    private let demoCoordinate = CLLocationCoordinate2D(latitude: 45.03547, longitude: 38.97531)
    private let useDemoLocation: Bool
    var state: State = .idle
    var coordinate: CLLocationCoordinate2D?
    var accuracyReduced = false
    var onRegionExit: ((String) -> Void)?

    init(useDemoLocation: Bool) {
        self.useDemoLocation = useDemoLocation
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        if useDemoLocation {
            coordinate = demoCoordinate
            state = .available
        }
    }

    func requestPermissionAndLocation() {
        if useDemoLocation {
            coordinate = demoCoordinate
            state = .available
            return
        }
        state = .requesting
        manager.requestWhenInUseAuthorization()
        manager.requestLocation()
    }

    func beginGeofence(for zone: ParkingZone) {
        guard CLLocationManager.isMonitoringAvailable(for: CLCircularRegion.self) else { return }
        manager.monitoredRegions.forEach { manager.stopMonitoring(for: $0) }
        let region = CLCircularRegion(
            center: zone.coordinate,
            radius: min(150, manager.maximumRegionMonitoringDistance),
            identifier: "parking-\(zone.zoneNumber)"
        )
        region.notifyOnEntry = false
        region.notifyOnExit = true
        manager.startMonitoring(for: region)
    }

    func stopGeofence() {
        manager.monitoredRegions.forEach { manager.stopMonitoring(for: $0) }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        let accuracyAuthorization = manager.accuracyAuthorization
        let authorizationStatus = manager.authorizationStatus
        Task { @MainActor [weak self] in
            guard let self else { return }
            accuracyReduced = accuracyAuthorization == .reducedAccuracy
            switch authorizationStatus {
            case .authorizedAlways, .authorizedWhenInUse:
                state = .requesting
                self.manager.requestLocation()
            case .denied, .restricted:
                state = .denied
            case .notDetermined:
                state = .idle
            @unknown default:
                state = .unavailable
            }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let latest = locations.last else { return }
        let latestCoordinate = latest.coordinate
        Task { @MainActor [weak self] in
            guard let self else { return }
            coordinate = latestCoordinate
            state = .available
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor [weak self] in self?.state = .unavailable }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        let identifier = region.identifier
        Task { @MainActor [weak self] in self?.onRegionExit?(identifier) }
    }
}
