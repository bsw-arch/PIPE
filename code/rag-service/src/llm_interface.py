"""
LLM Interface - Llama Model Integration
Handles Llama-2-7B for response generation using Hugging Face
"""

from typing import List, Dict, Any, Optional
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline
)
import logging

logger = logging.getLogger(__name__)


class LlamaInterface:
    """
    Interface for Llama-2-7B model
    Optimised for 48GB RAM with 4-bit quantisation
    """

    def __init__(self,
                 model_name: str = "meta-llama/Llama-2-7b-chat-hf",
                 use_4bit: bool = True,
                 device: str = "auto"):
        """
        Initialise Llama model

        Args:
            model_name: HuggingFace model identifier
            use_4bit: Use 4-bit quantisation (recommended for 48GB RAM)
            device: Device to use ('auto', 'cuda', 'cpu')
        """
        self.model_name = model_name
        self.use_4bit = use_4bit
        self.device = device

        self.model = None
        self.tokenizer = None
        self.pipeline = None

    async def initialise(self):
        """Load and initialise the model"""
        logger.info(f"Loading Llama model: {self.model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        # Configure 4-bit quantisation if enabled
        if self.use_4bit:
            logger.info("Using 4-bit quantisation (saves ~75% memory)")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map=self.device,
                trust_remote_code=True,
            )
        else:
            # Load full precision model (requires more RAM)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map=self.device,
                trust_remote_code=True,
            )

        self.model.eval()

        # Create text generation pipeline
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.float16,
            device_map=self.device,
        )

        logger.info("✓ Llama model loaded successfully")

    async def generate_response(self,
                               query: str,
                               retrieved_knowledge: List[Dict[str, Any]],
                               context: Optional[Dict[str, Any]] = None,
                               max_new_tokens: int = 512,
                               temperature: float = 0.7,
                               top_p: float = 0.9) -> str:
        """
        Generate response using Llama model with retrieved knowledge

        Args:
            query: User query
            retrieved_knowledge: List of retrieved knowledge pieces
            context: Additional context
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            Generated response text
        """
        # Prepare prompt with retrieved knowledge
        prompt = self._build_prompt(query, retrieved_knowledge, context)

        logger.debug(f"Generating response for query: {query[:100]}...")

        try:
            # Generate response
            outputs = self.pipeline(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                repetition_penalty=1.1,
                return_full_text=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

            response = outputs[0]['generated_text'].strip()

            logger.info(f"Generated response ({len(response)} chars)")

            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._fallback_response(query, retrieved_knowledge)

    def _build_prompt(self,
                     query: str,
                     knowledge: List[Dict[str, Any]],
                     context: Optional[Dict] = None) -> str:
        """Build Llama-2-Chat formatted prompt with retrieved knowledge"""

        # Extract knowledge text
        knowledge_text = self._format_knowledge(knowledge)

        # Build system message
        system_msg = (
            "You are a helpful AI assistant with access to a knowledge base. "
            "Use the provided knowledge to answer the user's question accurately. "
            "If the knowledge doesn't contain relevant information, say so honestly."
        )

        # Build user message with knowledge
        user_msg = f"""Based on the following knowledge:

{knowledge_text}

Question: {query}

Please provide a comprehensive answer."""

        # Format as Llama-2-Chat prompt
        prompt = f"""<s>[INST] <<SYS>>
{system_msg}
<</SYS>>

{user_msg} [/INST]"""

        return prompt

    def _format_knowledge(self, knowledge: List[Dict[str, Any]]) -> str:
        """Format retrieved knowledge for prompt"""
        if not knowledge:
            return "No relevant knowledge found."

        formatted_pieces = []

        for idx, item in enumerate(knowledge[:5], 1):  # Top 5 pieces
            # Extract text based on knowledge type
            if 'text' in item:
                text = item['text']
            elif 'entity' in item:
                entity = item['entity']
                text = f"{entity.get('name', '')}: {entity.get('description', '')}"
            elif 'content' in item:
                text = item['content']
            else:
                text = str(item)

            # Clean and truncate
            text = text.strip()[:500]  # Max 500 chars per piece

            formatted_pieces.append(f"[{idx}] {text}")

        return "\n\n".join(formatted_pieces)

    def _fallback_response(self,
                          query: str,
                          knowledge: List[Dict]) -> str:
        """Provide fallback response if generation fails"""
        if not knowledge:
            return (
                "I don't have enough information to answer your question. "
                "Could you please rephrase or provide more context?"
            )

        # Simple knowledge-based response
        knowledge_summary = self._format_knowledge(knowledge)
        return (
            f"Based on the available knowledge:\n\n{knowledge_summary}\n\n"
            f"This information may be relevant to your question: '{query}'"
        )

    async def generate_streaming(self,
                                query: str,
                                knowledge: List[Dict],
                                context: Optional[Dict] = None):
        """
        Generate response with streaming (for real-time display)
        Yields tokens as they are generated
        """
        prompt = self._build_prompt(query, knowledge, context)

        # Tokenize prompt
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        # Generate with streaming
        with torch.no_grad():
            for output in self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                streamer=True,  # Enable streaming
            ):
                # Decode and yield token
                token = self.tokenizer.decode(
                    output,
                    skip_special_tokens=True
                )
                yield token

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and stats"""
        if not self.model:
            return {"status": "not_loaded"}

        return {
            "model_name": self.model_name,
            "quantisation": "4-bit" if self.use_4bit else "16-bit",
            "device": str(self.model.device),
            "dtype": str(self.model.dtype),
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "memory_footprint_mb": self.model.get_memory_footprint() / 1024 / 1024
        }
