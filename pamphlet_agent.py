#!/usr/bin/env python3
"""
AI Agent for Pamphlet Generation
Combines Ollama text generation with Stable Diffusion image generation
"""

import requests
import json
import base64
import random
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import io
import os

@dataclass
class PamphletRequest:
    """Data class for pamphlet generation request"""
    product_name: str
    description: str
    tone: str
    target_audience: str
    key_features: List[str]
    call_to_action: str
    color_scheme: str = "modern"
    style: str = "professional"
    image_prompt: str = ""
    custom_image: str = ""
    image_source: str = "ai_generated"
    regeneration_index: int = 0


VARIATION_PROFILES: List[Dict[str, str]] = [
    {
        "name": "vibrant_action",
        "headline_hint": "Use an energetic verb and spotlight the product's most electrifying payoff.",
        "description_hint": "Lead with a bold promise, weave in a sensory detail, and address the reader directly.",
        "cta_hint": "Inject immediate urgency with a time-bound incentive.",
        "tagline_hint": "Craft a punchy, rhythmic phrase with subtle alliteration."
    },
    {
        "name": "premium_story",
        "headline_hint": "Frame the product as a premium experience or story-driven journey.",
        "description_hint": "Paint a mini narrative that contrasts a problem with an elevated resolution.",
        "cta_hint": "Invite the reader to 'discover' or 'experience' something exclusive.",
        "tagline_hint": "Blend sophistication with aspiration in 3-4 words."
    },
    {
        "name": "data_focused",
        "headline_hint": "Anchor the headline in a bold metric or tangible outcome.",
        "description_hint": "Surface a quantifiable benefit and mention a differentiating feature.",
        "cta_hint": "Encourage action with confidence-building wording (e.g., 'See How').",
        "tagline_hint": "Use a crisp, confidence-forward statement."
    },
    {
        "name": "lifestyle_mood",
        "headline_hint": "Emphasize the lifestyle transformation or mood shift the product unlocks.",
        "description_hint": "Highlight how the product fits seamlessly into the reader's day-to-day life.",
        "cta_hint": "Prompt the reader to start their journey toward that lifestyle.",
        "tagline_hint": "Capture the feeling in a short, emotive phrase."
    }
]

IMAGE_VARIATION_HINTS: List[str] = [
    "Feature diagonal lighting, soft depth-of-field, and open whitespace on the upper third for typography.",
    "Use a geometric framing element on one side and a cooler color palette with subtle gradients.",
    "Incorporate warm accent lighting with a bokeh background and a foreground focal point positioned off-center.",
    "Highlight natural textures with gentle shadows and a clean negative space band suitable for body copy."
]

