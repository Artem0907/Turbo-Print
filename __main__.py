import sys
from typing import Optional, NoReturn

from src import TurboPrint, LogLevel


def setup_logging(log_level: Optional[LogLevel] = None) -> TurboPrint:
    """
    Set up logging using TurboPrint.

    Args:
        log_level: Optional logging level. If None, uses default value.

    Returns:
        Configured TurboPrint instance

    Raises:
        SystemExit: If initialization fails
    """
    try:
        logger = TurboPrint.get_logger()
        if log_level:
            logger.level = log_level
        return logger
    except Exception as e:
        print(f"Error initializing TurboPrint: {e}", file=sys.stderr)
        sys.exit(1)


def handle_error(error: Exception, message: str) -> NoReturn:
    """
    Handle errors consistently across the application.

    Args:
        error: The exception that occurred
        message: Custom error message to display

    Raises:
        SystemExit: Always raises SystemExit with appropriate exit code
    """
    print(f"{message}: {error}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    """Main entry point for the TurboPrint package."""
    try:
        logger = setup_logging()
        logger("TurboPrint successfully initialized!", LogLevel.INFO)

        for level in LogLevel:
            logger(f"This is a {level.name} message", level)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        handle_error(e, "An unexpected error occurred")


if __name__ == "__main__":
    main()
