import ActivityKit
import SwiftUI
import WidgetKit

struct ParkGoLiveActivityWidget: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: ParkingActivityAttributes.self) { context in
            HStack(spacing: 14) {
                Image(systemName: "parkingsign.circle.fill")
                    .font(.title)
                    .foregroundStyle(.blue)
                VStack(alignment: .leading, spacing: 3) {
                    Text("Парковка №\(context.attributes.zoneNumber)")
                        .font(.headline)
                    Text(timerInterval: context.state.startedAt...Date.distantFuture, countsDown: false)
                        .font(.title2.monospacedDigit().weight(.semibold))
                    Text(context.attributes.vehicleName)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                Text(context.state.estimatedAmount, format: .currency(code: "RUB").precision(.fractionLength(0)))
                    .font(.headline)
                Link(destination: URL(string: "parkgo://session/\(context.attributes.sessionID)")!) {
                    Image(systemName: "arrow.up.right.circle.fill")
                }
                .accessibilityLabel("Открыть ParkGo")
            }
            .padding()
            .activityBackgroundTint(Color(uiColor: .systemBackground))
            .activitySystemActionForegroundColor(.blue)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Label("№\(context.attributes.zoneNumber)", systemImage: "parkingsign")
                        .font(.headline)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text(context.state.estimatedAmount, format: .currency(code: "RUB").precision(.fractionLength(0)))
                        .font(.headline)
                }
                DynamicIslandExpandedRegion(.bottom) {
                    HStack {
                        Text(timerInterval: context.state.startedAt...Date.distantFuture, countsDown: false)
                            .monospacedDigit()
                        Spacer()
                        Text(context.attributes.vehicleName).foregroundStyle(.secondary)
                    }
                }
            } compactLeading: {
                Image(systemName: "parkingsign")
            } compactTrailing: {
                Text(timerInterval: context.state.startedAt...Date.distantFuture, countsDown: false)
                    .monospacedDigit()
                    .frame(width: 42)
            } minimal: {
                Image(systemName: "parkingsign")
            }
            .widgetURL(URL(string: "parkgo://session/\(context.attributes.sessionID)"))
            .keylineTint(.blue)
        }
    }
}

@main
struct ParkGoWidgets: WidgetBundle {
    var body: some Widget { ParkGoLiveActivityWidget() }
}
