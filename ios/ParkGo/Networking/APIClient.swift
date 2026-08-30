import Foundation

actor APIClient {
    private let baseURL: URL
    private let session: URLSession
    private let tokenStore: TokenStore
    private var refreshTask: Task<Void, Error>?

    init(baseURL: URL, tokenStore: TokenStore, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.tokenStore = tokenStore
        self.session = session
    }

    func send<Response>(_ endpoint: Endpoint<Response>, retryAfterRefresh: Bool = true) async throws -> Response {
        let request = try await makeRequest(endpoint)
        do {
            let (data, response) = try await session.data(for: request)
            guard let http = response as? HTTPURLResponse else {
                throw ParkGoError.server(message: "Некорректный ответ сервера.")
            }
            if http.statusCode == 401, endpoint.authenticated, retryAfterRefresh {
                try await refreshTokens()
                return try await send(endpoint, retryAfterRefresh: false)
            }
            guard (200..<300).contains(http.statusCode) else {
                throw mapError(data: data, status: http.statusCode)
            }
            return try JSONDecoder.parkGo.decode(Response.self, from: data)
        } catch let error as URLError {
            switch error.code {
            case .notConnectedToInternet, .networkConnectionLost:
                throw ParkGoError.noInternet
            case .timedOut:
                throw ParkGoError.timeout
            default:
                throw ParkGoError.server(message: "Ошибка сети. Попробуйте ещё раз.")
            }
        }
    }

    func store(_ pair: TokenPairDTO) async throws {
        try await tokenStore.save(access: pair.accessToken, refresh: pair.refreshToken)
    }

    func logout() async {
        await tokenStore.clear()
    }

    private func makeRequest<Response>(_ endpoint: Endpoint<Response>) async throws -> URLRequest {
        var components = URLComponents(
            url: baseURL.appendingPathComponent(endpoint.path),
            resolvingAgainstBaseURL: false
        )
        components?.queryItems = endpoint.query.isEmpty ? nil : endpoint.query
        guard let url = components?.url else {
            throw ParkGoError.server(message: "Некорректный адрес API.")
        }
        var request = URLRequest(url: url, timeoutInterval: 12)
        request.httpMethod = endpoint.method.rawValue
        request.httpBody = endpoint.body
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if endpoint.body != nil {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        if endpoint.authenticated, let token = await tokenStore.accessToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        return request
    }

    private func refreshTokens() async throws {
        if let task = refreshTask { return try await task.value }
        let task = Task { [baseURL, session, tokenStore] in
            guard let refresh = await tokenStore.refreshToken() else {
                throw ParkGoError.authenticationRequired
            }
            let endpoint = try Endpoint<TokenPairDTO>.json(
                path: "auth/refresh",
                method: .post,
                body: ["refresh_token": refresh],
                authenticated: false
            )
            var request = URLRequest(
                url: baseURL.appendingPathComponent(endpoint.path),
                timeoutInterval: 12
            )
            request.httpMethod = endpoint.method.rawValue
            request.httpBody = endpoint.body
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            let (data, response) = try await session.data(for: request)
            guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
                await tokenStore.clear()
                throw ParkGoError.authenticationRequired
            }
            let pair = try JSONDecoder.parkGo.decode(TokenPairDTO.self, from: data)
            try await tokenStore.save(access: pair.accessToken, refresh: pair.refreshToken)
        }
        refreshTask = task
        defer { refreshTask = nil }
        try await task.value
    }

    private func mapError(data: Data, status: Int) -> ParkGoError {
        let envelope = try? JSONDecoder.parkGo.decode(ErrorEnvelopeDTO.self, from: data)
        switch envelope?.error.code {
        case "PROVIDER_UNAVAILABLE": .providerUnavailable
        case "SESSION_ALREADY_ACTIVE": .sessionAlreadyActive
        case "PAYMENT_FAILED": .paymentFailed
        case "TOKEN_EXPIRED", "AUTHENTICATION_REQUIRED": .authenticationRequired
        default:
            envelope.map { .server(message: $0.error.message) }
                ?? .server(message: "Сервис временно недоступен (\(status)).")
        }
    }
}
