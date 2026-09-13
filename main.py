import traceback
import nest_asyncio
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from nemoguardrails import RailsConfig, LLMRails
from pydantic import BaseModel
import actions  # Registers custom actions

# Event loop conflict fix
nest_asyncio.apply()

app = FastAPI(title="Spatial Enterprise AI Gateway")
security = HTTPBearer()

# Load NeMo Rules Engine
try:
    config = RailsConfig.from_path("./config")
    rails = LLMRails(config)
    print("✅ [SPATIAL GATEWAY] NeMo Rails Engine Loaded Successfully!")
except Exception as e:
    print(f"❌ [SPATIAL GATEWAY] Config Load Error: {e}")

class ChatRequest(BaseModel):
    prompt: str
    provider: str = "ollama"

@app.post("/v1/chat")
async def secure_chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials.credentials != "sas_secret_key_123":
        raise HTTPException(status_code=401, detail="Invalid Gateway Key")

    try:
        # Run through NeMo Rails Pipeline
        res = await rails.generate_async(prompt=request.prompt)
        
        # FIX: NeMo directly returns a string, so we assign 'res' directly
        if isinstance(res, dict):
            response_text = res.get("response", str(res))
        else:
            response_text = str(res)

        # Check if NeMo blocked the response or input
        if "[SPATIAL GATEWAY" in response_text:
            return {"status": "BLOCKED", "response": response_text}

        return {"status": "SUCCESS", "response": response_text}

    except Exception as e:
        print("\n❌ ===== DETAILED BACKEND TRACEBACK =====")
        traceback.print_exc()
        print("=========================================\n")
        raise HTTPException(status_code=500, detail=str(e))