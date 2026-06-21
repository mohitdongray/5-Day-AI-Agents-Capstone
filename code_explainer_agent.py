"""
code_explainer_agent.py
Explains any code snippet in plain English using Groq API (fast, reliable).
Caches explanations with confidence scores for quality tracking.
"""
import hashlib
import os
import logging
from typing import Dict, Any
from memory_hub import MemoryHub
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# Groq API imports (using OpenAI-compatible interface for stability)
from openai import OpenAI

# Initialize Groq via OpenAI-compatible interface
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

logger = logging.getLogger("CodeExplainer")


class CodeExplainerAgent:
    def __init__(self, hub: MemoryHub):
        self.name = "CodeExplainer"
        self.hub = hub

    def _calculate_confidence(self, code: str, explanation: str) -> float:
        confidence = 0.0
        if len(explanation) > 200:
            confidence += 0.3
        elif len(explanation) > 100:
            confidence += 0.2
        elif len(explanation) > 50:
            confidence += 0.1
        
        code_keywords = ["function", "class", "method", "variable", "loop", "condition", 
                         "return", "public", "private", "static", "void", "string"]
        found_keywords = sum(1 for kw in code_keywords if kw in explanation.lower())
        confidence += min(0.3, found_keywords * 0.05)
        return min(1.0, confidence)
    
    def run(self, code_snippet: str) -> Dict[str, Any]:
        if not code_snippet.strip():
            return {"status": "error", "message": "No code provided", "agent": self.name}
        
        code_hash = hashlib.md5(code_snippet.encode()).hexdigest()
        
        cached = self.hub.get_cached_code(code_hash)
        if cached:
            logger.info(f"Cache hit for code hash {code_hash[:8]}")
            return {
                "status": "cached",
                "explanation": cached["explanation"],
                "confidence": cached["confidence"],
                "agent": self.name
            }
        
        logger.info("Generating fresh explanation from Gemini...")
        
        prompt = f"""You are a friendly programming tutor. Explain the following code in simple, 
clear terms for a beginner Java developer who knows basic syntax but needs help understanding 
what the code actually does. Focus on the purpose and flow, not line-by-line details unless necessary.
Be confident in your answer and don't include disclaimers.

CODE:
{code_snippet}

EXPLANATION:"""
        
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
                top_p=1
            )
            explanation = response.choices[0].message.content
            logger.info(f"Groq generated explanation ({len(explanation)} chars)")
            
            confidence = self._calculate_confidence(code_snippet, explanation)
            confidence = min(1.0, confidence + 0.2)
            
            self.hub.cache_code(code_hash, explanation, confidence)
            
            return {
                "status": "new",
                "explanation": explanation,
                "confidence": confidence,
                "agent": self.name,
                "model_used": "llama-3.1-8b-instant"
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate explanation: {str(e)}",
                "agent": self.name
            }


class WeatherTool:
    """
    A simple tool that gives your agent the ability to check weather.
    Implements the 'Tools' concept required for the capstone.
    """
    
    @staticmethod
    def get_weather(city: str) -> str:
        import requests
        
        try:
            response = requests.get(f"https://wttr.in/{city}?format=%C+%t", timeout=10)
            if response.status_code == 200:
                weather_text = response.text.strip()
                return f"Weather in {city}: {weather_text}"
            else:
                return f"Could not fetch weather for {city} (HTTP {response.status_code})"
        except Exception as e:
            return f"Weather service error: {str(e)}"