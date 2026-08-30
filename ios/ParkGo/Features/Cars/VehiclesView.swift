import SwiftUI

struct VehiclesView: View {
    @Environment(AppContainer.self) private var container
    @State private var vehicles: [Vehicle] = []
    @State private var showAdd = false
    @State private var error: ParkGoError?

    var body: some View {
        List {
            ForEach(vehicles) { vehicle in
                HStack {
                    VehicleLabel(vehicle: vehicle)
                    if vehicle.isDefault {
                        Text("По умолчанию")
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(.blue)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 5)
                            .background(.blue.opacity(0.1), in: Capsule())
                    }
                }
            }
            Button { showAdd = true } label: {
                Label("Добавить автомобиль", systemImage: "plus.circle.fill")
            }
        }
        .navigationTitle("Мои автомобили")
        .task { await load() }
        .refreshable { await load() }
        .sheet(isPresented: $showAdd) { AddVehicleView { await load() } }
        .overlay(alignment: .bottom) {
            if let error { ErrorNotice(error: error) { Task { await load() } }.padding() }
        }
    }

    private func load() async {
        do {
            vehicles = try await container.repository.vehicles()
            error = nil
        } catch let value as ParkGoError {
            error = value
        } catch {
            self.error = .server(message: error.localizedDescription)
        }
    }
}

private struct AddVehicleView: View {
    @Environment(AppContainer.self) private var container
    @Environment(\.dismiss) private var dismiss
    let didSave: () async -> Void
    @State private var plate = ""
    @State private var region = "23"
    @State private var name = ""
    @State private var saving = false
    @State private var error: ParkGoError?

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("Госномер", text: $plate).textInputAutocapitalization(.characters)
                    TextField("Регион", text: $region).keyboardType(.numberPad)
                    TextField("Название, например Toyota RAV4", text: $name)
                }
                if let error { Section { ErrorNotice(error: error, retry: nil) } }
            }
            .navigationTitle("Новый автомобиль")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Отмена") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Добавить") { Task { await save() } }
                        .disabled(plate.count < 2 || name.isEmpty || saving)
                }
            }
        }
        .presentationDetents([.medium])
    }

    private func save() async {
        saving = true
        defer { saving = false }
        do {
            _ = try await container.repository.addVehicle(plate: plate, region: region, name: name)
            await didSave()
            dismiss()
        } catch let value as ParkGoError {
            error = value
        } catch {
            self.error = .server(message: error.localizedDescription)
        }
    }
}
