import LocalAuthentication

struct BiometricService: Sendable {
    func confirmParking() async throws {
        let context = LAContext()
        var error: NSError?
        guard context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error) else { return }
        let approved = try await context.evaluatePolicy(
            .deviceOwnerAuthentication,
            localizedReason: "Подтвердите запуск тестовой парковки"
        )
        if !approved { throw ParkGoError.server(message: "Подтверждение отменено.") }
    }
}
