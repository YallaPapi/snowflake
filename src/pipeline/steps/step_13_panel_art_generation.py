"""
Step 13 Implementation: Panel Art Generation
Generates actual comic panel images from Step 11 comic script using AI image generation
"""

import json
import hashlib
import base64
import requests
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import io

from src.pipeline.validators.step_13_validator import Step13Validator
from src.ai.generator import AIGenerator

class Step13PanelArtGeneration:
    """
    Generates actual comic panel images using AI image generation APIs
    
    Supports multiple providers:
    - Replicate API (SDXL, Flux)
    - OpenAI DALL-E 3
    - Stability AI
    - Together AI
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step13Validator()
        self.ai_generator = AIGenerator()
        
        # Image generation configuration
        self.default_config = {
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "style": "comic book art, detailed ink lines, professional comic style"
        }
        
        # Character consistency seeds (maintained across panels)
        self.character_seeds = {}
        
        # Style consistency parameters
        self.style_params = {
            "manga": "manga style, black and white, screentones, Japanese comic art",
            "western": "western comic book style, bold colors, dynamic action, Marvel DC style",
            "graphic_novel": "graphic novel style, painterly, realistic, muted colors",
            "noir": "noir style, high contrast, black and white, dramatic shadows"
        }
    
    def execute(self,
                step11_artifact: Dict[str, Any],
                step7_artifact: Dict[str, Any],
                project_id: str,
                generation_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 13: Generate actual comic panel images
        
        Args:
            step11_artifact: Comic script with panel descriptions
            step7_artifact: Character bibles for visual consistency
            project_id: Project identifier
            generation_config: Image generation configuration
            
        Returns:
            Tuple of (success, panel_images_artifact, message)
        """
        if not generation_config:
            generation_config = {
                "provider": "replicate",  # or "openai", "stability", "together"
                "model": "sdxl",
                "style": "western",
                "quality": "standard",
                "generate_all": False  # Set to True to generate all panels
            }
        
        try:
            # Calculate upstream hash
            upstream_hash = hashlib.sha256(
                json.dumps(step11_artifact, sort_keys=True).encode()
            ).hexdigest()
            
            # Extract character designs for consistency
            character_designs = step11_artifact.get('character_designs', {})
            self._initialize_character_profiles(character_designs, step7_artifact)
            
            # Get comic pages and panels
            comic_pages = step11_artifact.get('pages', [])
            
            # Generate images for panels
            max_pages = generation_config.get('max_pages', len(comic_pages))
            print(f"Generating art for {min(max_pages, len(comic_pages))} pages...")
            generated_panels = []
            
            for page_idx, page in enumerate(comic_pages[:max_pages]):
                print(f"  Processing page {page_idx + 1}/{min(max_pages, len(comic_pages))}...")
                
                for panel in page.get('panels', []):
                    panel_image = self._generate_panel_image(
                        panel, page_idx, character_designs, generation_config
                    )
                    generated_panels.append(panel_image)
            
            # Create artifact with generated images
            artifact = self._create_artifact(
                generated_panels, comic_pages, character_designs,
                project_id, upstream_hash, generation_config
            )
            
            # Validate artifact
            is_valid, errors = self.validator.validate(artifact)
            if not is_valid:
                return False, {}, f"Validation failed: {errors}"
            
            # Save artifact and images
            artifact_path = self._save_artifact(artifact, project_id)
            
            return True, artifact, f"Step 13 completed. Generated {len(generated_panels)} panel images."
            
        except Exception as e:
            return False, {}, f"Error in Step 13: {str(e)}"
    
    def _initialize_character_profiles(self, character_designs: Dict, step7_artifact: Dict):
        """Initialize character visual profiles for consistency"""
        
        # Extract character bibles - check both possible keys
        bibles = step7_artifact.get('character_bibles', step7_artifact.get('bibles', []))
        
        for bible in bibles:
            char_name = bible.get('name', 'unknown')
            
            # Create consistent visual description
            physical = bible.get('physical', {})
            
            # Generate a stable seed for this character (for consistency)
            import hashlib
            char_seed = int(hashlib.md5(char_name.encode()).hexdigest()[:8], 16) % 1000000
            self.character_seeds[char_name] = char_seed
            
            # Build character prompt
            char_prompt = self._build_character_prompt(char_name, physical, bible)
            
            # Store in character designs
            if char_name not in character_designs:
                character_designs[char_name] = {}
            
            character_designs[char_name]['visual_prompt'] = char_prompt
            character_designs[char_name]['seed'] = char_seed
    
    def _build_character_prompt(self, name: str, physical: Dict, bible: Dict) -> str:
        """Build consistent character visual prompt with detailed features for consistency"""
        
        # Start with character identifier tag for consistency
        prompt_parts = [f"[{name.upper()}:1.2]"]  # Use character name as a strong identifier
        
        # Add age and gender first for better consistency
        if physical.get('age'):
            prompt_parts.append(f"{physical['age']} years old")
        if physical.get('gender'):
            prompt_parts.append(physical['gender'])
        
        # Face and facial features (critical for consistency)
        face_details = []
        if physical.get('face_shape'):
            face_details.append(f"{physical['face_shape']} face")
        if physical.get('eyes'):
            face_details.append(f"{physical['eyes']} eyes")
        if physical.get('eyebrows'):
            face_details.append(f"{physical['eyebrows']} eyebrows")
        if physical.get('nose'):
            face_details.append(f"{physical['nose']} nose")
        if physical.get('lips'):
            face_details.append(f"{physical['lips']} lips")
        if physical.get('skin_tone'):
            face_details.append(f"{physical['skin_tone']} skin")
        
        if face_details:
            prompt_parts.append("with " + ", ".join(face_details))
        
        # Hair (very important for consistency)
        if physical.get('hair'):
            hair_desc = physical['hair']
            # Be more specific about hair
            if 'color' in hair_desc.lower() or 'blonde' in hair_desc.lower() or 'brown' in hair_desc.lower() or 'black' in hair_desc.lower():
                prompt_parts.append(f"{hair_desc} hair")
            else:
                prompt_parts.append(f"distinctive {hair_desc} hair")
        
        # Build and body type
        if physical.get('build'):
            prompt_parts.append(f"{physical['build']} build")
        if physical.get('height'):
            prompt_parts.append(f"{physical['height']} height")
        
        # Distinctive features (scars, tattoos, etc.)
        if physical.get('distinctive_features'):
            prompt_parts.append(physical['distinctive_features'])
        
        # Clothing style (if consistent throughout)
        if physical.get('usual_clothing'):
            prompt_parts.append(f"wearing {physical['usual_clothing']}")
        elif physical.get('appearance'):
            # Use appearance if it contains clothing info
            if 'wear' in physical['appearance'].lower() or 'dress' in physical['appearance'].lower():
                prompt_parts.append(physical['appearance'])
        
        # Add personality traits that affect appearance
        personality = bible.get('personality', {})
        if isinstance(personality, str):
            if 'confident' in personality.lower():
                prompt_parts.append("confident posture")
            if 'nervous' in personality.lower() or 'anxious' in personality.lower():
                prompt_parts.append("anxious expression")
            if 'cheerful' in personality.lower() or 'happy' in personality.lower():
                prompt_parts.append("warm smile")
        elif isinstance(personality, dict):
            if personality.get('traits'):
                traits = personality['traits']
                if 'confident' in str(traits).lower():
                    prompt_parts.append("confident bearing")
                if 'shy' in str(traits).lower():
                    prompt_parts.append("reserved demeanor")
        
        # Add consistency anchor phrase
        prompt_parts.append("consistent character design")
        
        return ", ".join(prompt_parts)
    
    def _get_panel_seed(self, characters: List[str], character_designs: Dict) -> int:
        """
        Get a consistent seed for a panel based on the characters present.
        This ensures characters look the same across all panels they appear in.
        """
        if not characters:
            # No specific characters, use a default seed
            return 42
        
        # If single character, use their specific seed
        if len(characters) == 1:
            char_name = characters[0]
            if char_name in character_designs and 'seed' in character_designs[char_name]:
                return character_designs[char_name]['seed']
            elif char_name in self.character_seeds:
                return self.character_seeds[char_name]
        
        # Multiple characters: combine their seeds deterministically
        combined_seed = 0
        for char_name in sorted(characters):  # Sort for consistency
            if char_name in character_designs and 'seed' in character_designs[char_name]:
                combined_seed ^= character_designs[char_name]['seed']
            elif char_name in self.character_seeds:
                combined_seed ^= self.character_seeds[char_name]
        
        # Ensure seed is within valid range
        return combined_seed % 1000000 if combined_seed > 0 else 42
    
    def _generate_panel_image(self, panel: Dict, page_idx: int, 
                             character_designs: Dict, config: Dict) -> Dict:
        """Generate actual image for a single panel"""
        
        panel_num = panel.get('panel_number', 1)
        description = panel.get('description', '')
        characters = panel.get('characters', [])
        mood = panel.get('mood', 'neutral')
        shot_type = panel.get('shot_type', 'medium_shot')
        
        # Build the image prompt
        prompt = self._build_panel_prompt(
            description, characters, character_designs, 
            mood, shot_type, config
        )
        
        # Get character-specific seed for consistency
        character_seed = self._get_panel_seed(characters, character_designs)
        
        # Update config with character-specific seed
        panel_config = config.copy()
        panel_config['seed'] = character_seed
        panel_config['characters_in_panel'] = characters
        
        # Generate the image based on provider
        provider = config.get('provider', 'replicate')
        use_consistent_model = config.get('use_consistent_character', False)
        
        if provider == 'replicate':
            # Use consistent-character model if specified and characters are present
            if use_consistent_model and characters:
                # Try to get reference image for main character if available
                character_ref = None
                if characters and len(characters) > 0:
                    main_char = characters[0]
                    if main_char in character_designs:
                        character_ref = character_designs[main_char].get('reference_image')
                
                image_data = self._generate_with_consistent_character(prompt, panel_config, character_ref)
            else:
                image_data = self._generate_with_replicate(prompt, panel_config)
        elif provider == 'openai':
            image_data = self._generate_with_openai(prompt, panel_config)
        elif provider == 'stability':
            image_data = self._generate_with_stability(prompt, panel_config)
        else:
            # Fallback: generate placeholder
            image_data = self._generate_placeholder(prompt, panel_num, page_idx)
        
        return {
            "page": page_idx + 1,
            "panel": panel_num,
            "prompt": prompt,
            "seed_used": character_seed,
            "image_data": image_data,
            "metadata": {
                "mood": mood,
                "shot_type": shot_type,
                "characters": characters,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _build_panel_prompt(self, description: str, characters: List[str],
                           character_designs: Dict, mood: str, 
                           shot_type: str, config: Dict) -> str:
        """Build detailed prompt for panel generation with emphasis on character consistency"""
        
        # Get style from config
        style_key = config.get('style', 'western')
        style_prompt = self.style_params.get(style_key, self.style_params['western'])
        
        prompt_parts = []
        
        # IMPORTANT: Put character descriptions FIRST for better consistency
        # Character descriptions should come before scene description
        if characters:
            # Add a consistency instruction
            if len(characters) == 1:
                prompt_parts.append(f"Comic panel featuring {characters[0]}")
            else:
                prompt_parts.append(f"Comic panel featuring {', '.join(characters)}")
            
            # Add detailed character descriptions
            for char_name in characters:
                if char_name in character_designs:
                    char_prompt = character_designs[char_name].get('visual_prompt', '')
                    if char_prompt:
                        prompt_parts.append(char_prompt)
        
        # Now add the scene description
        if description:
            prompt_parts.append(description)
        
        # Add shot type
        shot_descriptions = {
            "close_up": "close-up shot, face focus, detailed facial features visible",
            "medium_shot": "medium shot, waist up, clear character details",
            "wide_shot": "wide shot, full scene, full body visible",
            "extreme_close_up": "extreme close-up, eyes or facial detail focus"
        }
        prompt_parts.append(shot_descriptions.get(shot_type, "medium shot"))
        
        # Add mood
        mood_descriptions = {
            "tense": "tense atmosphere, dramatic lighting",
            "happy": "bright, cheerful atmosphere",
            "dramatic": "dramatic mood, high contrast lighting",
            "neutral": "balanced lighting and mood",
            "dark": "dark, ominous atmosphere, shadows"
        }
        prompt_parts.append(mood_descriptions.get(mood, "neutral mood"))
        
        # Add style
        prompt_parts.append(style_prompt)
        
        # Add consistency and quality modifiers
        consistency_modifiers = [
            "consistent character appearance",
            "same character design throughout",
            "high quality",
            "detailed",
            "professional comic art"
        ]
        prompt_parts.extend(consistency_modifiers)
        
        # Add negative prompt hints (will be used in negative_prompt parameter)
        if characters:
            prompt_parts.append(f"(maintaining exact appearance of {', '.join(characters)})")
        
        return ", ".join(prompt_parts)
    
    def _generate_with_consistent_character(self, prompt: str, config: Dict, 
                                           character_ref_image: Optional[str] = None) -> Dict:
        """Generate image using fofr/consistent-character model for better character consistency"""
        
        api_key = os.getenv('REPLICATE_API_TOKEN')
        
        if not api_key:
            return self._generate_with_replicate(prompt, config)
        
        try:
            import replicate
            
            # Use the consistent-character model
            model = "fofr/consistent-character:9c77a3c2f884193fcee4d89645f02a0b9def9434f9e03cb98460456b831c8772"
            
            # Get character seed
            seed = config.get('seed', 42)
            
            # Prepare input
            model_input = {
                "prompt": prompt,
                "number_of_outputs": 1,
                "number_of_images_per_pose": 1,
                "randomise_poses": False,
                "seed": seed,
                "output_format": "png",
                "output_quality": 90
            }
            
            # Add reference image if available
            if character_ref_image:
                model_input["subject"] = character_ref_image
            
            # Add negative prompt
            characters_in_panel = config.get('characters_in_panel', [])
            negative_prompt = "inconsistent, different face, morphing features"
            if characters_in_panel:
                negative_prompt += f", different looking {', '.join(characters_in_panel)}"
            model_input["negative_prompt"] = negative_prompt
            
            output = replicate.run(model, input=model_input)
            
            if output and len(output) > 0:
                image_url = str(output[0]) if hasattr(output[0], '__str__') else output[0]
                
                # Download image
                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    image_data = base64.b64encode(response.content).decode('utf-8')
                    
                    return {
                        "type": "generated",
                        "provider": "replicate-consistent",
                        "model": "consistent-character",
                        "url": image_url,
                        "base64": image_data,
                        "format": "png"
                    }
            
            # Fallback to standard SDXL
            return self._generate_with_replicate(prompt, config)
            
        except Exception as e:
            print(f"    Consistent-character generation failed: {e}, falling back to SDXL")
            return self._generate_with_replicate(prompt, config)
    
    def _generate_with_replicate(self, prompt: str, config: Dict) -> Dict:
        """Generate image using Replicate API"""
        
        # Check if API key is available
        api_key = os.getenv('REPLICATE_API_TOKEN')
        
        if not api_key:
            print("  Warning: REPLICATE_API_TOKEN not found, using placeholder")
            return self._generate_placeholder(prompt, 1, 1)
        
        try:
            import replicate
            
            # Use SDXL or Flux model
            model_name = config.get('model', 'sdxl')
            
            if model_name == 'sdxl':
                model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
            else:  # flux
                model = "black-forest-labs/flux-schnell:bf53bdb93fba2977db39da098dc966138580629d4bb3daa96f5b90ed807d004f"
            
            # Get character-specific seed for consistency
            seed = config.get('seed', 42)
            
            # Build enhanced negative prompt for character consistency
            negative_prompt_parts = [
                "blurry", "low quality", "distorted", "ugly",
                "inconsistent character", "different face", "changing appearance",
                "morphing features", "unstable design", "varying character model"
            ]
            
            # Add character-specific negative prompts
            characters_in_panel = config.get('characters_in_panel', [])
            if characters_in_panel:
                negative_prompt_parts.append(f"different looking {', '.join(characters_in_panel)}")
            
            negative_prompt = ", ".join(negative_prompt_parts)
            
            # Log for debugging
            print(f"    Using seed {seed} for characters: {characters_in_panel}")
            
            output = replicate.run(
                model,
                input={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": self.default_config['width'],
                    "height": self.default_config['height'],
                    "num_inference_steps": self.default_config['num_inference_steps'],
                    "guidance_scale": self.default_config['guidance_scale'],
                    "seed": seed
                }
            )
            
            # Get image URL from output (handle FileOutput objects)
            if output and len(output) > 0:
                # Replicate returns FileOutput objects, extract the URL
                image_url = str(output[0]) if hasattr(output[0], '__str__') else output[0]
                
                # Download image
                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    image_data = base64.b64encode(response.content).decode('utf-8')
                    
                    return {
                        "type": "generated",
                        "provider": "replicate",
                        "model": model_name,
                        "url": image_url,
                        "base64": image_data,
                        "format": "png"
                    }
            
            # Fallback if generation failed
            return self._generate_placeholder(prompt, 1, 1)
            
        except Exception as e:
            import traceback
            error_detail = {
                "provider": "replicate", 
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"    Replicate generation failed: {e}")
            print(f"    Traceback: {error_detail['traceback'][:200]}...")
            return self._generate_placeholder(prompt, 1, 1)
    
    def _generate_with_openai(self, prompt: str, config: Dict) -> Dict:
        """Generate image using OpenAI DALL-E 3"""
        
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("  Warning: OPENAI_API_KEY not found, using placeholder")
            return self._generate_placeholder(prompt, 1, 1)
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality=config.get('quality', 'standard'),
                n=1
            )
            
            if response.data:
                image_url = response.data[0].url
                
                # Download image
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    image_data = base64.b64encode(img_response.content).decode('utf-8')
                    
                    return {
                        "type": "generated",
                        "provider": "openai",
                        "model": "dall-e-3",
                        "url": image_url,
                        "base64": image_data,
                        "format": "png"
                    }
            
            return self._generate_placeholder(prompt, 1, 1)
            
        except Exception as e:
            print(f"    OpenAI generation failed: {e}")
            return self._generate_placeholder(prompt, 1, 1)
    
    def _generate_with_stability(self, prompt: str, config: Dict) -> Dict:
        """Generate image using Stability AI"""
        
        api_key = os.getenv('STABILITY_API_KEY')
        
        if not api_key:
            print("  Warning: STABILITY_API_KEY not found, using placeholder")
            return self._generate_placeholder(prompt, 1, 1)
        
        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            body = {
                "text_prompts": [{"text": prompt, "weight": 1}],
                "cfg_scale": self.default_config['guidance_scale'],
                "steps": self.default_config['num_inference_steps'],
                "width": self.default_config['width'],
                "height": self.default_config['height']
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('artifacts'):
                    image_data = data['artifacts'][0]['base64']
                    
                    return {
                        "type": "generated",
                        "provider": "stability",
                        "model": "sdxl",
                        "base64": image_data,
                        "format": "png"
                    }
            
            return self._generate_placeholder(prompt, 1, 1)
            
        except Exception as e:
            print(f"    Stability generation failed: {e}")
            return self._generate_placeholder(prompt, 1, 1)
    
    def _generate_placeholder(self, prompt: str, panel_num: int, page_num: int) -> Dict:
        """Generate a placeholder image when API is not available"""
        
        # Create a simple placeholder image with PIL
        img = Image.new('RGB', (1024, 1024), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add border
        draw.rectangle([0, 0, 1023, 1023], outline='black', width=3)
        
        # Add diagonal lines for comic panel effect
        for i in range(0, 1024, 100):
            draw.line([i, 0, 0, i], fill='lightgray', width=1)
            draw.line([1024-i, 1024, 1024, 1024-i], fill='lightgray', width=1)
        
        # Add text
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Panel info
        text = f"Page {page_num} - Panel {panel_num}"
        draw.text((512, 100), text, fill='black', font=font, anchor='mm')
        
        # Truncated prompt
        prompt_lines = []
        words = prompt.split()
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 40:
                prompt_lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        
        if current_line:
            prompt_lines.append(' '.join(current_line))
        
        # Draw prompt text
        y_offset = 200
        for line in prompt_lines[:10]:  # Limit to 10 lines
            draw.text((512, y_offset), line, fill='darkgray', font=font, anchor='mm')
            y_offset += 50
        
        # Add placeholder notice
        draw.text((512, 900), "[Placeholder - Set API key for real generation]", 
                 fill='red', font=font, anchor='mm')
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            "type": "placeholder",
            "provider": "local",
            "model": "placeholder",
            "base64": image_data,
            "format": "png",
            "prompt_used": prompt[:200] + "..."
        }
    
    def _create_artifact(self, generated_panels: List[Dict], comic_pages: List[Dict],
                        character_designs: Dict, project_id: str, 
                        upstream_hash: str, config: Dict) -> Dict:
        """Create Step 13 artifact with generated images"""
        
        return {
            "metadata": {
                "step": 13,
                "step_name": "panel_art_generation",
                "project_id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "source_step": 11,
                "upstream_hash": upstream_hash
            },
            "generation_config": config,
            "character_designs": character_designs,
            "character_seeds": self.character_seeds,
            "panels": generated_panels,
            "statistics": {
                "total_panels_generated": len(generated_panels),
                "total_pages": len(comic_pages),
                "provider_used": config.get('provider', 'placeholder'),
                "style": config.get('style', 'western')
            }
        }
    
    def _save_artifact(self, artifact: Dict[str, Any], project_id: str) -> str:
        """Save artifact and generated images"""
        
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create images directory
        images_path = project_path / "comic_panels"
        images_path.mkdir(exist_ok=True)
        
        # Save each panel image
        for panel_data in artifact['panels']:
            page_num = panel_data['page']
            panel_num = panel_data['panel']
            image_data = panel_data['image_data']
            
            if image_data.get('base64'):
                # Save the image file
                filename = f"page_{page_num:03d}_panel_{panel_num:02d}.png"
                image_path = images_path / filename
                
                # Decode and save
                image_bytes = base64.b64decode(image_data['base64'])
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Update panel data with file path
                panel_data['file_path'] = str(image_path)
        
        # Save JSON artifact
        artifact_path = project_path / "step_13_panel_art.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            # Remove base64 data from saved JSON to reduce size
            save_artifact = artifact.copy()
            for panel in save_artifact['panels']:
                if 'image_data' in panel and 'base64' in panel['image_data']:
                    del panel['image_data']['base64']
            
            json.dump(save_artifact, f, indent=2, ensure_ascii=False)
        
        return str(artifact_path)

if __name__ == "__main__":
    # Test the implementation
    step13 = Step13PanelArtGeneration()
    print("Step 13: Panel Art Generation initialized")
    print("Supports: Replicate, OpenAI, Stability AI")
    print("Set environment variables for API access:")
    print("  - REPLICATE_API_TOKEN")
    print("  - OPENAI_API_KEY")
    print("  - STABILITY_API_KEY")