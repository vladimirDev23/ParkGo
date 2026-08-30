import UserNotifications

actor NotificationService {
    func requestAuthorization() async {
        _ = try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge])
    }

    func scheduleExitReminder(zoneNumber: String) async {
        let content = UNMutableNotificationContent()
        content.title = "Похоже, вы уехали"
        content.body = "Завершить парковку №\(zoneNumber)?"
        content.sound = .default
        content.userInfo = ["action": "stop-parking", "zone": zoneNumber]
        let request = UNNotificationRequest(identifier: "parking-exit", content: content, trigger: nil)
        try? await UNUserNotificationCenter.current().add(request)
    }

    func scheduleActiveReminders(session: ParkingSession) async {
        let center = UNUserNotificationCenter.current()
        center.removePendingNotificationRequests(withIdentifiers: ["parking-hour", "parking-forget"])
        let hour = UNMutableNotificationContent()
        hour.title = "Парковка активна уже 1 час"
        hour.body = "Проверьте парковку №\(session.parkingZone.zoneNumber)."
        hour.sound = .default
        try? await center.add(
            UNNotificationRequest(
                identifier: "parking-hour",
                content: hour,
                trigger: UNTimeIntervalNotificationTrigger(timeInterval: 3_600, repeats: false)
            )
        )
    }

    func clearParkingReminders() {
        UNUserNotificationCenter.current().removePendingNotificationRequests(
            withIdentifiers: ["parking-hour", "parking-forget", "parking-exit"]
        )
    }
}
