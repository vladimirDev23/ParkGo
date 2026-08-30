import Foundation

enum ParkGoError: LocalizedError, Equatable, Sendable {
    case noInternet
    case locationDenied
    case locationUnavailable
    case noParkingNearby
    case authenticationRequired
    case providerUnavailable
    case sessionAlreadyActive
    case paymentFailed
    case timeout
    case server(message: String)

    var errorDescription: String? {
        switch self {
        case .noInternet:
            "Нет соединения с интернетом. Проверьте сеть и попробуйте ещё раз."
        case .locationDenied:
            "Разрешите доступ к геопозиции в настройках, чтобы находить парковки рядом."
        case .locationUnavailable:
            "Не удалось определить геопозицию. Выберите парковку на карте."
        case .noParkingNearby:
            "Рядом не найдена платная парковка."
        case .authenticationRequired:
            "Сессия истекла. Войдите снова."
        case .providerUnavailable:
            "Не удалось связаться с парковочной системой. Проверьте интернет и попробуйте ещё раз."
        case .sessionAlreadyActive:
            "У вас уже есть активная парковка."
        case .paymentFailed:
            "Не удалось выполнить тестовую оплату. Сессия завершена; проверьте историю."
        case .timeout:
            "Сервис отвечает слишком долго. Попробуйте ещё раз."
        case let .server(message):
            message
        }
    }
}
