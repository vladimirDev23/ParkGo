import SwiftUI

struct RootView: View {
    @Environment(AppContainer.self) private var container
    @AppStorage("hasCompletedOnboarding") private var completedOnboarding = false

    var body: some View {
        Group {
            switch container.authentication {
            case .loading:
                VStack(spacing: 16) {
                    Image(systemName: "parkingsign.circle.fill")
                        .font(.system(size: 64))
                        .foregroundStyle(.tint)
                    ProgressView()
                }
            case .signedOut:
                AuthView()
            case .signedIn:
                if completedOnboarding || container.configuration.presentationMode {
                    MainTabView()
                } else {
                    OnboardingView(completed: $completedOnboarding)
                }
            }
        }
        .task { await container.bootstrap() }
    }
}
