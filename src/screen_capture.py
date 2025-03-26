import os
from mss import mss
from PIL import Image
import time
import threading
import yaml
import logging

class ScreenCapture:
    def __init__(self, config_path='config.yaml'):
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = {
                'screenshot': {
                    'interval': 60,
                    'storage_path': "./screenshots"
                }
            }
        
        # Ensure screenshot directory exists
        self.storage_path = self.config['screenshot']['storage_path']
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Screenshot interval
        self.interval = self.config['screenshot']['interval']
        
        # Capture method with thread-safe initialization
        self.sct = None
        self._init_screen_capture()
        
        # Most recent screenshot
        self.latest_screenshot = None
        
        # Threading setup
        self.capture_thread = None
        self.running = False
        
        # Thread-level lock
        self._lock = threading.Lock()

    def _init_screen_capture(self):
        """
        Initialize screen capture with error handling
        Ensures MSS is properly initialized for each thread
        """
        try:
            # Reinitialize MSS for each thread
            self.sct = mss()
            
            # Validate monitors are available
            if not self.sct.monitors:
                raise ValueError("No monitors found")
        except Exception as e:
            self.logger.error(f"Screen capture initialization error: {e}")
            raise

    def capture_screen(self):
        """Capture the entire screen with robust error handling"""
        try:
            # Ensure thread-safe initialization
            if not self.sct:
                self._init_screen_capture()
            
            # Use thread-safe monitoring
            with self._lock:
                # Capture primary monitor (index 0)
                monitor = self.sct.monitors[0]
                screenshot = self.sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Generate unique filename
                timestamp = int(time.time())
                filename = os.path.join(
                    self.storage_path, 
                    f"screenshot_{timestamp}.png"
                )
                
                # Save screenshot
                img.save(filename)
                
                # Update latest screenshot
                self.latest_screenshot = filename
                
                self.logger.info(f"Screenshot captured: {filename}")
                
                return filename
        
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            # Attempt to reinitialize on failure
            try:
                self._init_screen_capture()
            except Exception as init_error:
                self.logger.critical(f"Failed to reinitialize screen capture: {init_error}")
            return None

    def start_continuous_capture(self):
        """Start continuous screenshot capturing with error handling"""
        if not self.running:
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            
            try:
                self.capture_thread.start()
                self.logger.info("Continuous screen capture started")
            except Exception as e:
                self.logger.error(f"Failed to start capture thread: {e}")
                self.running = False

    def stop_continuous_capture(self):
        """Stop continuous screenshot capturing"""
        self.running = False
        if self.capture_thread:
            try:
                self.capture_thread.join(timeout=5)
                self.logger.info("Continuous screen capture stopped")
            except Exception as e:
                self.logger.error(f"Error stopping capture thread: {e}")

    def _capture_loop(self):
        """Internal method for continuous capturing with error handling"""
        while self.running:
            try:
                self.capture_screen()
                time.sleep(self.interval)
            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                # Prevent tight error loops
                time.sleep(5)

    def get_latest_screenshot(self):
        """Get the path of the most recent screenshot"""
        return self.latest_screenshot