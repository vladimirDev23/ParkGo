import SwiftUI

struct AuthView: View {
    @Environment(AppContainer.self) private var container
    @State private var email = ""
    @State private var password = ""
    @State private var firstName = ""
    @State private var registering = false
    @State private var loading = false
    @State private var error: ParkGoError?

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("Email", text: $email)
                        .textInputAutocapitalization(.never)
                        .keyboardType(.emailAddress)
                        .textContentType(.emailAddress)
                    SecureField("Пароль", text: $password)
                        .textContentType(registering ? .newPassword : .password)
                    if registering {
                        TextField("Имя (необязательно)", text: $firstName)
                            .textContentType(.givenName)
                    }
                }
                if let error {
                    Section { ErrorNotice(error: error, retry: nil) }
                        .listRowBackground(Color.clear)
                }
                Section {
                    PrimaryActionButton(
                        title: registering ? "Создать аккаунт" : "Войти",
                        loading: loading,
                        disabled: email.isEmpty || password.isEmpty
                    ) { Task { await submit() } }
                    .listRowInsets(EdgeInsets())
                    .listRowBackground(Color.clear)
                    Button(registering ? "У меня уже есть аккаунт" : "Создать аккаунт") {
                        withAnimation { registering.toggle() }
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .navigationTitle("ParkGo")
            .safeAreaInset(edge: .top) {
                TestModeBanner(visible: container.configuration.testMode)
            }
        }
    }

    private func submit() async {
        loading = true
        defer { loading = false }
        do {
            if registering {
                try await container.register(
                    email: email,
                    password: password,
                    firstName: firstName.isEmpty ? nil : firstName
                )
            } else {
                try await container.signIn(email: email, password: password)
            }
            error = nil
        } catch let value as ParkGoError {
            error = value
        } catch {
            self.error = .server(message: error.localizedDescription)
        }
    }
}
