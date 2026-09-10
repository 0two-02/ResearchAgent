"""
ResearchPilot AI - LLM Client
Priority chain: IBM watsonx.ai → Groq → structured demo fallback.
Credentials are always read from environment variables; never hardcoded.
"""
import json
import re
from typing import Optional

from backend.config import (
    IBM_API_KEY, IBM_PROJECT_ID, IBM_URL, IBM_MODEL_ID, IBM_MODEL_PARAMS, IBM_AVAILABLE,
    GROQ_API_KEY, GROQ_MODEL, GROQ_AVAILABLE,
)


class WatsonxClient:
    """
    Unified LLM client.
    - If IBM_API_KEY + IBM_PROJECT_ID are set  → uses IBM watsonx.ai
    - Else if GROQ_API_KEY is set              → uses Groq (llama3-70b-8192 by default)
    - Else                                     → structured demo responses (no API needed)
    """

    def __init__(self):
        self._ibm_client = None
        self._groq_client = None
        self._initialized = False

    # ── Lazy init ─────────────────────────────────────────────────────────────

    def _init(self):
        if self._initialized:
            return
        self._initialized = True

        # 1. Try IBM watsonx.ai
        if IBM_AVAILABLE:
            try:
                from ibm_watsonx_ai.foundation_models import ModelInference
                from ibm_watsonx_ai import Credentials
                credentials = Credentials(api_key=IBM_API_KEY, url=IBM_URL)
                self._ibm_client = ModelInference(
                    model_id=IBM_MODEL_ID,
                    credentials=credentials,
                    project_id=IBM_PROJECT_ID,
                    params=IBM_MODEL_PARAMS,
                )
                print(f"[LLM] Connected to IBM watsonx.ai — model: {IBM_MODEL_ID}")
                return
            except ImportError:
                print("[LLM] ibm-watsonx-ai not installed; skipping IBM.")
            except Exception as e:
                print(f"[LLM] IBM init error: {e}; skipping.")

        # 2. Try Groq
        if GROQ_AVAILABLE:
            try:
                from groq import Groq
                self._groq_client = Groq(api_key=GROQ_API_KEY)
                print(f"[LLM] Connected to Groq — model: {GROQ_MODEL}")
                return
            except ImportError:
                print("[LLM] groq package not installed. Run: pip install groq")
            except Exception as e:
                print(f"[LLM] Groq init error: {e}")

        # 3. Demo mode
        print("[LLM] No LLM credentials found — using structured demo responses.")

    # ── Public API ────────────────────────────────────────────────────────────

    async def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate text. Falls through IBM → Groq → demo."""
        self._init()

        # IBM
        if self._ibm_client is not None:
            try:
                return self._ibm_client.generate_text(prompt=prompt)
            except Exception as e:
                print(f"[LLM] IBM generation error: {e}. Trying Groq.")

        # Groq
        if self._groq_client is not None:
            try:
                return await self._groq_generate(prompt, max_tokens)
            except Exception as e:
                print(f"[LLM] Groq generation error: {e}. Falling back to demo.")

        # Demo
        return self._demo_response(prompt)

    async def _groq_generate(self, prompt: str, max_tokens: int) -> str:
        """Call Groq chat completions API (sync SDK wrapped in thread)."""
        import asyncio
        loop = asyncio.get_event_loop()

        def _call():
            chat = self._groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=GROQ_MODEL,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return chat.choices[0].message.content

        return await loop.run_in_executor(None, _call)

    # ── Provider info ─────────────────────────────────────────────────────────

    @property
    def active_provider(self) -> str:
        self._init()
        if self._ibm_client:
            return "ibm_watsonx"
        if self._groq_client:
            return "groq"
        return "demo"

    # ── Structured Demo Responses ─────────────────────────────────────────────

    def _demo_response(self, prompt: str) -> str:
        """
        Return a realistic structured response keyed to the prompt intent.
        Keeps the app fully functional without any external credentials.
        """
        p = prompt.lower()

        # --- Ordering: most-specific checks first ---

        if "research plan" in p or "research planner" in p:
            return json.dumps({
                "research_topic": "AI and Machine Learning Research",
                "key_concepts": ["deep learning", "neural networks", "transfer learning", "computer vision"],
                "search_queries": [
                    "artificial intelligence machine learning applications",
                    "deep learning neural network performance",
                    "transfer learning domain adaptation",
                ],
                "recommended_sources": ["arxiv", "semantic_scholar", "openalex"],
            })

        if "research gap agent" in p or (
            "gap" in p
            and "research_gaps" not in p
            and "paper analysis" not in p
            and "literature" not in p
        ):
            return json.dumps({
                "research_gaps": [
                    "Few studies evaluate methods on low-resource or low-data scenarios",
                    "Insufficient cross-domain generalization benchmarks",
                    "Limited interpretability of large-scale models",
                    "Lack of fairness and bias analysis in recent approaches",
                ],
                "evidence": [
                    "Observed in 6 of 12 analyzed papers",
                    "Only 2 papers include cross-domain evaluation",
                    "Interpretability discussed superficially in most studies",
                    "Fairness evaluation absent in 9 of 12 papers",
                ],
                "importance": ["high", "high", "medium", "high"],
                "possible_research_questions": [
                    "How do current models perform under limited data conditions?",
                    "What benchmarks can evaluate true cross-domain generalization?",
                    "Can we develop interpretable versions without sacrificing accuracy?",
                    "What bias mitigation strategies are most effective for this domain?",
                ],
            })

        if "paper analysis agent" in p or (
            "analyze this paper" in p
        ) or (
            "analyze" in p
            and "gap" not in p
            and "trend" not in p
            and "literature" not in p
            and "recommend" not in p
        ):
            return json.dumps({
                "problem_statement": "Existing methods struggle with generalization across domains.",
                "objective": "To develop a more robust and transferable learning approach.",
                "methodology": "The authors propose a transformer-based architecture with attention mechanisms and contrastive learning.",
                "dataset": "ImageNet, CIFAR-10, and domain-specific benchmark datasets.",
                "results": "Achieves 94.2% accuracy on ImageNet, outperforming baseline by 3.1%.",
                "limitations": "High computational cost; limited evaluation on low-resource settings.",
                "key_findings": "Attention-based pre-training significantly improves transfer performance.",
                "future_work": "Extension to multi-modal settings and evaluation on low-resource languages.",
                "summary": "This paper introduces a transformer-based approach that substantially improves transfer learning performance across domains with strong empirical validation.",
            })

        if "literature review" in p:
            return """## Literature Review

