import ActivityKit
import Foundation

@MainActor
final class LiveActivityService {
    private var activity: Activity<ParkingActivityAttributes>?

    func start(session: ParkingSession) async {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else { return }
        let attributes = ParkingActivityAttributes(
            sessionID: session.id,
            zoneNumber: session.parkingZone.zoneNumber,
            vehicleName: session.vehicle.displayName,
            plateNumber: session.vehicle.formattedPlate,
            hourlyRate: session.parkingZone.hourlyRate
        )
        let state = ParkingActivityAttributes.ContentState(
            startedAt: session.startedAt,
            estimatedAmount: session.calculatedAmount
        )
        do {
            activity = try Activity.request(
                attributes: attributes,
                content: ActivityContent(state: state, staleDate: nil),
                pushType: nil
            )
        } catch {
            // The main parking flow remains valid when system policy rejects an activity.
        }
    }

    func update(session: ParkingSession, estimatedAmount: Decimal) async {
        let matching = activity
            ?? Activity<ParkingActivityAttributes>.activities.first(where: {
                $0.attributes.sessionID == session.id
            })
        guard let matching else { return }
        let state = ParkingActivityAttributes.ContentState(
            startedAt: session.startedAt,
            estimatedAmount: estimatedAmount
        )
        await matching.update(ActivityContent(state: state, staleDate: nil))
    }

    func end(sessionID: UUID, finalAmount: Decimal) async {
        let values = Activity<ParkingActivityAttributes>.activities.filter {
            $0.attributes.sessionID == sessionID
        }
        for value in values {
            let state = ParkingActivityAttributes.ContentState(
                startedAt: value.content.state.startedAt,
                estimatedAmount: finalAmount
            )
            await value.end(
                ActivityContent(state: state, staleDate: nil),
                dismissalPolicy: .after(.now.addingTimeInterval(10))
            )
        }
        activity = nil
    }
}
