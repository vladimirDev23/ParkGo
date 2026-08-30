import SwiftUI

struct TestModeBanner: View {
    let visible: Bool

    var body: some View {
        if visible {
            Text("TEST MODE · ОПЛАТА НЕ ПРОИЗВОДИТСЯ")
                .font(.caption2.weight(.bold))
                .tracking(0.7)
                .foregroundStyle(.orange)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 6)
                .background(.orange.opacity(0.12))
                .accessibilityIdentifier("testModeBanner")
        }
    }
}

struct PrimaryActionButton: View {
    let title: String
    var systemImage: String? = nil
    var loading = false
    var disabled = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 10) {
                if loading { ProgressView().tint(.white) }
                if let systemImage { Image(systemName: systemImage) }
                Text(title).fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 54)
        }
        .buttonStyle(.borderedProminent)
        .buttonBorderShape(.roundedRectangle(radius: 14))
        .disabled(disabled || loading)
    }
}

struct ErrorNotice: View {
    let error: ParkGoError
    let retry: (() -> Void)?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(error.localizedDescription, systemImage: "exclamationmark.triangle.fill")
                .font(.subheadline)
                .foregroundStyle(.primary)
            if let retry {
                Button("Повторить", action: retry)
                    .font(.subheadline.weight(.semibold))
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.orange.opacity(0.12), in: RoundedRectangle(cornerRadius: 14))
    }
}

struct VehicleLabel: View {
    let vehicle: Vehicle

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "car.fill")
                .foregroundStyle(.tint)
                .frame(width: 36, height: 36)
                .background(.tint.opacity(0.12), in: Circle())
            VStack(alignment: .leading, spacing: 2) {
                Text(vehicle.displayName).font(.subheadline.weight(.semibold))
                Text(vehicle.formattedPlate).font(.caption.monospaced()).foregroundStyle(.secondary)
            }
            Spacer()
        }
    }
}
