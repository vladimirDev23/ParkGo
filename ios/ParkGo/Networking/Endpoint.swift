import Foundation

enum HTTPMethod: String, Sendable {
    case get = "GET"
    case post = "POST"
    case patch = "PATCH"
    case delete = "DELETE"
}

struct Endpoint<Response: Decodable & Sendable>: Sendable {
    let path: String
    var method: HTTPMethod = .get
    var query: [URLQueryItem] = []
    var body: Data?
    var authenticated = true

    init(
        path: String,
        method: HTTPMethod = .get,
        query: [URLQueryItem] = [],
        body: Data? = nil,
        authenticated: Bool = true
    ) {
        self.path = path
        self.method = method
        self.query = query
        self.body = body
        self.authenticated = authenticated
    }

    static func json<Body: Encodable & Sendable>(
        path: String,
        method: HTTPMethod,
        body: Body,
        authenticated: Bool = true
    ) throws -> Endpoint<Response> {
        Endpoint(
            path: path,
            method: method,
            body: try JSONEncoder.parkGo.encode(body),
            authenticated: authenticated
        )
    }
}

extension JSONDecoder {
    static var parkGo: JSONDecoder {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }
}

extension JSONEncoder {
    static var parkGo: JSONEncoder {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }
}
