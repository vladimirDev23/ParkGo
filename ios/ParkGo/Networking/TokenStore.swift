import Foundation
import Security

actor TokenStore {
    private let service = "com.parkgo.tokens"

    func save(access: String, refresh: String) throws {
        try write(access, account: "access")
        try write(refresh, account: "refresh")
    }

    func accessToken() -> String? { read(account: "access") }
    func refreshToken() -> String? { read(account: "refresh") }

    func clear() {
        delete(account: "access")
        delete(account: "refresh")
    }

    private func write(_ value: String, account: String) throws {
        delete(account: account)
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: account,
            kSecAttrAccessible: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly,
            kSecValueData: Data(value.utf8)
        ]
        guard SecItemAdd(query as CFDictionary, nil) == errSecSuccess else {
            throw ParkGoError.server(message: "Не удалось безопасно сохранить сессию.")
        }
    }

    private func read(account: String) -> String? {
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: account,
            kSecReturnData: true,
            kSecMatchLimit: kSecMatchLimitOne
        ]
        var result: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data
        else { return nil }
        return String(decoding: data, as: UTF8.self)
    }

    private func delete(account: String) {
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: account
        ]
        SecItemDelete(query as CFDictionary)
    }
}
