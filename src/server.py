from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import yaml
import os

from .screen_capture import ScreenCapture
from .llm_processor import LLMProcessor
from .storage import ScreenDescriptionStorage

class ScreenMonitorServer:
    def __init__(self, config_path='config.yaml'):
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Initialize components
        self.screen_capture = ScreenCapture(config_path)
        self.llm_processor = LLMProcessor(config_path)
        self.storage = ScreenDescriptionStorage(config_path)
        
        # Create FastAPI app
        self.app = FastAPI(title="Screen Monitor Server")
        
        # Setup routes
        self._setup_routes()
        
        # Start continuous screen capture
        self.screen_capture.start_continuous_capture()

    def _setup_routes(self):
        """Setup API routes"""
        @self.app.get("/screenshot/latest")
        async def get_latest_screenshot():
            """Retrieve the latest screenshot"""
            latest_screenshot = self.screen_capture.get_latest_screenshot()
            if not latest_screenshot or not os.path.exists(latest_screenshot):
                raise HTTPException(status_code=404, detail="No screenshot found")
            return FileResponse(latest_screenshot)

        @self.app.get("/description/latest")
        async def get_latest_description():
            """Retrieve the latest description"""
            # Capture latest screenshot
            latest_screenshot = self.screen_capture.get_latest_screenshot()
            
            if not latest_screenshot:
                raise HTTPException(status_code=404, detail="No screenshot available")
            
            # Process screenshot
            description = self.llm_processor.process_image(latest_screenshot)
            
            # Save description
            description_file = self.storage.save_description(
                latest_screenshot, 
                description
            )
            
            return JSONResponse({
                "description": description,
                "image_path": latest_screenshot
            })

        @self.app.get("/descriptions")
        async def list_descriptions(limit: int = 10):
            """List recent descriptions"""
            descriptions = self.storage.list_descriptions(limit)
            return JSONResponse(descriptions)

        @self.app.get("/screenshot/{timestamp}")
        async def get_screenshot_by_timestamp(timestamp: int):
            """Retrieve a specific screenshot by timestamp"""
            storage_path = self.config['screenshot']['storage_path']
            possible_files = [
                f for f in os.listdir(storage_path) 
                if f.startswith(f"screenshot_{timestamp}")
            ]
            
            if not possible_files:
                raise HTTPException(status_code=404, detail="Screenshot not found")
            
            return FileResponse(os.path.join(storage_path, possible_files[0]))

    def run(self):
        """Run the server"""
        import uvicorn
        uvicorn.run(
            self.app, 
            host=self.config['server']['host'], 
            port=self.config['server']['port']
        )