import XCTest

final class ParkGoUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testOfflinePresentationHappyPath() throws {
        let app = XCUIApplication()
        app.launchArguments = ["--offline-demo"]
        app.launch()

        XCTAssertTrue(app.staticTexts["testModeBanner"].waitForExistence(timeout: 4))
        let start = app.buttons["startParkingButton"]
        XCTAssertTrue(start.waitForExistence(timeout: 4))
        start.tap()

        let stop = app.buttons["stopParkingButton"]
        XCTAssertTrue(stop.waitForExistence(timeout: 4))
        stop.tap()
        app.buttons.matching(NSPredicate(format: "label BEGINSWITH 'Завершить ·'")).firstMatch.tap()

        app.buttons["Готово"].tap()
        app.tabBars.buttons["История"].tap()
        XCTAssertTrue(app.otherElements["historySessionRow"].firstMatch.waitForExistence(timeout: 4))
    }
}
