import os
import requests


def main():
    print(f"TEST OUTPUT: {os.getenv('key1')}; requests_version: {requests.__version__}")


if __name__ == '__main__':
    main()
