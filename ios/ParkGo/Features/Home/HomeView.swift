import SwiftUI
import UIKit

struct HomeView: View {
    @Environment(AppContainer.self) private var container
    @State private var model: HomeViewModel?
    @State private var showZones = false
    @State private var showStopSheet = false

    var body: some View {
        NavigationStack {
            Group {
                if let active = container.sessionStore.activeSession {
                    ActiveParkingView(session: active, showStopSheet: $showStopSheet)
                } else if let model {
                    idleContent(model)
                } else {
                    ProgressView("Готовим ParkGo…")
                }
            }
            .navigationTitle("Главная")
            .navigationBarTitleDisplayMode(.large)
            .safeAreaInset(edge: .top) {
                TestModeBanner(visible: container.configuration.testMode)
            }
            .task {
                if model == nil { model = HomeViewModel(repository: container.repository) }
                container.location.requestPermissionAndLocation()
                await refresh()
            }
            .task(id: container.location.state) { await refresh() }
            .refreshable { await refresh() }
            .sheet(isPresented: $showZones) {
                ZonePickerView(
                    zones: model?.zones ?? [],
                    selected: Binding(
                        get: { model?.selectedZone },
                        set: { model?.selectedZone = $0 }
                    )
                )
            }
            .alert(
                "Тестовая оплата прошла",
                isPresented: Binding(
                    get: { container.sessionStore.completionMessage != nil },
                    set: { if !$0 { container.sessionStore.completionMessage = nil } }
                )
            ) {
                Button("Готово", role: .cancel) {
                    container.sessionStore.completionMessage = nil
                }
            } message: {
                Text(container.sessionStore.completionMessage ?? "")
            }
        }
    }

    @ViewBuilder
    private func idleContent(_ model: HomeViewModel) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                Text(greeting).font(.title2.weight(.semibold))
                if let vehicle = model.selectedVehicle {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Текущий автомобиль").font(.caption).foregroundStyle(.secondary)
                        VehicleLabel(vehicle: vehicle)
                    }
                    .padding()
                    .background(.background, in: RoundedRectangle(cornerRadius: 18))
                } else {
                    ContentUnavailableView(
                        "Добавьте автомобиль",
                        systemImage: "car",
                        description: Text("Автомобиль нужен для запуска парковки.")
                    )
                }

                if model.loading && model.selectedZone == nil {
                    VStack(alignment: .leading, spacing: 14) {
                        RoundedRectangle(cornerRadius: 8).fill(.quaternary).frame(height: 18)
                        RoundedRectangle(cornerRadius: 8).fill(.quaternary).frame(height: 64)
                    }
                    .redacted(reason: .placeholder)
                } else if let zone = model.selectedZone {
                    zoneCard(zone)
                } else {
                    ContentUnavailableView(
                        "Парковка не найдена",
                        systemImage: "parkingsign",
                        description: Text("Откройте карту и выберите зону вручную.")
                    )
                }

                if let error = model.error {
                    ErrorNotice(error: error) { Task { await refresh() } }
                }
            }
            .padding()
        }
        .background(Color(uiColor: .systemGroupedBackground))
        .safeAreaInset(edge: .bottom) {
            VStack(spacing: 10) {
                PrimaryActionButton(
                    title: "НАЧАТЬ ПАРКОВКУ",
                    systemImage: "play.fill",
                    loading: container.sessionStore.operation == .starting,
                    disabled: model.selectedVehicle == nil
                        || model.selectedZone == nil
                        || !container.configuration.testMode
                ) { Task { await start(model) } }
                .accessibilityIdentifier("startParkingButton")
                Button("Другая парковка") { showZones = true }
                    .disabled(model.zones.isEmpty)
            }
            .padding()
            .background(.ultraThinMaterial)
        }
    }

    private func zoneCard(_ zone: ParkingZone) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Ближайшая парковка").font(.caption).foregroundStyle(.secondary)
                    Text("Парковка №\(zone.zoneNumber)").font(.title3.bold())
                }
                Spacer()
                Text(ParkGoFormatting.distance(zone.distanceMeters))
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(.secondary)
            }
            Text(zone.address).foregroundStyle(.secondary)
            Divider()
            HStack {
                Text(ParkGoFormatting.amount(zone.hourlyRate))
                    .font(.title2.bold())
                Text("/ час").foregroundStyle(.secondary)
                Spacer()
                if let from = zone.activeFrom, let until = zone.activeUntil {
                    Label("\(from)–\(until)", systemImage: "clock")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding()
        .background(.background, in: RoundedRectangle(cornerRadius: 18))
    }

    private var greeting: String {
        let hour = Calendar.current.component(.hour, from: .now)
        return hour < 12 ? "Доброе утро" : hour < 18 ? "Добрый день" : "Добрый вечер"
    }

    private func refresh() async {
        guard let coordinate = container.location.coordinate, let model else { return }
        await model.load(latitude: coordinate.latitude, longitude: coordinate.longitude)
    }

    private func start(_ model: HomeViewModel) async {
        guard let vehicle = model.selectedVehicle, let zone = model.selectedZone else { return }
        do {
            try await container.biometricService.confirmParking()
            try await container.sessionStore.start(vehicle: vehicle, zone: zone)
            UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        } catch {
            UINotificationFeedbackGenerator().notificationOccurred(.error)
        }
    }
}

private struct ZonePickerView: View {
    @Environment(\.dismiss) private var dismiss
    let zones: [ParkingZone]
    @Binding var selected: ParkingZone?

    var body: some View {
        NavigationStack {
            List(zones) { zone in
                Button {
                    selected = zone
                    dismiss()
                } label: {
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Парковка №\(zone.zoneNumber)").fontWeight(.semibold)
                            Text(zone.address).font(.caption).foregroundStyle(.secondary)
                        }
                        Spacer()
                        Text(ParkGoFormatting.amount(zone.hourlyRate))
                    }
                }
                .foregroundStyle(.primary)
            }
            .navigationTitle("Выберите парковку")
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button("Закрыть") { dismiss() } } }
        }
        .presentationDetents([.medium, .large])
    }
}
