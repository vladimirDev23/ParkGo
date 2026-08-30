import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            Tab("Главная", systemImage: "house.fill") { HomeView() }
            Tab("Карта", systemImage: "map.fill") { ParkingMapView() }
            Tab("История", systemImage: "clock.arrow.circlepath") { HistoryView() }
            Tab("Профиль", systemImage: "person.fill") { ProfileView() }
        }
    }
}
