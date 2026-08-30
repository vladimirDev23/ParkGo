import Foundation

public enum ParkGoFormatting {
    static let currency: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.numberStyle = .currency
        formatter.currencyCode = "RUB"
        formatter.currencySymbol = "₽"
        formatter.maximumFractionDigits = 0
        return formatter
    }()

    public static func amount(_ value: Decimal) -> String {
        let value = currency.string(from: value as NSDecimalNumber) ?? "0 ₽"
        return value.replacingOccurrences(of: "\u{00a0}", with: " ")
    }

    public static func duration(_ interval: TimeInterval, compact: Bool = false) -> String {
        let total = max(0, Int(interval))
        let hours = total / 3_600
        let minutes = (total % 3_600) / 60
        let seconds = total % 60
        if compact { return String(format: "%02d:%02d:%02d", hours, minutes, seconds) }
        if hours > 0 { return "\(hours) ч \(minutes) мин" }
        return "\(max(1, minutes)) мин"
    }

    public static func distance(_ meters: Int?) -> String {
        guard let meters else { return "—" }
        return meters < 1_000 ? "\(meters) м" : String(format: "%.1f км", Double(meters) / 1_000)
    }
}