class OllamaTextGenerator:
    """Low-level helper that talks to the Ollama HTTP API."""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate_pamphlet_text(self, request: PamphletRequest) -> Dict[str, str]:
        """
        Generate comprehensive pamphlet text content optimized for visual pamphlets.
        
        This is intentionally a focused, single-responsibility helper used by
        TextGenerationAgent so higher-level orchestration stays clean.
        """

        profile = VARIATION_PROFILES[request.regeneration_index % len(VARIATION_PROFILES)] if VARIATION_PROFILES else {}
        is_variation = request.regeneration_index > 0
        variation_suffix = "\nPlease ensure this version feels distinct from any previous iterations while staying on-brand."
        
        # Generate compelling headline
        headline_prompt = f"""
        Create a compelling, attention-grabbing headline for a pamphlet about: {request.product_name}
        Description: {request.description}
        Tone: {request.tone}
        Target audience: {request.target_audience}
        {"Additional directive: " + profile.get("headline_hint", "") if is_variation else ""}
        
        The headline should be:
        - 3-6 words maximum (for pamphlet layout)
        - {request.tone} in tone
        - Bold and impactful
        - Perfect for {request.target_audience}
        - Eye-catching and memorable
        {"- Deliver a fresh phrasing that differs from prior versions" if is_variation else ""}
        
        Return only the headline, no quotes or additional text.{variation_suffix if is_variation else ""}
        """
        
        headline = self._call_ollama(headline_prompt) or request.product_name
        
        # Generate short, punchy description for pamphlet
        description_prompt = f"""
        Write a concise, persuasive description for a pamphlet about: {request.product_name}
        
        Original description: {request.description}
        Key features: {', '.join(request.key_features)}
        Tone: {request.tone}
        Target audience: {request.target_audience}
        Style: {request.style}
        {"Variation directive: " + profile.get("description_hint", "") if is_variation else ""}
        
        The description should be:
        - 1-2 short paragraphs (max 3-4 sentences total)
        - {request.tone} and {request.style}
        - Highlight key benefits, not just features
        - Perfect for pamphlet layout
        - Appeal to {request.target_audience}
        - Easy to read and scan
        {"- Present a noticeably different angle than previous drafts" if is_variation else ""}
        
        Return only the description text.{variation_suffix if is_variation else ""}
        """
        
        description = self._call_ollama(description_prompt) or f"Discover {request.product_name}: {', '.join(request.key_features[:3])}. {request.call_to_action}"
        
        # Generate call-to-action
        cta_prompt = f"""
        Create a compelling call-to-action for a pamphlet about: {request.product_name}
        
        Original CTA: {request.call_to_action}
        Tone: {request.tone}
        Target audience: {request.target_audience}
        {"Variation directive: " + profile.get("cta_hint", "") if is_variation else ""}
        
        The CTA should be:
        - 1 short sentence (max 8-10 words)
        - Action-oriented and urgent
        - {request.tone} in tone
        - Perfect for pamphlet button or banner
        - Clear and specific
        {"- Provide an alternate framing versus previous CTAs" if is_variation else ""}
        
        Return only the call-to-action text.{variation_suffix if is_variation else ""}
        """
        
        cta = self._call_ollama(cta_prompt) or (request.call_to_action or "Learn more today")
        
        # Generate tagline
        tagline_prompt = f"""
        Create a memorable tagline for: {request.product_name}
        
        Description: {request.description}
        Tone: {request.tone}
        Target audience: {request.target_audience}
        {"Variation directive: " + profile.get("tagline_hint", "") if is_variation else ""}
        
        The tagline should be:
        - 2-4 words maximum
        - Memorable and catchy
        - {request.tone} in tone
        - Perfect for pamphlet subheading
        - Capture the essence of the product
        {"- Offer a distinctly new phrasing" if is_variation else ""}
        
        Return only the tagline.{variation_suffix if is_variation else ""}
        """
        
        tagline = self._call_ollama(tagline_prompt) or request.product_name
        
        return {
            "headline": headline.strip().replace('"', '').replace("'", ""),
            "description": description.strip(),
            "call_to_action": cta.strip(),
            "tagline": tagline.strip().replace('"', '').replace("'", "")
        }
    
    def _call_ollama(self, prompt: str) -> str:
        """Make API call to Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""


class TextGenerationAgent:
    """
    TextGenerationAgent
    -------------------
    Responsible for generating high-quality structured pamphlet content
    using Ollama. This wraps the lower-level OllamaTextGenerator and exposes
    a narrow, easy-to-toggle interface for the pamphlet system.
    """

    def __init__(self, text_backend: Optional[OllamaTextGenerator] = None) -> None:
        self.text_backend = text_backend or OllamaTextGenerator()

    def generate(self, request: PamphletRequest) -> Dict[str, str]:
        """
        Produce a structured text payload for a pamphlet.
        
        Output keys:
        - headline
        - description
        - call_to_action
        - tagline
        """
        return self.text_backend.generate_pamphlet_text(request)


class ContentEditingAgent:
    """
    ContentEditingAgent
    -------------------
    Light-weight editor that can refine tone, grammar hints, and length of
    content based on layout needs.

    For predictability and to avoid extra latency, this implementation uses
    simple deterministic heuristics (length limiting, whitespace cleanup).
    It can be upgraded later to call Ollama for smarter edits.
    """

    def __init__(self, max_description_chars: int = 480, max_headline_words: int = 8) -> None:
        self.max_description_chars = max_description_chars
        self.max_headline_words = max_headline_words

    def edit(self, text_content: Dict[str, str], request: PamphletRequest) -> Dict[str, str]:
        """Return a refined copy of the text content."""

        refined = dict(text_content)

        # Normalize whitespace
        for key in ["headline", "description", "call_to_action", "tagline"]:
            value = refined.get(key, "") or ""
            refined[key] = " ".join(value.split())

        # Shorten headline slightly to keep it layout-friendly
        headline_words = refined.get("headline", "").split()
        if len(headline_words) > self.max_headline_words:
            refined["headline"] = " ".join(headline_words[: self.max_headline_words])

        # Limit description length to keep it within panel/text area
        description = refined.get("description", "")
        if len(description) > self.max_description_chars:
            trimmed = description[: self.max_description_chars].rsplit(" ", 1)[0]
            refined["description"] = trimmed + "…"

        return refined

class StableDiffusionGenerator:
    """Handles image generation using Stability AI API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    
    def generate_pamphlet_image(self, request: PamphletRequest, text_content: Dict[str, str]) -> Optional[bytes]:
        """Generate background image for pamphlet"""
        
        variation_hint = ""
        if request.regeneration_index and IMAGE_VARIATION_HINTS:
            variation_hint = IMAGE_VARIATION_HINTS[request.regeneration_index % len(IMAGE_VARIATION_HINTS)]
        
        # Use custom uploaded image if provided
        if request.image_source == 'custom_upload' and request.custom_image:
            try:
                # Decode base64 image
                image_data = base64.b64decode(request.custom_image)
                return image_data
            except Exception as e:
                print(f"Error processing custom image: {e}")
                # Fall back to AI generation
        
        # Use custom image prompt if provided, otherwise generate based on product type
        if request.image_prompt and request.image_prompt.strip():
            image_prompt = f"""
            {request.image_prompt}
            
            Additional requirements for pamphlet design:
            - Professional pamphlet background
            - Space for text overlay
            - {request.tone} and {request.style} aesthetic
            - Perfect for {request.target_audience}
            - High quality, 4K resolution
            - Clean composition with room for headlines and text
            {"- " + variation_hint if variation_hint else ""}
            """
        else:
            # Create detailed prompt for image generation based on product type
            if any(word in request.product_name.lower() for word in ['food', 'cookies', 'biscuits', 'sweets', 'chocolate', 'bakery', 'restaurant', 'cafe']):
                image_prompt = f"""
                Professional food product pamphlet background for {request.product_name}:
                - Appetizing food photography style
                - Warm, inviting colors (golden, brown, cream tones)
                - Clean white space for text overlay
                - High-quality commercial food photography
                - {request.tone} and {request.style} aesthetic
                - Perfect for {request.target_audience}
                - Professional lighting and composition
                - Space for headline and text
                - 4K quality, magazine-style photography
                {"- " + variation_hint if variation_hint else ""}
                """
            elif any(word in request.product_name.lower() for word in ['tech', 'software', 'app', 'digital', 'computer', 'phone', 'gadget']):
                image_prompt = f"""
                Modern tech product pamphlet background for {request.product_name}:
                - Clean, minimalist tech aesthetic
                - Blue, white, and silver color scheme
                - Geometric patterns and clean lines
                - High-tech, professional look
                - {request.tone} and {request.style} design
                - Perfect for {request.target_audience}
                - Space for text overlay
                - 4K quality, modern design
                {"- " + variation_hint if variation_hint else ""}
                """
            elif any(word in request.product_name.lower() for word in ['beauty', 'cosmetics', 'skincare', 'makeup', 'fashion', 'clothing']):
                image_prompt = f"""
                Elegant beauty/fashion pamphlet background for {request.product_name}:
                - Soft, elegant beauty photography
                - Pastel or sophisticated color palette
                - Clean, luxurious aesthetic
                - {request.tone} and {request.style} mood
                - Perfect for {request.target_audience}
                - Space for text overlay
                - 4K quality, magazine-style photography
                {"- " + variation_hint if variation_hint else ""}
                """
            else:
                image_prompt = f"""
                Professional product pamphlet background for {request.product_name}:
                - {request.style} and {request.tone} style
                - {request.color_scheme} color scheme
                - Clean, modern layout with space for text
                - High quality, professional photography style
                - Suitable for {request.target_audience}
                - Product-focused but not cluttered
                - Elegant and sophisticated
                - 4K quality, commercial photography
                {"- " + variation_hint if variation_hint else ""}
                """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*"
            }
            
            files = {
                "prompt": (None, image_prompt),
                "output_format": (None, "png"),
                "aspect_ratio": (None, "4:5"),  # Good for pamphlet (portrait)
                "mode": (None, "text-to-image")
            }
            
            response = requests.post(self.base_url, headers=headers, files=files, timeout=60)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None

