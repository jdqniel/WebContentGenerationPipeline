# WebContentGenerationPipeline/v1/stages/stage_2_generation.py
from .base_stage import BaseStage
from utils.openai_client import OpenAIClient

class GenerationStage(BaseStage):
    """
    Etapa 2: Implementa un proceso de generación síncrono en dos pasos:
    1. Genera el contenido completo.
    2. Genera los recursos de SEO basados en el contenido.
    """
    def __init__(self, client: OpenAIClient, content_prompt_path: str, seo_prompt_path: str):
        self._client = client
        with open(content_prompt_path, 'r', encoding='utf-8') as f:
            self._content_prompt_template = f.read()
        with open(seo_prompt_path, 'r', encoding='utf-8') as f:
            self._seo_prompt_template = f.read()

    def run(self, context: dict) -> dict:
        print("--- Executing Stage 2: Two-Step Content & SEO Generation ---")
        config = context['config']
        
        # 1. Generar el contenido creativo completo
        print("  - Generating Full Content (API Call 1)...")
        content_prompt = self._content_prompt_template.format(
            documentType=config['documentType'],
            strategy_category=config['strategy']['category'],
            strategy_focus=config['strategy']['specificFocus'],
            target_audience=config['generationConfig']['targetAudience'],
            content_goal=config['generationConfig']['contentGoal'],
            content_tone=config['generationConfig']['contentTone'],
            partners=", ".join([p['name'] for p in config.get('partners', [])])
        )
        
        generated_content = self._client.generate_json(
            system_prompt="You are a world-class content strategist and copywriter.",
            user_prompt=content_prompt,
            max_tokens=3000
        )
        
        if not generated_content:
            context['generated_content'] = {"error": "Could not generate main content."}
            context['seo_assets'] = {}
            print("  - 🚨 Failed to generate main content.")
            return context

        # 2. Generar recursos de SEO basados en el contenido
        print("  - Generating SEO Assets (API Call 2)...")
        title = generated_content.get("title", "")
        body = generated_content.get("body_markdown", "")
        
        seo_prompt = self._seo_prompt_template.format(title=title, body=body)
        seo_assets = self._client.generate_json(
            system_prompt="You are an SEO specialist.",
            user_prompt=seo_prompt
        )

        # 3. Pasar todos los resultados a la siguiente etapa
        context['generated_content'] = generated_content
        context['seo_assets'] = seo_assets or {}
        
        print("  - ✅ Content and SEO assets generated successfully.")
        return context