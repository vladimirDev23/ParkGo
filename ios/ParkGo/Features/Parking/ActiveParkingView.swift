import SwiftUI
import UIKit

struct ActiveParkingView: View {
    @Environment(AppContainer.self) private var container
    let session: ParkingSession
    @Binding var showStopSheet: Bool

    var body: some View {
        ScrollView {
            VStack(spacing: 26) {
                VStack(spacing: 8) {
                    Label("Парковка активна", systemImage: "parkingsign.circle.fill")
                        .font(.headline)
                        .foregroundStyle(.green)
                    Text(ParkGoFormatting.duration(container.sessionStore.elapsed, compact: true))
                        .font(.system(size: 48, weight: .semibold, design: .rounded))
                        .monospacedDigit()
                        .contentTransition(.numericText())
                    Text(ParkGoFormatting.amount(container.sessionStore.estimatedAmount))
                        .font(.title.bold())
                        .contentTransition(.numericText())
                    Text("примерная стоимость")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 28)

                VStack(spacing: 0) {
                    detailRow("Парковка", value: "№\(session.parkingZone.zoneNumber)")
                    Divider()
                    detailRow("Адрес", value: session.parkingZone.address)
                    Divider()
                    detailRow("Автомобиль", value: session.vehicle.displayName)
                    Divider()
                    detailRow("Госномер", value: session.vehicle.formattedPlate)
                    Divider()
                    detailRow("Начало", value: session.startedAt.formatted(date: .omitted, time: .shortened))
                }
                .padding(.horizontal)
                .background(.background, in: RoundedRectangle(cornerRadius: 18))
            }
            .padding()
        }
        .background(Color(uiColor: .systemGroupedBackground))
        .safeAreaInset(edge: .bottom) {
            PrimaryActionButton(
                title: "ЗАВЕРШИТЬ ПАРКОВКУ",
                systemImage: "stop.fill",
                loading: container.sessionStore.operation == .stopping
            ) { showStopSheet = true }
            .tint(.red)
            .padding()
            .background(.ultraThinMaterial)
            .accessibilityIdentifier("stopParkingButton")
        }
        .confirmationDialog(
            "Завершить парковку?",
            isPresented: $showStopSheet,
            titleVisibility: .visible
        ) {
            Button("Завершить · \(ParkGoFormatting.amount(container.sessionStore.estimatedAmount))", role: .destructive) {
                Task { await stop() }
            }
            Button("Отмена", role: .cancel) {}
        } message: {
            Text("Продолжительность: \(ParkGoFormatting.duration(container.sessionStore.elapsed))")
        }
    }

    private func detailRow(_ title: String, value: String) -> some View {
        HStack(alignment: .firstTextBaseline) {
            Text(title).foregroundStyle(.secondary)
            Spacer()
            Text(value).fontWeight(.medium).multilineTextAlignment(.trailing)
        }
        .padding(.vertical, 14)
    }

    private func stop() async {
        do {
            _ = try await container.sessionStore.stop()
            UINotificationFeedbackGenerator().notificationOccurred(.success)
        } catch {
            UINotificationFeedbackGenerator().notificationOccurred(.error)
        }
    }
}
