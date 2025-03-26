from src.server import ScreenMonitorServer

def main():
    # Initialize and run the server
    server = ScreenMonitorServer()
    server.run()

if __name__ == "__main__":
    main()