import SwiftUI

struct ProfileView: View {
    @Environment(AppContainer.self) private var container
    @State private var stats: ParkingStats?
    @AppStorage("notifyOneHour") private var notifyOneHour = true
    @AppStorage("notifyZoneExit") private var notifyZoneExit = true

    var body: some View {
        NavigationStack {
            List {
                Section {
                    HStack(spacing: 14) {
                        Image(systemName: "person.crop.circle.fill")
                            .font(.system(size: 48))
                            .foregroundStyle(.tint)
                        VStack(alignment: .leading) {
                            Text(userName).font(.headline)
                            Text("ParkGo").font(.caption).foregroundStyle(.secondary)
                        }
                    }
                }
                if let stats {
                    Section("Статистика · \(stats.period)") {
                        LabeledContent("Парковок", value: String(stats.parkingCount))
                        LabeledContent("Время", value: ParkGoFormatting.duration(TimeInterval(stats.totalDurationSeconds)))
                        LabeledContent("Потрачено", value: ParkGoFormatting.amount(stats.totalSpent))
                        LabeledContent("Средняя парковка", value: ParkGoFormatting.amount(stats.averageAmount))
                        if let most = stats.mostUsedZoneNumber {
                            LabeledContent("Чаще всего", value: "№\(most)")
                        }
                    }
                }
                Section {
                    NavigationLink { VehiclesView() } label: {
                        Label("Мои автомобили", systemImage: "car.2.fill")
                    }
                }
                Section("Уведомления") {
                    Toggle("Парковка активна 1 час", isOn: $notifyOneHour)
                    Toggle("Покидание парковки", isOn: $notifyZoneExit)
                }
                Section {
                    Button("Выйти", role: .destructive) { Task { await container.signOut() } }
                }
                if container.configuration.testMode {
                    Section("Режим") {
                        LabeledContent("Provider", value: "Mock")
                        LabeledContent("Оплата", value: "Тестовая")
                    }
                }
            }
            .navigationTitle("Профиль")
            .safeAreaInset(edge: .top) {
                TestModeBanner(visible: container.configuration.testMode)
            }
            .task { stats = try? await container.repository.stats() }
            .refreshable { stats = try? await container.repository.stats() }
        }
    }

    private var userName: String {
        guard case let .signedIn(user) = container.authentication else { return "Пользователь" }
        return user.firstName ?? (user.email.isEmpty ? "Пользователь" : user.email)
    }
}
