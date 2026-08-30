import SwiftUI

@main
struct ParkGoApp: App {
    @Environment(\.scenePhase) private var scenePhase
    @State private var container = AppContainer()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(container)
                .tint(.blue)
        }
        .onChange(of: scenePhase) { _, phase in
            if phase == .active {
                Task { await container.sessionStore.synchronize() }
            }
        }
    }
}
