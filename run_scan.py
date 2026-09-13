import json
import subprocess
import sys

# 1. Generate YAML Config (Garak 0.16.0 Native Format)
yaml_content = """
plugins:
  generators:
    rest:
      Rest:
        uri: "http://localhost:8000/v1/chat"
        method: "POST"
        headers:
          Content-Type: "application/json"
          Authorization: "Bearer sas_secret_key_123"
        req_template: '{"prompt": "$KEY", "provider": "ollama"}'
        response_json_field: "response"
"""

with open("garak_config.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_content)

# 2. Generate JSON Options
json_config = {
    "uri": "http://localhost:8000/v1/chat",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer sas_secret_key_123"
    },
    "req_template": "{\"prompt\": \"$KEY\", \"provider\": \"ollama\"}",
    "response_json_field": "response"
}

with open("garak_config.json", "w", encoding="utf-8") as f:
    json.dump(json_config, f, indent=2)

print("✅ garak_config.yaml and garak_config.json generated.")

# 3. Execute Scan with Explicit Target Name and Config
command = [
    sys.executable, "-m", "garak",
    "--config", "garak_config.yaml",
    "--target_type", "rest",
    "--target_name", "http://localhost:8000/v1/chat",
    "--generator_option_file", "garak_config.json",
    "--probes", "dan,promptinject"
]

print("🚀 Starting Garak Security Scan...\n")
subprocess.run(command)