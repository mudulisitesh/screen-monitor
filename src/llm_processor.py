import ollama
import yaml
import base64

class LLMProcessor:
    def __init__(self, config_path='config.yaml'):
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # LLM model configuration
        self.model = self.config['llm']['model']

    def process_image(self, image_path):
        """
        Process an image using the local LLM (Ollama)
        
        :param image_path: Path to the image file
        :return: Descriptive text about the image
        """
        # Read the image file and encode it to base64
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        try:
            # Use Ollama to generate description
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': 'Describe what is happening in this image in detail.',
                        'images': [encoded_image]
                    }
                ]
            )
            
            return response['message']['content']
        
        except Exception as e:
            return f"Error processing image: {str(e)}"