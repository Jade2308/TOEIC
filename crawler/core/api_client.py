from __future__ import annotations

"""
Resilient Multi-Provider LLM Engine with Key Rotation, Multi-Key Scoped File Uploads,
Model Tier Fallback & Anti-Recitation Safety.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class MultiKeyFileRef:
    """Manages per-key scoped Gemini File uploads to prevent 403 PERMISSION_DENIED on rotation."""

    def __init__(self, file_path: str | Path, clients: List[genai.Client]):
        self.file_path = str(file_path)
        self.clients = clients
        self.cached_refs: Dict[int, Any] = {}

    def get_ref_for_key(self, key_idx: int) -> Any:
        if key_idx not in self.cached_refs:
            p = Path(self.file_path)
            print(f"  [➔] Uploading {p.name} to Gemini Files API for Key #{key_idx + 1}...", flush=True)
            client = self.clients[key_idx]
            for att in range(4):
                try:
                    ref = client.files.upload(file=self.file_path)
                    self.cached_refs[key_idx] = ref
                    break
                except Exception as e:
                    print(f"  [WARN] Upload retry {att+1} for Key #{key_idx+1}: {e}", flush=True)
                    time.sleep(2)
            if key_idx not in self.cached_refs:
                self.cached_refs[key_idx] = client.files.upload(file=self.file_path)
        return self.cached_refs[key_idx]


class ResilientLLMClient:
    """Manages Gemini Multi-Key Rotation and Fallbacks."""

    def __init__(self, keys: Optional[List[str]] = None):
        if genai is None:
            raise ImportError("Package 'google-genai' is required. Run: pip install google-genai")

        # Discover all available Gemini API keys from environment
        if not keys:
            found_keys = []
            for env_var in [
                "GEMINI_API_KEY",
                "GEMINI_API_KEY_2",
                "GEMINI_API_KEY_3",
                "GEMINI_API_KEY_4",
                "GOOGLE_API_KEY",
            ]:
                val = os.getenv(env_var)
                if val and val.strip() and val.strip() not in found_keys:
                    found_keys.append(val.strip())
            self.keys = found_keys
        else:
            self.keys = [k.strip() for k in keys if k and k.strip()]

        if not self.keys:
            print("[ERROR] No valid Gemini API keys found in environment.")
            sys.exit(1)

        # Clear global env vars to prevent google-genai from auto-binding to a single key
        for env_var in ["GOOGLE_API_KEY", "GEMINI_API_KEY"]:
            os.environ.pop(env_var, None)

        self.current_key_idx = 0
        self.clients = [genai.Client(api_key=k) for k in self.keys]
        print(f"[*] ResilientLLMClient initialized with {len(self.keys)} Gemini API Key(s).")

        # Prioritize stable, high-throughput models
        self.models = [
            "gemini-flash-lite-latest",
            "gemini-3-flash-preview",
            "gemini-3.5-flash-lite",
            "gemini-flash-latest",
        ]

    @property
    def client(self) -> genai.Client:
        return self.clients[self.current_key_idx]

    def rotate_key(self):
        old_idx = self.current_key_idx
        self.current_key_idx = (self.current_key_idx + 1) % len(self.keys)
        print(f"  [➔] Rotated Gemini Key: #{old_idx + 1} -> #{self.current_key_idx + 1}", flush=True)

    def upload_file_safe(self, file_path: str | Path) -> MultiKeyFileRef:
        """Returns a MultiKeyFileRef that provides key-scoped file references dynamically."""
        return MultiKeyFileRef(file_path=file_path, clients=self.clients)

    def generate_json_with_retry(
        self,
        contents: List[Any],
        response_schema: Optional[Any] = None,
        system_instruction: Optional[str] = None,
        max_retries: int = 5,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """Calls Gemini with multi-key rotation, key-scoped file resolution, and anti-recitation handling."""
        for attempt in range(max_retries):
            for model in self.models:
                for _ in range(len(self.keys)):
                    try:
                        # Dynamically resolve file references for the CURRENT active key
                        resolved_contents = []
                        for item in contents:
                            if isinstance(item, MultiKeyFileRef):
                                resolved_contents.append(item.get_ref_for_key(self.current_key_idx))
                            else:
                                resolved_contents.append(item)

                        config_kwargs: Dict[str, Any] = {
                            "temperature": temperature,
                            "response_mime_type": "application/json",
                        }
                        if response_schema is not None:
                            config_kwargs["response_schema"] = response_schema
                        if system_instruction is not None:
                            config_kwargs["system_instruction"] = system_instruction

                        config = types.GenerateContentConfig(**config_kwargs)
                        res = self.client.models.generate_content(
                            model=model,
                            contents=resolved_contents,
                            config=config,
                        )

                        if res.text and len(res.text.strip()) > 0:
                            raw_txt = res.text.strip()
                            if raw_txt.startswith("```json"):
                                raw_txt = raw_txt[7:]
                            if raw_txt.startswith("```"):
                                raw_txt = raw_txt[3:]
                            if raw_txt.endswith("```"):
                                raw_txt = raw_txt[:-3]
                            parsed = json.loads(raw_txt.strip())
                            return parsed

                        # Check Finish Reason if text is empty
                        if res.candidates:
                            f_reason = str(getattr(res.candidates[0], "finish_reason", "UNKNOWN"))
                            if "RECITATION" in f_reason:
                                print(f"  [WARN] {model} hit RECITATION filter on key #{self.current_key_idx+1}. Retrying with higher temp...", flush=True)
                                temperature = min(0.7, temperature + 0.3)
                                continue

                    except Exception as e:
                        err_str = str(e)
                        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "limit exceeded" in err_str:
                            print(f"  [WARN] Quota exhausted on key #{self.current_key_idx+1} for {model}. Rotating key...", flush=True)
                            self.rotate_key()
                            time.sleep(1)
                            continue
                        elif "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str:
                            print(f"  [WARN] {model} 503 unavailable (attempt {attempt+1}). Rotating key & trying next...", flush=True)
                            self.rotate_key()
                            time.sleep(2)
                        elif "404" in err_str:
                            break  # Try next model tier
                        else:
                            print(f"  [WARN] {model} on key #{self.current_key_idx+1} error: {err_str[:90]}. Retrying...", flush=True)
                            self.rotate_key()
                            time.sleep(2)

            time.sleep(2)

        raise RuntimeError(f"All LLM retries failed after {max_retries} cycles across all models & keys.")