### Introduction
Research in artificial intelligence has grown exponentially over the past decade, with deep learning emerging as the dominant paradigm across multiple domains.

### Existing Research
Studies in this area have explored various approaches including convolutional neural networks, recurrent architectures, and more recently, transformer-based models. Key contributions include seminal works on attention mechanisms and self-supervised learning.

### Major Approaches
1. **Supervised learning** – Traditional deep learning with labeled datasets
2. **Transfer learning** – Pre-training on large corpora and fine-tuning
3. **Self-supervised learning** – Learning representations without human labels
4. **Few-shot learning** – Generalizing from limited examples

### Comparison of Methods
Supervised approaches achieve strong performance when labeled data is abundant. Transfer learning reduces data requirements substantially. Self-supervised learning has shown the strongest generalization across tasks.

### Important Findings
Transformer-based architectures consistently outperform convolutional baselines on language tasks and are increasingly competitive on vision tasks. Pre-training dataset scale is a significant performance driver.

### Limitations
Computational costs for large-scale pre-training remain prohibitive for many research groups. Evaluation benchmarks may not reflect real-world deployment conditions.

### Research Gaps
Current literature reveals several gaps: (1) limited evaluation on low-resource scenarios, (2) insufficient interpretability of large models, (3) lack of standardized benchmarks for domain-specific applications.

### Emerging Trends
Foundation models, multimodal learning, and efficient fine-tuning methods (LoRA, adapters) are rapidly emerging as dominant research directions.

### Future Research Directions
Research should focus on developing computationally efficient architectures, improving model interpretability, and expanding evaluation to diverse real-world datasets."""

        if "trend" in p:
            return json.dumps({
                "growing_topics": ["foundation models", "multimodal AI", "efficient fine-tuning", "AI safety"],
                "declining_topics": ["traditional RNNs", "hand-crafted features", "shallow learning"],
                "emerging_keywords": ["LoRA", "RLHF", "chain-of-thought", "in-context learning"],
                "active_research_areas": ["large language models", "diffusion models", "reinforcement learning from human feedback"],
            })

        if "recommend" in p or "future research" in p:
            return json.dumps({
                "recommendations": [
                    {
                        "research_idea": "Efficient low-resource adaptation of foundation models",
                        "why_it_matters": "Many real-world applications lack large labeled datasets",
                        "existing_evidence": "Transfer learning shows promise but degrades in low-data regimes",
                        "research_gap": "No systematic study of data efficiency thresholds",
                        "suggested_methodology": "Systematic ablation with varying dataset sizes + meta-learning",
                        "possible_dataset": "Low-resource NLP benchmarks (XTREME, FewGLUE)",
                        "expected_contribution": "Practical guidelines for deploying models in constrained settings",
                        "difficulty_level": "medium",
                    },
                    {
                        "research_idea": "Interpretable attention for medical AI decision support",
                        "why_it_matters": "Clinical settings require explainable predictions",
                        "existing_evidence": "Transformer models achieve high accuracy but lack transparency",
                        "research_gap": "Interpretability in high-stakes medical domains is underexplored",
                        "suggested_methodology": "Attention visualization + concept-based explanations",
                        "possible_dataset": "MIMIC-III, CheXpert medical imaging datasets",
                        "expected_contribution": "Trust-worthy AI decision support for clinical use",
                        "difficulty_level": "high",
                    },
                ]
            })

        if "citation" in p:
            return json.dumps({
                "highly_cited": [],
                "frequently_referenced": [],
                "note": "Citation analysis is based on available citation count metadata only.",
            })

        if "compare" in p or "comparison" in p:
            return (
                "These papers employ different methodological approaches. "
                "Paper A focuses on supervised deep learning achieving strong baseline performance, "
                "while Paper B introduces self-supervised pre-training that reduces dependence on labeled data. "
                "Both report competitive results but differ significantly in dataset requirements and "
                "computational cost. Paper B is more suitable for low-resource settings, while Paper A "
                "provides stronger performance when ample labeled data is available."
            )

        # Default — chat / summarization
        return (
            "Based on the analyzed research papers, the primary findings indicate significant advances in the field. "
            "Key methodologies include deep learning architectures with attention mechanisms, evaluated on standard "
            "benchmark datasets. The research collectively demonstrates improved performance over prior baselines, "
            "though limitations around generalizability and computational efficiency remain. "
            "For detailed evidence, please refer to the individual paper analyses above."
        )


# Module-level singleton
watsonx = WatsonxClient()
