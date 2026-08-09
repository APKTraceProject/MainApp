"""
APKTrace - mainapp/main.py

Minimal application entry point. All business logic lives in the `core`
package; the UI lives in `ui`. This file only starts the app.
"""

from core.launcher import launch_app


def main() -> None:
    launch_app()


if __name__ == "__main__":
    main()
