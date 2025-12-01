import sys
from yotta.core.management import execute_from_command_line

def main():
    """
    Point d'entrée principal quand on tape 'onyx' dans le terminal.
    """
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()