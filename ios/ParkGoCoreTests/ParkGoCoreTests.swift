import Foundation
import ParkGoCore

private func expect(_ condition: @autoclosure () -> Bool, _ message: String) {
    guard condition() else { fatalError(message) }
}

@main
enum ParkGoCoreChecks {
    static func main() {
        expect(ParkGoFormatting.amount(Decimal(84)) == "84 ₽", "Price formatting failed")
        expect(ParkGoFormatting.duration(5_077) == "1 ч 24 мин", "Duration formatting failed")
        expect(
            ParkGoFormatting.duration(5_077, compact: true) == "01:24:37",
            "Compact duration formatting failed"
        )

        let id = UUID()
        let started = Date(timeIntervalSince1970: 1_000)
        let active = PortableSessionReducer.reduce(
            state: .idle,
            event: .synchronized(id: id, startedAt: started)
        )
        expect(active == .active(id: id, startedAt: started), "Active reducer transition failed")
        let completed = PortableSessionReducer.reduce(
            state: active,
            event: .stopped(amount: 84)
        )
        expect(
            completed == .completed(id: id, amount: 84),
            "Completed reducer transition failed"
        )
        print("ParkGoCoreChecks: all checks passed")
    }
}
