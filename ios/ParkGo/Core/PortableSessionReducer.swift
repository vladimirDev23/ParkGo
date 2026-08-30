import Foundation

public enum PortableSessionState: Equatable, Sendable {
    case idle
    case active(id: UUID, startedAt: Date)
    case completed(id: UUID, amount: Decimal)
}

public enum PortableSessionEvent: Sendable {
    case started(id: UUID, at: Date)
    case synchronized(id: UUID, startedAt: Date)
    case stopped(amount: Decimal)
    case cleared
}

public enum PortableSessionReducer {
    public static func reduce(
        state: PortableSessionState,
        event: PortableSessionEvent
    ) -> PortableSessionState {
        switch event {
        case let .started(id, at), let .synchronized(id, at):
            .active(id: id, startedAt: at)
        case let .stopped(amount):
            if case let .active(id, _) = state { .completed(id: id, amount: amount) } else { state }
        case .cleared:
            .idle
        }
    }
}
