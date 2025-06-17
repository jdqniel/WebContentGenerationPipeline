# WebContentGenerationPipeline/v1/main.py
import json
import random
import time
import os
from pipeline_orchestrator import WebContentPipeline
from dotenv import load_dotenv

load_dotenv()
def load_mock_data(filepath: str):
    """Carga datos de un archivo JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"🚨 Error: El archivo {filepath} no fue encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"🚨 Error: No se pudo decodificar el JSON del archivo {filepath}.")
        return None

def main():
    """
    Función principal para ejecutar el pipeline v1 de generación de contenido web.
    """
    # Usamos una ruta relativa al directorio del proyecto para mayor robustez
    data_path = "data/mock_web_content_data.json"
    output_path = "v1/output.json"

    # 1. Cargar la lista de configuraciones
    all_configs = load_mock_data(data_path)
    if not all_configs or not isinstance(all_configs, list):
        print("Saliendo... El archivo de datos debe existir y contener una lista de configuraciones.")
        return

    # 2. Seleccionar una configuración al azar
    sample_config = random.choice(all_configs)
    
    print("--- Running V1 Pipeline with Random Sample Config ---")
    print(json.dumps(sample_config, indent=2))
    print("------------------------------------------------")

    # 3. Inicializar y ejecutar el pipeline
    pipeline = WebContentPipeline()
    
    start_time = time.monotonic()
    # El método .run() ahora devuelve un diccionario con 'result' y 'metrics'
    pipeline_output = pipeline.run(sample_config)
    end_time = time.monotonic()

    # 4. Extraer el resultado y las métricas
    final_result = pipeline_output.get("result", {})
    metrics = pipeline_output.get("metrics", {})
    metrics["execution_time_seconds"] = end_time - start_time

    # 5. Guardar el resultado final
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Pipeline v1 finished successfully. Output saved to {output_path}")
    except IOError as e:
        print(f"🚨 Error writing output to file: {e}")

    # 6. Imprimir las métricas
    cost_summary = metrics.get("cost_summary", {})
    print("\n--- V1 Pipeline Metrics ---")
    print(f"Execution Time: {metrics.get('execution_time_seconds', 0):.2f} seconds")
    print("Cost Summary:")
    print(f"  - Prompt Tokens:     {cost_summary.get('total_prompt_tokens', 0)}")
    print(f"  - Completion Tokens: {cost_summary.get('total_completion_tokens', 0)}")
    print(f"  - Total Cost (USD):  ${cost_summary.get('total_cost_usd', 0):.6f}")
    print("---------------------------\n")

if __name__ == "__main__":
    main()