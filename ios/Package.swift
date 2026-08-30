// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ParkGoCore",
    platforms: [.macOS(.v14), .iOS(.v18)],
    products: [
        .library(name: "ParkGoCore", targets: ["ParkGoCore"]),
        .executable(name: "ParkGoCoreChecks", targets: ["ParkGoCoreChecks"])
    ],
    targets: [
        .target(
            name: "ParkGoCore",
            path: "ParkGo",
            exclude: [
                "App",
                "Features",
                "Models",
                "Networking",
                "Resources",
                "Services",
                "ParkGo.entitlements",
                "Core/AppConfiguration.swift",
                "Core/AppError.swift",
                "DesignSystem/Components.swift"
            ],
            sources: [
                "Core/PortableSessionReducer.swift",
                "DesignSystem/Formatting.swift"
            ]
        ),
        .executableTarget(
            name: "ParkGoCoreChecks",
            dependencies: ["ParkGoCore"],
            path: "ParkGoCoreTests"
        )
    ]
)
