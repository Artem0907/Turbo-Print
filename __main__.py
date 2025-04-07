from turbo_print import TurboPrint, LogLevel

def main() -> None:
    """Основная точка входа для пакета TurboPrint."""
    logger = TurboPrint()
    logger.info("TurboPrint initialized successfully!")

if __name__ == "__main__":
    main()