class PamphletDesigner:
    """Handles the visual design and layout of the pamphlet"""
    
    def __init__(self):
        self.font_candidates: Dict[str, List[str]] = {
            "Arial": [
                "arial.ttf",
                "Arial.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ],
            "Arial-Bold": [
                "arialbd.ttf",
                "Arial Bold.ttf",
                "Arial-Bold.ttf",
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ],
            "Helvetica": [
                "Helvetica.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ],
            "Helvetica-Bold": [
                "Helvetica Bold.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ],
            "Times": [
                "Times New Roman.ttf",
                "times.ttf",
                "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            ],
            "Times-Bold": [
                "Times New Roman Bold.ttf",
                "timesbd.ttf",
                "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            ],
            "Georgia": [
                "Georgia.ttf",
                "/System/Library/Fonts/Supplemental/Georgia.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            ],
            "Georgia-Bold": [
                "Georgia Bold.ttf",
                "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            ],
            "Verdana": [
                "Verdana.ttf",
                "/System/Library/Fonts/Supplemental/Verdana.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ],
            "Verdana-Bold": [
                "Verdana Bold.ttf",
                "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            ],
        }
        self.default_layout_cycle = ["centered", "split", "left-aligned", "right-aligned"]
    
    def create_pamphlet(
        self,
        image_data: bytes,
        text_content: Dict[str, str],
        request: PamphletRequest,
    ) -> bytes:
        """Create the final pamphlet design"""
        
        base_image = Image.open(io.BytesIO(image_data)).convert("RGBA")
        canvas_size = (1200, 1600)
        base_image = ImageOps.fit(base_image, canvas_size, Image.Resampling.LANCZOS)
        
        layout_choice = self.default_layout_cycle[
            request.regeneration_index % len(self.default_layout_cycle)
        ]
        
        config = self._build_design_config(request, layout_choice)
        textless_canvas = self._compose_layout(
            base_image,
            text_content,
            config,
            features=request.key_features,
            render_text=False,
        )
        composed = self._compose_layout(
            base_image,
            text_content,
            config,
            features=request.key_features,
            render_text=True,
        )
        
        final_output = io.BytesIO()
        composed.convert("RGB").save(final_output, format="PNG", quality=95)
        
        base_output = io.BytesIO()
        textless_canvas.convert("RGB").save(base_output, format="PNG", quality=95)
        return final_output.getvalue(), base_output.getvalue()
    
    def apply_edits(
        self,
        base_image: Image.Image,
        edits: Dict[str, Any],
        text_content: Optional[Dict[str, str]] = None,
        features: Optional[List[str]] = None,
    ) -> Image.Image:
        """
        Apply editing controls to an existing pamphlet image and re-render text to match the preview.
        """
        image = base_image.convert("RGBA")
        target_size = (
            int(edits.get("size", {}).get("width", image.width)),
            int(edits.get("size", {}).get("height", image.height)),
        )
        
        # Apply cropping if requested before resizing
        crop_type = edits.get("imageCrop", "none")
        if crop_type and crop_type != "none":
            image = self._apply_cropping(image, crop_type)
        
        # Fit image to requested size using positioning preference
        position = edits.get("imagePosition", "center")
        image = self._fit_with_position(image, target_size, position)
        
        # Apply image level filters
        filter_type = edits.get("imageFilter", "none")
        intensity = int(edits.get("filterIntensity", 50))
        image = self._apply_image_filter(image, filter_type, intensity)
        
        overall_brightness = int(edits.get("overallBrightness", 100))
        if overall_brightness != 100:
            brightness_base = image.convert("RGB")
            enhancer = ImageEnhance.Brightness(brightness_base)
            image = enhancer.enhance(overall_brightness / 100).convert("RGBA")
        
        # Build layout configuration from edits
        config = self._edits_to_config(edits)
        textless_canvas = self._compose_layout(
            image,
            text_content or {},
            config,
            features=features,
            render_text=False,
        )
        composed = self._compose_layout(
            image,
            text_content or {},
            config,
            features=features,
            render_text=True,
        )
        return composed.convert("RGB"), textless_canvas.convert("RGB")
    
    def _build_design_config(self, request: PamphletRequest, layout: str) -> Dict[str, Any]:
        palette = self._get_color_scheme(request.color_scheme)
        return {
            "layout": layout,
            "headline_font": "Arial-Bold",
            "body_font": "Arial",
            # Panel opacity is left in config but the default is now effectively
            # "no panel" so that text appears directly over the background image.
            # LayoutFormattingAgent can choose to re-enable subtle panels if ever needed.
            "panel_opacity": 0.0,
            "headline_size": 70,
            "tagline_size": 34,
            "body_size": 28,
            "feature_size": 26,
            "cta_size": 34,
            "cta_padding": (36, 22),
            "border_radius": 28,
            "panel_radius": 36,
            "panel_shadow": 30,
            "line_spacing": 1.25,
            "text_shadow": 30,
            "cta_shadow": 35,
            "colors": {
                "text": palette["text"],
                "accent": palette["accent"],
                "cta_bg": palette["cta"],
                "cta_text": (255, 255, 255),
                "panel": palette["overlay"],
            },
            # Whether to render a background panel box behind the text at all.
            # Default is False per UI request to remove rectangular artifacts.
            "show_panel": False,
        }
    
    def _edits_to_config(self, edits: Dict[str, Any]) -> Dict[str, Any]:
        palette = {
            "text": self._parse_color(edits.get("bodyColor", "#ffffff"), (255, 255, 255)),
            "accent": self._parse_color(edits.get("headlineColor", "#ffffff"), (255, 255, 255)),
            "cta_bg": self._parse_color(edits.get("ctaBgColor", "#ff6464"), (255, 100, 100)),
            "cta_text": self._parse_color(edits.get("ctaTextColor", "#ffffff"), (255, 255, 255)),
            "panel": (0, 0, 0),
        }
        return {
            "layout": edits.get("layout", "centered"),
            "text_anchor": edits.get("textPlacement", "top"),
            "headline_font": edits.get("headlineFont", "Arial-Bold"),
            "body_font": edits.get("bodyFont", "Arial"),
            "panel_opacity": max(
                0.0,
                min(
                    1.0,
                    (100 - int(edits.get("backgroundOpacity", 80))) / 100 + 0.15,
                ),
            ),
            "headline_size": int(edits.get("headlineSize", 72)),
            "tagline_size": max(20, min(60, int(edits.get("bodySize", 28)) + 6)),
            "body_size": int(edits.get("bodySize", 28)),
            "feature_size": max(18, int(edits.get("bodySize", 28)) - 2),
            "cta_size": max(22, int(edits.get("bodySize", 28)) + 4),
            "cta_padding": (32, 18),
            "border_radius": int(edits.get("borderRadius", 12)),
            "panel_radius": max(18, int(edits.get("borderRadius", 12)) + 12),
            "panel_shadow": int(edits.get("shadowIntensity", 0)),
            "line_spacing": 1.2,
            "text_shadow": int(edits.get("textShadow", 0)),
            "cta_shadow": int(edits.get("shadowIntensity", 0)),
            "colors": palette,
            # For edited pamphlets we respect the same default: no solid box,
            # but this flag can be toggled from a higher-level agent later.
            "show_panel": False,
        }
    
    def _compose_layout(
        self,
        base_image: Image.Image,
        text_content: Dict[str, str],
        config: Dict[str, Any],
        features: Optional[List[str]] = None,
        render_text: bool = True,
    ) -> Image.Image:
        image = base_image.copy().convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        width, height = image.size
        margin_x = int(width * 0.08)
        top_margin = int(height * 0.08)
        bottom_margin = int(height * 0.12)
        text_area_width = width - (margin_x * 2)
        align = "center"
        x_start = margin_x
        
        if config["layout"] == "centered":
            x_start = (width - text_area_width) // 2
        elif config["layout"] == "left-aligned":
            align = "left"
        elif config["layout"] == "right-aligned":
            align = "right"
            x_start = width - margin_x - text_area_width
        elif config["layout"] == "split":
            align = "left"
            text_area_width = int(width * 0.42)
            x_start = width - text_area_width - margin_x
        
        panel_rect = (
            x_start,
            top_margin,
            x_start + text_area_width,
            height - bottom_margin,
        )
        # The background panel is now optional and disabled by default to avoid
        # any "box" artifact behind the text. Text readability is handled via
        # shadows and color choices instead.
        if config.get("show_panel", False) and config.get("panel_opacity", 0) > 0:
            self._draw_panel(overlay, panel_rect, config)
        
        fonts = {
            "headline": self._load_font(config["headline_font"], config["headline_size"]),
            "tagline": self._load_font(config["body_font"], config["tagline_size"]),
            "body": self._load_font(config["body_font"], config["body_size"]),
            "feature": self._load_font(config["body_font"], config["feature_size"]),
            "cta": self._load_font(config["headline_font"], config["cta_size"]),
        }
        
        draw = ImageDraw.Draw(overlay)
        removals = (text_content or {}).get("removeLines", {}) or {}
        custom_lines: List[str] = (text_content or {}).get("customText", []) or []
        estimated_height = self._estimate_content_height(
            text_content or {},
            fonts,
            text_area_width,
            features or [],
            removals=removals,
            custom_lines=custom_lines,
        )
        panel_height = panel_rect[3] - panel_rect[1]
        anchor = config.get("text_anchor", "top")
        if anchor == "middle":
            y_cursor = panel_rect[1] + max(0, (panel_height - estimated_height) // 2)
        elif anchor == "bottom":
            y_cursor = panel_rect[1] + max(0, panel_height - estimated_height)
        else:
            y_cursor = panel_rect[1]
        line_gap = int(config["body_size"] * config["line_spacing"])
        
        if render_text:
            # Headline
            headline = (text_content or {}).get("headline", "").strip()
            if headline and not removals.get("headline"):
                y_cursor = self._draw_text_line(
                    draw,
                    headline.upper(),
                    fonts["headline"],
                    config["colors"]["accent"],
                    (x_start, y_cursor, text_area_width),
                    align,
                    config["text_shadow"],
                )
                y_cursor += int(config["headline_size"] * 0.08)
            
            # Tagline
            tagline = (text_content or {}).get("tagline", "").strip()
            if tagline and not removals.get("tagline"):
                y_cursor = self._draw_text_line(
                    draw,
                    tagline.upper(),
                    fonts["tagline"],
                    config["colors"]["text"],
                    (x_start, y_cursor, text_area_width),
                    align,
                    config["text_shadow"],
                )
                y_cursor += int(config["tagline_size"] * 0.4)
            
            # Description
            description = (text_content or {}).get("description", "").strip()
            if description and not removals.get("description"):
                wrapped_lines = self._wrap_text(description, fonts["body"], text_area_width)
                for line in wrapped_lines:
                    y_cursor = self._draw_text_line(
                        draw,
                        line,
                        fonts["body"],
                        config["colors"]["text"],
                        (x_start, y_cursor, text_area_width),
                        align,
                        config["text_shadow"],
                    )
                    y_cursor += int(config["body_size"] * 0.15)
                y_cursor += line_gap
            
            # Feature list (for generated pamphlets)
            if features:
                y_cursor += int(config["body_size"] * 0.4)
                feature_title = "Key Features"
                y_cursor = self._draw_text_line(
                    draw,
                    feature_title.upper(),
                    fonts["tagline"],
                    config["colors"]["accent"],
                    (x_start, y_cursor, text_area_width),
                    align if config["layout"] != "centered" else "left",
                    config["text_shadow"],
                )
                y_cursor += int(config["feature_size"] * 0.4)
                
                bullet_align = align if config["layout"] != "centered" else "left"
                bullet_x_start = x_start if bullet_align != "right" else x_start + text_area_width
                for feature in features[:4]:
                    bullet_text = f"• {feature}"
                    y_cursor = self._draw_text_line(
                        draw,
                        bullet_text,
                        fonts["feature"],
                        config["colors"]["text"],
                        (bullet_x_start, y_cursor, text_area_width),
                        bullet_align,
                        config["text_shadow"],
                    )
                    y_cursor += int(config["feature_size"] * 0.3)
                y_cursor += line_gap
            
            # CTA button
            cta = (text_content or {}).get("call_to_action", "").strip()
            if cta and not removals.get("call_to_action"):
                y_cursor += int(config["cta_size"] * 0.4)
                cta_text = cta.upper()
                self._draw_cta(
                    overlay,
                    draw,
                    cta_text,
                    fonts["cta"],
                    config,
                    (x_start, y_cursor, text_area_width),
                    align,
                )
            
            # Custom text block
            if custom_lines and not removals.get("custom"):
                y_cursor += int(config["body_size"] * 0.6)
                for line in custom_lines:
                    y_cursor = self._draw_text_line(
                        draw,
                        line,
                        fonts["body"],
                        config["colors"]["text"],
                        (x_start, y_cursor, text_area_width),
                        align,
                        config["text_shadow"],
                    )
                    y_cursor += int(config["body_size"] * 0.2)
        
        composed = Image.alpha_composite(image, overlay)
        border_radius = config.get("border_radius", 0)
        if border_radius > 0:
            composed = self._apply_border_radius(composed, border_radius)
        return composed
    
    def _get_color_scheme(self, scheme: str) -> Dict[str, Tuple[int, int, int]]:
        schemes = {
            "modern": {
                "text": (240, 247, 255),
                "accent": (111, 203, 255),
                "cta": (255, 102, 102),
                "overlay": (12, 24, 42),
            },
            "elegant": {
                "text": (255, 255, 255),
                "accent": (255, 215, 0),
                "cta": (194, 24, 91),
                "overlay": (35, 22, 58),
            },
            "minimal": {
                "text": (38, 38, 38),
                "accent": (18, 132, 108),
                "cta": (0, 112, 201),
                "overlay": (245, 245, 245),
            },
        }
        return schemes.get(scheme, schemes["modern"])
    
    def _draw_panel(self, overlay: Image.Image, rect: Tuple[int, int, int, int], config: Dict[str, Any]) -> None:
        panel_color = config["colors"]["panel"]
        alpha = int(max(0.0, min(0.92, config.get("panel_opacity", 0.7))) * 255)
        rgba = (*panel_color, alpha)
        draw = ImageDraw.Draw(overlay)
        radius = config.get("panel_radius", 32)
        
        shadow_strength = config.get("panel_shadow", 0)
        if shadow_strength > 0:
            shadow_layer = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            shadow_alpha = int(min(180, shadow_strength * 2.2))
            shadow_draw.rounded_rectangle(rect, radius=radius, fill=(0, 0, 0, shadow_alpha))
            blurred_shadow = shadow_layer.filter(ImageFilter.GaussianBlur(radius=18))
            overlay.alpha_composite(blurred_shadow)
        
        draw.rounded_rectangle(rect, radius=radius, fill=rgba)
    
    def _draw_text_line(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int],
        context: Tuple[int, int, int],
        align: str,
        shadow_intensity: int,
    ) -> int:
        if not text:
            return context[1]
        
        x_start, y_pos, width_available = context
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if align == "left":
            x = x_start
        elif align == "right":
            x = x_start + width_available - text_width
        else:
            x = x_start + (width_available - text_width) // 2
        
        if shadow_intensity > 0:
            shadow_alpha = int(min(200, shadow_intensity * 2.4))
            shadow_color = (0, 0, 0, shadow_alpha)
            for dx, dy in [(-2, 2), (2, 2), (0, 3)]:
                draw.text((x + dx, y_pos + dy), text, font=font, fill=shadow_color)
        
        draw.text((x, y_pos), text, font=font, fill=(*color, 255))
        return y_pos + text_height
    
    def _draw_cta(
        self,
        overlay: Image.Image,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
        config: Dict[str, Any],
        context: Tuple[int, int, int],
        align: str,
    ) -> None:
        x_start, y_pos, width_available = context
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        padding_x, padding_y = config.get("cta_padding", (30, 18))
        box_width = text_width + padding_x * 2
        box_height = text_height + padding_y * 2
        
        if align == "left":
            box_x = x_start
        elif align == "right":
            box_x = x_start + width_available - box_width
        else:
            box_x = x_start + (width_available - box_width) // 2
        
        box_y = y_pos
        cta_bg = Image.new("RGBA", (box_width, box_height), (*config["colors"]["cta_bg"], 235))
        
        # Optional drop shadow
        shadow_intensity = config.get("cta_shadow", 0)
        if shadow_intensity > 0:
            shadow = Image.new("RGBA", (box_width, box_height), (0, 0, 0, int(1.5 * shadow_intensity)))
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))
            overlay.paste(shadow, (box_x + 3, box_y + 6), shadow)
        
        mask = Image.new("L", (box_width, box_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        radius = max(18, config.get("border_radius", 12))
        mask_draw.rounded_rectangle(
            [(0, 0), (box_width, box_height)],
            radius=radius,
            fill=255,
        )
        overlay.paste(cta_bg, (box_x, box_y), mask)
        
        text_x = box_x + (box_width - text_width) // 2
        text_y = box_y + (box_height - text_height) // 2
        draw.text(
            (text_x, text_y),
            text,
            font=font,
            fill=(*config["colors"]["cta_text"], 255),
        )

    def _estimate_content_height(
        self,
        text_content: Dict[str, str],
        fonts: Dict[str, ImageFont.FreeTypeFont],
        text_area_width: int,
        features: List[str],
        removals: Optional[Dict[str, bool]] = None,
        custom_lines: Optional[List[str]] = None,
    ) -> int:
        """
        Lightweight height estimator so we can anchor text vertically (top/middle/bottom)
        without rendering twice. This keeps edits predictable for users who want the
        text block positioned above the image focal point.
        """
        height = 0
        removals = removals or {}
        custom_lines = custom_lines or []

        def add(bbox_height: int) -> None:
            nonlocal height
            height += max(0, bbox_height)

        headline = (text_content or {}).get("headline", "").strip()
        if headline and not removals.get("headline"):
            hb = fonts["headline"].getbbox(headline)
            add(hb[3] - hb[1])
            height += int(fonts["headline"].size * 0.08)

        tagline = (text_content or {}).get("tagline", "").strip()
        if tagline and not removals.get("tagline"):
            tb = fonts["tagline"].getbbox(tagline)
            add(tb[3] - tb[1])
            height += int(fonts["tagline"].size * 0.4)

        description = (text_content or {}).get("description", "").strip()
        if description and not removals.get("description"):
            wrapped = self._wrap_text(description, fonts["body"], text_area_width)
            bb = fonts["body"].getbbox("Hg")
            per_line = bb[3] - bb[1]
            add(len(wrapped) * per_line)
            height += len(wrapped) * int(fonts["body"].size * 0.15)
            height += int(fonts["body"].size * 1.1)

        if features:
            height += int(fonts["body"].size * 0.4)
            title_bb = fonts["tagline"].getbbox("KEY FEATURES")
            add(title_bb[3] - title_bb[1])
            height += int(fonts["feature"].size * 0.4)
            feature_bb = fonts["feature"].getbbox("• Sample feature")
            add(len(features[:4]) * (feature_bb[3] - feature_bb[1]))
            height += len(features[:4]) * int(fonts["feature"].size * 0.3)
            height += int(fonts["body"].size * 0.4)

        cta = (text_content or {}).get("call_to_action", "").strip()
        if cta and not removals.get("call_to_action"):
            cta_bb = fonts["cta"].getbbox(cta.upper())
            add(cta_bb[3] - cta_bb[1])
            height += int(fonts["cta"].size * 0.8)

        if custom_lines and not removals.get("custom"):
            bb = fonts["body"].getbbox("Hg")
            per_line = bb[3] - bb[1]
            add(len(custom_lines) * per_line)
            height += len(custom_lines) * int(fonts["body"].size * 0.2)

        return max(1, height)
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        words = text.split()
        lines: List[str] = []
        current_line: List[str] = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            try:
                text_width = font.getlength(test_line)
            except AttributeError:
                bbox = font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        return lines
    
    def _load_font(self, font_key: str, size: int) -> ImageFont.FreeTypeFont:
        candidates = self.font_candidates.get(font_key, [])
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()
    
    def _parse_color(self, color_value: Any, default: Tuple[int, int, int]) -> Tuple[int, int, int]:
        if isinstance(color_value, (list, tuple)) and len(color_value) >= 3:
            return tuple(int(c) for c in color_value[:3])
        if isinstance(color_value, str):
            value = color_value.strip().lstrip("#")
            if len(value) == 6:
                try:
                    r = int(value[0:2], 16)
                    g = int(value[2:4], 16)
                    b = int(value[4:6], 16)
                    return (r, g, b)
                except ValueError:
                    pass
        return default
    
    def _apply_border_radius(self, image: Image.Image, radius: int) -> Image.Image:
        if radius <= 0:
            return image
        radius = min(radius, min(image.size) // 2)
        rounded = Image.new("RGBA", image.size, (0, 0, 0, 0))
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
        rounded.paste(image, (0, 0), mask)
        return rounded
    
    def _fit_with_position(
        self,
        image: Image.Image,
        target_size: Tuple[int, int],
        position: str,
    ) -> Image.Image:
        centering_map = {
            "center": (0.5, 0.5),
            "top": (0.5, 0.1),
            "bottom": (0.5, 0.9),
            "left": (0.1, 0.5),
            "right": (0.9, 0.5),
        }
        centering = centering_map.get(position, (0.5, 0.5))
        return ImageOps.fit(image, target_size, Image.Resampling.LANCZOS, centering=centering)
    
    def _apply_image_filter(self, image: Image.Image, filter_type: str, intensity: int) -> Image.Image:
        intensity = max(0, min(100, intensity))
        if filter_type == "brightness":
            base = image.convert("RGB")
            enhancer = ImageEnhance.Brightness(base)
            return enhancer.enhance(1 + (intensity - 50) / 70).convert("RGBA")
        if filter_type == "contrast":
            base = image.convert("RGB")
            enhancer = ImageEnhance.Contrast(base)
            return enhancer.enhance(1 + (intensity - 50) / 70).convert("RGBA")
        if filter_type == "saturate":
            base = image.convert("RGB")
            enhancer = ImageEnhance.Color(base)
            return enhancer.enhance(1 + (intensity - 50) / 65).convert("RGBA")
        if filter_type == "blur":
            blur_radius = max(0.1, intensity / 20)
            return image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        if filter_type == "sepia":
            sepia = image.convert("RGB")
            width, height = sepia.size
            pixels = sepia.load()
            for py in range(height):
                for px in range(width):
                    r, g, b = pixels[px, py]
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[px, py] = (
                        min(255, tr),
                        min(255, tg),
                        min(255, tb),
                    )
            return sepia.convert("RGBA")
        if filter_type == "grayscale":
            return image.convert("L").convert("RGBA")
        return image
    
    def _apply_cropping(self, image: Image.Image, crop_type: str) -> Image.Image:
        width, height = image.size
        if crop_type == "square":
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            return image.crop((left, top, left + size, top + size))
        if crop_type == "portrait":
            ratio = 0.75
            new_width = int(height * ratio)
            if new_width < width:
                left = (width - new_width) // 2
                return image.crop((left, 0, left + new_width, height))
        if crop_type == "landscape":
            ratio = 1.33
            new_height = int(width / ratio)
            if new_height < height:
                top = (height - new_height) // 2
                return image.crop((0, top, width, top + new_height))
        return image


class LayoutFormattingAgent:
    """
    LayoutFormattingAgent
    ---------------------
    Responsible for configuring how text is rendered on top of the background
    image. It collaborates with PamphletDesigner but keeps layout decisions
    modular and easy to toggle.
    """

    def __init__(self, designer: Optional[PamphletDesigner] = None) -> None:
        self.designer = designer or PamphletDesigner()

    def render(
        self,
        image_data: bytes,
        text_content: Dict[str, str],
        request: PamphletRequest,
        enable_panel: bool = False,
    ) -> Tuple[bytes, bytes]:
        """
        Apply layout formatting and return:
        - composed pamphlet PNG bytes
        - layout base (textless) PNG bytes

        By default, panels behind text are disabled, per UI requirement.
        """
        # Delegate to designer but ensure we respect the no-panel default by
        # leaving config.show_panel False. If enable_panel is ever True, we
        # could patch the config inside PamphletDesigner to turn panels on.
        return self.designer.create_pamphlet(image_data, text_content, request)


class PamphletReviewAgent:
    """
    PamphletReviewAgent
    -------------------
    Analyzes the final rendered pamphlet output and can make adjustments if
    formatting issues are detected (e.g., overlaps).

    Current implementation is intentionally conservative: it simply tags the
    result with lightweight metadata. This keeps the agent safe and
    side-effect-free while providing a clean extension point.
    """

    def review(
        self,
        pamphlet_bytes: bytes,
        layout_base_bytes: bytes,
        text_content: Dict[str, str],
        request: PamphletRequest,
    ) -> Dict[str, Any]:
        """
        Return a metadata dictionary describing the review outcome.
        In the future this could run OCR or layout detection on the image.
        """
        return {
            "status": "reviewed",
            "issues_detected": False,
            "notes": "PamphletReviewAgent placeholder: no overlaps auto-detected.",
            "headline_preview": text_content.get("headline", "")[:80],
        }

class PamphletAgent:
    """
    Main AI Agent that coordinates all components.

    It composes the following modular agents:
    - TextGenerationAgent
    - ContentEditingAgent
    - LayoutFormattingAgent
    - PamphletReviewAgent

    Each agent can be toggled independently so core functionality remains
    intact even if a particular agent is disabled.
    """
    
    def __init__(
        self,
        stability_api_key: str,
        ollama_model: str = "llama3.2",
        enable_text_generation_agent: bool = True,
        enable_content_editing_agent: bool = True,
        enable_layout_formatting_agent: bool = True,
        enable_review_agent: bool = True,
    ):
        # Core backends
        self.text_backend = OllamaTextGenerator(ollama_model)
        self.image_generator = StableDiffusionGenerator(stability_api_key)
        self.designer = PamphletDesigner()

        # High-level agents
        self.text_agent = TextGenerationAgent(self.text_backend) if enable_text_generation_agent else None
        self.content_editing_agent = ContentEditingAgent() if enable_content_editing_agent else None
        self.layout_agent = LayoutFormattingAgent(self.designer) if enable_layout_formatting_agent else None
        self.review_agent = PamphletReviewAgent() if enable_review_agent else None
    
    def generate_pamphlet(self, request: PamphletRequest) -> Dict[str, any]:
        """
        Generate a complete pamphlet by orchestrating the specialized agents.

        Pipeline:
        1. TextGenerationAgent   → create base content with Ollama.
        2. ContentEditingAgent   → clean up and shorten for layout.
        3. StableDiffusionGenerator → generate background image (Stability AI).
        4. LayoutFormattingAgent → place text cleanly over the image.
        5. PamphletReviewAgent   → validate the final rendering (non-invasive).
        """
        
        print("🤖 AI Agent: Starting pamphlet generation...")
        if request.regeneration_index:
            print(f"♻️ Regeneration iteration detected: #{request.regeneration_index}")
        
        # Step 1: Generate text content (fallback to direct backend if disabled)
        print("📝 Generating text content with TextGenerationAgent/Ollama...")
        if self.text_agent is not None:
            text_content = self.text_agent.generate(request)
        else:
            text_content = self.text_backend.generate_pamphlet_text(request)
        
        # Step 2: Edit content for tone and layout fit
        if self.content_editing_agent is not None:
            print("✏️  Refining content with ContentEditingAgent...")
            text_content = self.content_editing_agent.edit(text_content, request)
        
        # Step 3: Generate background image using Stability AI
        print("🎨 Generating background image with Stable Diffusion...")
        image_data = self.image_generator.generate_pamphlet_image(request, text_content)
        
        if not image_data:
            return {"error": "Failed to generate image"}
        
        # Step 4: Layout formatting and final rendering
        print("🧱 Applying layout with LayoutFormattingAgent...")
        if self.layout_agent is not None:
            pamphlet_data, layout_base = self.layout_agent.render(image_data, text_content, request)
        else:
            pamphlet_data, layout_base = self.designer.create_pamphlet(image_data, text_content, request)
        
        # Step 5: Optional review/validation phase
        review_metadata: Optional[Dict[str, Any]] = None
        if self.review_agent is not None:
            print("🔍 Reviewing final pamphlet with PamphletReviewAgent...")
            review_metadata = self.review_agent.review(
                pamphlet_bytes=pamphlet_data,
                layout_base_bytes=layout_base,
                text_content=text_content,
                request=request,
            )
        
        # Step 6: Save files
        print("💾 Saving pamphlet...")
        filename = f"pamphlet_{request.product_name.replace(' ', '_').lower()}.png"
        with open(filename, 'wb') as f:
            f.write(pamphlet_data)
        
        response: Dict[str, Any] = {
            "success": True,
            "filename": filename,
            "text_content": {
                **text_content,
                "features": request.key_features
            },
            "layout_base_image": base64.b64encode(layout_base).decode("utf-8"),
            "message": "Pamphlet generated successfully!",
        }
        if review_metadata is not None:
            response["review"] = review_metadata
        return response
    
    def edit_pamphlet(self, original_image_data: bytes, edits: Dict, text_content: Optional[Dict[str, str]] = None) -> Optional[bytes]:
        """Edit an existing pamphlet with custom settings"""
        
        print("🎨 Editing pamphlet with custom settings...")
        
        try:
            original_image = Image.open(io.BytesIO(original_image_data)).convert("RGBA")
            features = None
            if text_content and isinstance(text_content, dict):
                features = text_content.get("features") or []
            edited_image, layout_base = self.designer.apply_edits(original_image, edits, text_content, features=features)
            output = io.BytesIO()
            edited_image.save(output, format="PNG", quality=95)
            layout_output = io.BytesIO()
            layout_base.save(layout_output, format="PNG", quality=95)
            return output.getvalue(), layout_output.getvalue()
        except Exception as e:
            print(f"Error editing pamphlet: {e}")
            return None

def main():
    """Example usage"""
    # Replace with your actual API key
    STABILITY_API_KEY = "your_stability_api_key_here"
    
    # Example pamphlet request
    request = PamphletRequest(
        product_name="EcoClean Pro",
        description="Revolutionary eco-friendly cleaning solution that removes 99.9% of bacteria",
        tone="professional",
        target_audience="health-conscious families",
        key_features=[
            "100% biodegradable",
            "No harmful chemicals",
            "Long-lasting formula",
            "Safe for children and pets"
        ],
        call_to_action="Order now and get 20% off your first purchase!",
        color_scheme="modern",
        style="professional"
    )
    
    # Create agent and generate pamphlet
    agent = PamphletAgent(STABILITY_API_KEY)
    result = agent.generate_pamphlet(request)
    
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"📄 Pamphlet saved as: {result['filename']}")
        print(f"📝 Generated content: {result['text_content']}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
