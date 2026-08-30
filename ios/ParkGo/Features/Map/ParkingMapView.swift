import MapKit
import SwiftUI

struct ParkingMapView: View {
    @Environment(AppContainer.self) private var container
    @State private var zones: [ParkingZone] = []
    @State private var vehicles: [Vehicle] = []
    @State private var selectedZoneID: UUID?
    @State private var position: MapCameraPosition = .automatic
    @State private var error: ParkGoError?

    private var selectedZone: ParkingZone? {
        zones.first(where: { $0.id == selectedZoneID })
    }

    var body: some View {
        NavigationStack {
            Map(position: $position, selection: $selectedZoneID) {
                UserAnnotation()
                ForEach(zones) { zone in
                    Marker("№\(zone.zoneNumber)", systemImage: "parkingsign", coordinate: zone.coordinate)
                        .tint(.blue)
                        .tag(zone.id)
                }
            }
            .mapControls { MapCompass(); MapScaleView() }
            .overlay(alignment: .topTrailing) {
                Button {
                    centerOnUser()
                } label: {
                    Image(systemName: "location.fill")
                        .font(.headline)
                        .frame(width: 44, height: 44)
                        .background(.regularMaterial, in: Circle())
                }
                .padding()
                .accessibilityLabel("Показать моё местоположение")
            }
            .safeAreaInset(edge: .top) {
                TestModeBanner(visible: container.configuration.testMode)
            }
            .safeAreaInset(edge: .bottom) {
                if let zone = selectedZone { zoneSheet(zone) }
            }
            .navigationTitle("Карта")
            .navigationBarTitleDisplayMode(.inline)
            .task { await load() }
        }
    }

    private func zoneSheet(_ zone: ParkingZone) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 3) {
                    Text("Парковка №\(zone.zoneNumber)").font(.headline)
                    Text(zone.address).font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
                VStack(alignment: .trailing) {
                    Text("\(ParkGoFormatting.amount(zone.hourlyRate))/час").fontWeight(.semibold)
                    Text(ParkGoFormatting.distance(zone.distanceMeters)).font(.caption).foregroundStyle(.secondary)
                }
            }
            PrimaryActionButton(
                title: "Начать парковку",
                loading: container.sessionStore.operation == .starting,
                disabled: vehicles.isEmpty
                    || container.sessionStore.activeSession != nil
                    || !container.configuration.testMode
            ) {
                guard let vehicle = vehicles.first(where: \.isDefault) ?? vehicles.first else { return }
                Task { try? await container.sessionStore.start(vehicle: vehicle, zone: zone) }
            }
        }
        .padding()
        .background(.ultraThinMaterial)
    }

    private func load() async {
        container.location.requestPermissionAndLocation()
        try? await Task.sleep(for: .milliseconds(250))
        guard let coordinate = container.location.coordinate else {
            error = .locationUnavailable
            return
        }
        do {
            async let loadedZones = container.repository.nearby(
                latitude: coordinate.latitude,
                longitude: coordinate.longitude,
                radius: 3_000
            )
            async let loadedVehicles = container.repository.vehicles()
            (zones, vehicles) = try await (loadedZones, loadedVehicles)
            selectedZoneID = zones.first?.id
            centerOnUser()
        } catch let value as ParkGoError {
            error = value
        } catch {
            self.error = .server(message: error.localizedDescription)
        }
    }

    private func centerOnUser() {
        guard let coordinate = container.location.coordinate else { return }
        position = .region(
            MKCoordinateRegion(
                center: coordinate,
                span: MKCoordinateSpan(latitudeDelta: 0.025, longitudeDelta: 0.025)
            )
        )
    }
}
