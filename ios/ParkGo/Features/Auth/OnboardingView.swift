import SwiftUI

struct OnboardingView: View {
    @Environment(AppContainer.self) private var container
    @Binding var completed: Bool
    @State private var page = 0
    @State private var plate = ""
    @State private var region = "23"
    @State private var vehicleName = "Toyota RAV4"
    @State private var saving = false
    @State private var error: ParkGoError?

    var body: some View {
        VStack {
            TabView(selection: $page) {
                welcome.tag(0)
                location.tag(1)
                vehicle.tag(2)
            }
            .tabViewStyle(.page(indexDisplayMode: .never))
        }
        .background(Color(uiColor: .systemGroupedBackground))
    }

    private var welcome: some View {
        VStack(spacing: 24) {
            Spacer()
            Image(systemName: "parkingsign.circle.fill")
                .font(.system(size: 86))
                .foregroundStyle(.tint)
            VStack(spacing: 8) {
                Text("ParkGo").font(.largeTitle.bold())
                Text("Парковка без лишних действий")
                    .font(.title3)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            PrimaryActionButton(title: "Продолжить") { withAnimation { page = 1 } }
                .padding()
        }
    }

    private var location: some View {
        VStack(spacing: 24) {
            Spacer()
            Image(systemName: "location.circle.fill")
                .font(.system(size: 82))
                .foregroundStyle(.tint)
            Text("Парковка рядом").font(.title.bold())
            Text("ParkGo использует геопозицию, чтобы автоматически определять ближайшую парковочную зону.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 28)
            Spacer()
            PrimaryActionButton(title: "Разрешить геопозицию") {
                container.location.requestPermissionAndLocation()
                withAnimation { page = 2 }
            }
            .padding()
        }
    }

    private var vehicle: some View {
        NavigationStack {
            Form {
                Section("Добавить автомобиль") {
                    TextField("Госномер", text: $plate)
                        .textInputAutocapitalization(.characters)
                    TextField("Регион", text: $region).keyboardType(.numberPad)
                    TextField("Название автомобиля", text: $vehicleName)
                }
                if let error {
                    Section { ErrorNotice(error: error, retry: nil) }
                }
                Section {
                    PrimaryActionButton(
                        title: "Добавить автомобиль",
                        loading: saving,
                        disabled: plate.trimmingCharacters(in: .whitespaces).count < 2
                    ) { Task { await saveVehicle() } }
                    .listRowInsets(EdgeInsets())
                    .listRowBackground(Color.clear)
                }
            }
            .navigationTitle("Ваш автомобиль")
        }
    }

    private func saveVehicle() async {
        saving = true
        defer { saving = false }
        do {
            _ = try await container.repository.addVehicle(
                plate: plate,
                region: region,
                name: vehicleName
            )
            completed = true
        } catch let value as ParkGoError {
            error = value
        } catch {
            self.error = .server(message: error.localizedDescription)
        }
    }
}
