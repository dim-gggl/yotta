import sys

from yotta.core.management import execute_from_command_line


def main():
    """Main entry point for the ``yotta`` CLI."""
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
