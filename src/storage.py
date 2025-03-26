import os
import json
import time
import yaml

class ScreenDescriptionStorage:
    def __init__(self, config_path='config.yaml'):
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Storage path
        self.storage_path = os.path.join(
            self.config['screenshot']['storage_path'], 
            'descriptions'
        )
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Storage for most recent description
        self.latest_description = None

    def save_description(self, image_path, description):
        """
        Save description for a given image
        
        :param image_path: Path to the screenshot
        :param description: Textual description from LLM
        :return: Path to the saved description file
        """
        # Generate unique filename based on timestamp
        timestamp = int(time.time())
        filename = os.path.join(
            self.storage_path, 
            f"description_{timestamp}.json"
        )
        
        # Prepare description data
        description_data = {
            'timestamp': timestamp,
            'image_path': image_path,
            'description': description
        }
        
        # Save description to file
        with open(filename, 'w') as f:
            json.dump(description_data, f, indent=4)
        
        # Update latest description
        self.latest_description = description_data
        
        return filename

    def get_latest_description(self):
        """
        Retrieve the most recent description
        
        :return: Latest description dictionary or None
        """
        return self.latest_description

    def list_descriptions(self, limit=10):
        """
        List recent descriptions
        
        :param limit: Number of recent descriptions to return
        :return: List of description dictionaries
        """
        description_files = sorted(
            [f for f in os.listdir(self.storage_path) if f.startswith('description_')],
            reverse=True
        )
        
        descriptions = []
        for file in description_files[:limit]:
            with open(os.path.join(self.storage_path, file), 'r') as f:
                descriptions.append(json.load(f))
        
        return descriptions