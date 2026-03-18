"""
LLM-based experience extractor for resume parsing.
Uses various LLM providers (Gemini, DeepSeek, Claude, GPT) to extract structured work experience.
"""

import os
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def extract_experience_with_llm(experience_text: str, llm_provider: str) -> List[Dict]:
    """
    Extract work experience using specified LLM provider.
    
    Args:
        experience_text: Text from the experience section
        llm_provider: LLM provider ID (gemini-2.0-flash-lite, deepseek-v3, claude-haiku-4-5, gpt-4o-mini)
        
    Returns:
        List of experience objects with company, role, dates, location, summary
    """
    
    logger.info(f"🤖 LLM EXTRACTION CALLED - Provider: {llm_provider}")
    logger.info(f"📝 Experience text length: {len(experience_text)} chars")
    logger.info(f"📝 Experience text preview: {experience_text[:200]}...")
    
    system_prompt = "You are an expert resume parser. Your only job is to extract work experience data from resume text and return it as valid JSON. You never add explanation, markdown, or any text outside the JSON array. You handle all resume formats. You never hallucinate data. If a field is missing, return null."
    
    user_prompt = f"""Extract all work experiences from the resume section below. Return ONLY a valid JSON array. No explanation. No markdown. No extra text. Each object must have: company (string or null), role (string or null), start_date (string or null), end_date (string or null), is_current (boolean), location (string or null), summary (2-3 sentence summary string or null). Rules: multiple roles at same company = separate objects. Missing dates = null. Year only like 2019-2022 is fine as-is. summary must be condensed version of bullet points not copy-paste. Never invent missing data. Resume experience section: {experience_text}"""
    
    try:
        if llm_provider == "gemini-2.0-flash-lite":
            result = _call_gemini(system_prompt, user_prompt)
        elif llm_provider == "deepseek-v3":
            result = _call_deepseek(system_prompt, user_prompt)
        elif llm_provider == "claude-haiku-4-5":
            result = _call_claude(system_prompt, user_prompt)
        elif llm_provider == "gpt-4o-mini":
            result = _call_openai(system_prompt, user_prompt)
        else:
            logger.error(f"Unknown LLM provider: {llm_provider}")
            return []
        
        # Save to training data
        _save_training_data(experience_text, result)
        
        logger.info(f"✅ LLM extraction successful - Extracted {len(result)} experiences")
        return result
        
    except Exception as e:
        logger.error(f"❌ LLM extraction failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def _call_gemini(system_prompt: str, user_prompt: str) -> List[Dict]:
    """Call Gemini API."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not found in environment")
            raise ValueError("GEMINI_API_KEY not set")
        
        logger.info(f"🔑 Gemini API key found: {api_key[:10]}...")
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "response_mime_type": "application/json"
            }
        )
        
        logger.info("📡 Calling Gemini API...")
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = model.generate_content(full_prompt)
        
        logger.info(f"📥 Gemini response received: {response.text[:200]}...")
        result = json.loads(response.text)
        
        if not isinstance(result, list):
            logger.warning("Gemini returned non-list, wrapping in list")
            result = [result] if result else []
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON response: {e}")
        # Retry once
        try:
            response = model.generate_content(full_prompt)
            result = json.loads(response.text)
            return result if isinstance(result, list) else []
        except:
            return []
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return []


def _call_deepseek(system_prompt: str, user_prompt: str) -> List[Dict]:
    """Call DeepSeek API."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # DeepSeek might wrap in an object with "experiences" key
        if isinstance(result, dict) and "experiences" in result:
            result = result["experiences"]
        elif isinstance(result, dict) and len(result) == 1:
            # If single key dict, extract the value
            result = list(result.values())[0]
        
        if not isinstance(result, list):
            result = [result] if result else []
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse DeepSeek JSON response: {e}")
        # Retry once
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            result = json.loads(content)
            if isinstance(result, dict):
                result = list(result.values())[0] if len(result) == 1 else []
            return result if isinstance(result, list) else []
        except:
            return []
    except Exception as e:
        logger.error(f"DeepSeek API error: {e}")
        return []


def _call_claude(system_prompt: str, user_prompt: str) -> List[Dict]:
    """Call Claude API."""
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        content = response.content[0].text
        
        # Claude might wrap in markdown code blocks
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        result = json.loads(content)
        
        if not isinstance(result, list):
            result = [result] if result else []
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude JSON response: {e}")
        # Retry once
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            content = response.content[0].text
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            return result if isinstance(result, list) else []
        except:
            return []
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return []


def _call_openai(system_prompt: str, user_prompt: str) -> List[Dict]:
    """Call OpenAI API."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # OpenAI might wrap in an object with "experiences" key
        if isinstance(result, dict) and "experiences" in result:
            result = result["experiences"]
        elif isinstance(result, dict) and len(result) == 1:
            result = list(result.values())[0]
        
        if not isinstance(result, list):
            result = [result] if result else []
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI JSON response: {e}")
        # Retry once
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            result = json.loads(content)
            if isinstance(result, dict):
                result = list(result.values())[0] if len(result) == 1 else []
            return result if isinstance(result, list) else []
        except:
            return []
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return []


def _save_training_data(input_text: str, output_data: List[Dict]) -> None:
    """Save input/output pair to training_data.jsonl for future fine-tuning."""
    try:
        from pathlib import Path
        
        # Get ai-service root directory
        current_file = Path(__file__)
        ai_service_root = current_file.parent.parent
        training_file = ai_service_root / "training_data.jsonl"
        
        training_entry = {
            "input": input_text,
            "output": output_data
        }
        
        # Append to file
        with open(training_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(training_entry) + "\n")
        
        logger.info(f"Saved training data to {training_file}")
        
    except Exception as e:
        logger.warning(f"Failed to save training data: {e}")
