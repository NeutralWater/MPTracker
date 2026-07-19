import sqlite3

from carriers.globkurier import GlobKurierError, GlobKurierTracker
from database import (
    add_package,
    get_active_packages,
    initialize_database,
    mark_delivered,
)


TRACKERS = {
    "globkurier": GlobKurierTracker(),
}


def display_result(result) -> None:
    print("\n" + "=" * 50)
    print(f"Carrier: {result.carrier}")
    print(f"Order:   {result.tracking_number}")
    print(f"Status:  {result.status_name}")
    print("=" * 50)

    if not result.events:
        print("No tracking events available.")
        return

    for event in result.events:
        print(f"\n{event.timestamp:%Y-%m-%d %H:%M}")
        print(f"  {event.name}")

        if event.location:
            print(f"  Location: {event.location}")

        if event.tracking_number:
            print(f"  Carrier number: {event.tracking_number}")


def add_new_package() -> None:
    tracking_number = input(
        "\nEnter GlobKurier order number: "
    ).strip()

    nickname = input(
        "Enter package nickname (optional): "
    ).strip()

    tracker = TRACKERS["globkurier"]

    try:
        result = tracker.track(tracking_number)
    except (ValueError, GlobKurierError) as exc:
        print(f"\nError: {exc}")
        return

    try:
        add_package(
            tracking_number=result.tracking_number,
            carrier="globkurier",
            nickname=nickname or None,
        )
    except sqlite3.IntegrityError:
        print("\nThat tracking number is already saved.")
        return

    print("\nPackage saved.")
    display_result(result)

    if result.delivered:
        mark_delivered(result.tracking_number)


def show_tracked_packages() -> None:
    packages = get_active_packages()

    if not packages:
        print("\nNo active packages are being tracked.")
        return

    for package in packages:
        tracker = TRACKERS.get(package["carrier"])

        if tracker is None:
            print(
                f"\nUnsupported carrier: {package['carrier']}"
            )
            continue

        title = package["nickname"] or package["tracking_number"]

        print("\n" + "#" * 50)
        print(title)
        print("#" * 50)

        try:
            result = tracker.track(package["tracking_number"])
        except (ValueError, GlobKurierError) as exc:
            print(f"Error: {exc}")
            continue

        display_result(result)

        if result.delivered:
            mark_delivered(result.tracking_number)


def main() -> None:
    initialize_database()

    while True:
        print("\nMPTracker")
        print("=" * 30)
        print("1. View tracked packages")
        print("2. Add new package")
        print("3. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            show_tracked_packages()
        elif choice == "2":
            add_new_package()
        elif choice == "3":
            print("\nGoodbye.")
            break
        else:
            print("\nInvalid option.")


if __name__ == "__main__":
    main()