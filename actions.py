import re
from nemoguardrails.actions import action

@action(name="check_input_security_action")
async def check_input_security_action(context: dict) -> bool:
    user_prompt = context.get("user_message", "").lower()

    attack_patterns = [
        # 1. Credential & Sensitive Info Extraction
        r"api\s*key",
        r"private\s*info",
        r"secret\s*key",
        r"credentials",
        r"system\s*prompt",
        r"password",
        
        # 2. Emotional Manipulation / Coercion
        r"save\s*my\s*life",
        r"suicide",
        r"otherwise\s*i\s*will",

        # 3. Hacking & Cyberattacks
        r"\bhack\b",
        r"\bhacking\b",
        r"exploit",
        r"malware",
        r"payload",
        r"reverse shell",

        # 4. Jailbreak Patterns
        r"ignore\s+(all|previous|rules)",
        r"you\s+are\s+now\s+dan",
        r"bypass\s+safety",

        # 5. SQL Injection
        r"select\s+.*\s+from",
        r"drop\s+table",
        r"union\s+select",
        r"--",
        r"or\s+1=1",
    ]

    for pattern in attack_patterns:
        if re.search(pattern, user_prompt):
            return False  # Block Input at Gateway (<100ms)

    return True  # Safe

@action(name="check_output_security_action")
async def check_output_security_action(context: dict) -> bool:
    bot_response = context.get("bot_message", "").lower()

    forbidden_patterns = [
        # 1. PII Data Leaks (Email & Phone Numbers)
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Email Address Regex
        r"\b\d{10}\b",                                      # 10-digit Indian Mobile Numbers
        r"\+?\d{1,3}[-.\s]?\d{10}",                         # Mobile numbers with Country Code

        # 2. Financial & API Secrets
        r"sk-[a-zA-Z0-9]{20,}",                             # OpenAI / API Keys
        r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",         # Credit Cards
        r"sas_secret_key",                                  # Gateway Internal Secret
        
        # 3. System Prompt Leaks
        r"system\s*instructions"
    ]

    for pattern in forbidden_patterns:
        if re.search(pattern, bot_response):
            return False  # Block Output at Gateway (PII / Leak Detected)
            
    return True