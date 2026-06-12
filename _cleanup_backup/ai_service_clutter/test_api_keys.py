#!/usr/bin/env python3
"""Test all LLM API keys to determine which providers are available."""

import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    """Test Gemini API key."""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "❌ No API key found"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
        response = model.generate_content("Say 'test' in JSON format")
        return f"✅ Working - Response: {response.text[:50]}"
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            return f"❌ Quota exhausted: {error_str[:100]}"
        elif "404" in error_str:
            return f"❌ Model not found: {error_str[:100]}"
        return f"❌ Error: {error_str[:100]}"

def test_deepseek():
    """Test DeepSeek API key."""
    try:
        from openai import OpenAI
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return "❌ No API key found"
        
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=10
        )
        return f"✅ Working - Response: {response.choices[0].message.content}"
    except Exception as e:
        error_str = str(e)
        if "Insufficient Balance" in error_str:
            return f"❌ Insufficient balance"
        return f"❌ Error: {error_str[:100]}"

def test_claude():
    """Test Claude API key."""
    try:
        from anthropic import Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "❌ No API key found"
        
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
        return f"✅ Working - Response: {response.content[0].text}"
    except Exception as e:
        error_str = str(e)
        if "credit balance" in error_str.lower():
            return f"❌ Insufficient credits"
        return f"❌ Error: {error_str[:100]}"

def test_openai():
    """Test OpenAI API key."""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "❌ No API key found"
        
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=10
        )
        return f"✅ Working - Response: {response.choices[0].message.content}"
    except Exception as e:
        error_str = str(e)
        if "quota" in error_str.lower() or "insufficient" in error_str.lower():
            return f"❌ Quota/balance issue"
        return f"❌ Error: {error_str[:100]}"

if __name__ == "__main__":
    print("=" * 80)
    print("LLM API KEY VALIDATION TEST")
    print("=" * 80)
    print()
    
    print("1. Gemini (gemini-2.0-flash-lite):")
    print(f"   {test_gemini()}")
    print()
    
    print("2. DeepSeek (deepseek-chat):")
    print(f"   {test_deepseek()}")
    print()
    
    print("3. Claude (claude-3-5-haiku):")
    print(f"   {test_claude()}")
    print()
    
    print("4. OpenAI (gpt-4o-mini):")
    print(f"   {test_openai()}")
    print()
    
    print("=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print("Use the provider marked with ✅ for experience extraction.")
    print("If all providers fail, you need to:")
    print("  - Add credits to your account")
    print("  - Wait for quota reset (usually 24 hours)")
    print("  - Get a new API key with available quota")
