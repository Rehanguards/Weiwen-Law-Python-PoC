import json
import sys
import subprocess

def create_garak_config():
    # Official Garak REST Generator Schema
    config_data = {
        "rest": {
            "RestGenerator": {
                "name": "Spatial App Studio REST Target",
                "uri": "http://localhost:8000/v1/chat",
                "method": "post",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer sas_secret_key_123"
                },
                "req_template_json_object": {
                    "prompt": "$INPUT",
                    "provider": "ollama"
                },
                "response_json": True,
                "response_json_field": "response"
            }
        }
    }

    with open("garak_config.json", "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    print("✅ Configuration file 'garak_config.json' created successfully.")

def run_garak_scan():
    create_garak_config()

    print("=========================================================")
    print("🚀 STARTING GARAK v0.16.0 SECURITY AUDIT SCAN")
    print("=========================================================\n")

    # Native Garak CLI Command
    cmd = [
        sys.executable, "-m", "garak",
        "--target_type", "rest",
        "-G", "garak_config.json",
        "--probes", "dan,promptinject"
    ]

    subprocess.run(cmd)

if __name__ == "__main__":
    run_garak_scan()