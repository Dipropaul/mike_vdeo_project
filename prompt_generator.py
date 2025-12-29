"""
Image Prompt Generator Module
Creates detailed image prompts from script using OpenAI GPT
"""
from openai import OpenAI
import config
from typing import List, Dict


class ImagePromptGenerator:
    """Generate image prompts from script using AI"""
    
    def __init__(self):
        """Initialize the prompt generator"""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None
        self.image_count = config.IMAGE_COUNT
    
    def generate_prompts(self, script: str, style: str = 'Modern Abstract', 
                        keywords: str = '', negative_keywords: str = '') -> List[Dict[str, str]]:
        """
        Generate image prompts from script
        
        Args:
            script: The video script
            style: Visual style for images
            keywords: Additional keywords to include
            negative_keywords: Keywords to avoid in images
            
        Returns:
            List of dictionaries containing prompts and negative prompts
        """
        try:
            # Create the system prompt
            negative_prompt_base = negative_keywords if negative_keywords else "blurry, low quality, distorted, text, watermark"
            keywords_instruction = f"Include these keywords: {keywords}" if keywords else "Use vivid, descriptive language"
            
            system_prompt = f"""You are an expert at creating detailed image prompts for AI image generation.
Your task is to create exactly {self.image_count} unique image prompts based on the provided script.

Requirements:
1. Each prompt should represent a key scene or moment from the script
2. Use the style: {style}
3. {keywords_instruction}
4. Make prompts detailed and vivid
5. Each prompt should be 1-2 sentences
6. For negative prompts, always include: {negative_prompt_base}

Return ONLY a JSON array with this exact format:
[
    {{
        "prompt": "detailed scene description in {style} style",
        "negative_prompt": "{negative_prompt_base}"
    }},
    ...
]
"""
            
            print(f"Generating {self.image_count} image prompts...")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Script: {script}"}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            # Parse response
            import json
            content = response.choices[0].message.content
            
            # Extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            json_str = content[start_idx:end_idx]
            
            prompts = json.loads(json_str)
            
            # Ensure we have exactly the right number of prompts
            if len(prompts) < self.image_count:
                # Duplicate some prompts if needed
                while len(prompts) < self.image_count:
                    prompts.append(prompts[-1])
            elif len(prompts) > self.image_count:
                prompts = prompts[:self.image_count]
            
            print(f"Generated {len(prompts)} image prompts")
            return prompts
            
        except Exception as e:
            print(f"Error generating prompts: {e}")
            # Return default prompts as fallback
            return self._generate_default_prompts(script, style)
    
    def _generate_default_prompts(self, script: str, style: str) -> List[Dict[str, str]]:
        """Generate simple default prompts as fallback"""
        words = script.split()
        chunk_size = len(words) // self.image_count
        
        prompts = []
        for i in range(self.image_count):
            start = i * chunk_size
            end = start + chunk_size if i < self.image_count - 1 else len(words)
            chunk = ' '.join(words[start:end])
            
            prompts.append({
                "prompt": f"{chunk[:100]} in {style} style, high quality, detailed",
                "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy"
            })
        
        return prompts


if __name__ == "__main__":
    # Test the prompt generator
    generator = ImagePromptGenerator()
    test_script = "A journey through ancient Egypt. The pyramids stand tall under the desert sun. Pharaohs ruled with wisdom and power."
    prompts = generator.generate_prompts(test_script, style="Comic Book", keywords="ancient, historical")
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nPrompt {i}:")
        print(f"  Prompt: {prompt['prompt']}")
        print(f"  Negative: {prompt['negative_prompt']}")
