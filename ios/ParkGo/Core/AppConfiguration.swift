import Foundation

struct AppConfiguration: Sendable {
    let apiBaseURL: URL
    let presentationMode: Bool
    let offlineDemo: Bool
    let testMode: Bool

    static var current: AppConfiguration {
        let arguments = ProcessInfo.processInfo.arguments
        #if DEBUG
        let defaultURL = URL(string: "http://localhost:8000/api/v1")!
        return AppConfiguration(
            apiBaseURL: defaultURL,
            presentationMode: !arguments.contains("--standard-mode"),
            offlineDemo: arguments.contains("--offline-demo"),
            testMode: true
        )
        #else
        return AppConfiguration(
            apiBaseURL: URL(string: "https://api.parkgo.example/api/v1")!,
            presentationMode: false,
            offlineDemo: false,
            testMode: false
        )
        #endif
    }
}
