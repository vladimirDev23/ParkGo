import MapKit
import SwiftUI

struct HistoryView: View {
    @Environment(AppContainer.self) private var container
    @State private var sessions: [ParkingSession] = []
    @State private var loading = true
    @State private var error: ParkGoError?

    var body: some View {
        NavigationStack {
            Group {
                if loading && sessions.isEmpty {
                    ProgressView("Загружаем историю…")
                } else if sessions.isEmpty {
                    ContentUnavailableView(
                        "История пуста",
                        systemImage: "clock.arrow.circlepath",
                        description: Text("Завершённые парковки появятся здесь.")
                    )
                } else {
                    List(sessions) { session in
                        NavigationLink {
                            ParkingHistoryDetail(session: session)
                        } label: {
                            HistoryRow(session: session)
                        }
                    }
                    .listStyle(.insetGrouped)
                }
            }
            .navigationTitle("История")
            .safeAreaInset(edge: .top) {
                TestModeBanner(visible: container.configuration.testMode)
            }
            .overlay(alignment: .bottom) {
                if let error { ErrorNotice(error: error) { Task { await load() } }.padding() }
            }
            .task { await load() }
            .refreshable { await load() }
        }
    }

    private func load() async {
        loading = true
        defer { loading = false }
        do {
            sessions = try await container.repository.history()
            error = nil
        } catch let value as ParkGoError {
            error = value
        } catch {
            self.error = .server(message: error.localizedDescription)
        }
    }
}

private struct HistoryRow: View {
    let session: ParkingSession

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: "parkingsign.circle.fill")
                .font(.title2)
                .foregroundStyle(.tint)
            VStack(alignment: .leading, spacing: 4) {
                Text("Парковка №\(session.parkingZone.zoneNumber)").fontWeight(.semibold)
                Text(timeRange).font(.caption).foregroundStyle(.secondary)
                Text(ParkGoFormatting.duration(session.duration())).font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            Text(ParkGoFormatting.amount(session.paidAmount)).fontWeight(.semibold)
        }
        .padding(.vertical, 5)
        .accessibilityIdentifier("historySessionRow")
    }

    private var timeRange: String {
        let start = session.startedAt.formatted(date: .abbreviated, time: .shortened)
        let end = session.finishedAt?.formatted(date: .omitted, time: .shortened) ?? "—"
        return "\(start)–\(end)"
    }
}

private struct ParkingHistoryDetail: View {
    let session: ParkingSession
    @State private var position: MapCameraPosition

    init(session: ParkingSession) {
        self.session = session
        _position = State(
            initialValue: .region(
                MKCoordinateRegion(
                    center: session.parkingZone.coordinate,
                    span: MKCoordinateSpan(latitudeDelta: 0.008, longitudeDelta: 0.008)
                )
            )
        )
    }

    var body: some View {
        List {
            Map(position: $position, interactionModes: []) {
                Marker("№\(session.parkingZone.zoneNumber)", coordinate: session.parkingZone.coordinate)
            }
            .frame(height: 180)
            .clipShape(RoundedRectangle(cornerRadius: 14))
            .listRowInsets(EdgeInsets())
            Section("Парковка") {
                LabeledContent("Зона", value: "№\(session.parkingZone.zoneNumber)")
                LabeledContent("Адрес", value: session.parkingZone.address)
                LabeledContent("Автомобиль", value: session.vehicle.displayName)
                LabeledContent("Госномер", value: session.vehicle.formattedPlate)
            }
            Section("Сессия") {
                LabeledContent("Начало", value: session.startedAt.formatted())
                if let finishedAt = session.finishedAt {
                    LabeledContent("Завершение", value: finishedAt.formatted())
                }
                LabeledContent("Продолжительность", value: ParkGoFormatting.duration(session.duration()))
                LabeledContent("Стоимость", value: ParkGoFormatting.amount(session.paidAmount))
                LabeledContent("Оплата", value: session.paymentStatus == .paid ? "Тестовая · успешно" : "Не оплачено")
            }
        }
        .navigationTitle("Парковка №\(session.parkingZone.zoneNumber)")
        .navigationBarTitleDisplayMode(.inline)
    }
}
