import logging


def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info("Hello from db!")


if __name__ == "__main__":
    main()
