import json
from typing import Literal

from pydantic import BaseModel

from services.llm_service import LLMService
from services.evaluator_memory import EvaluatorMemory


class EvaluationResult(BaseModel):
    decision: Literal["accept", "reject"]
    feedback: str

    accuracy: float
    relevance: float
    completeness: float
    grounding: float


class EvaluatorAgent:

    SYSTEM_PROMPT = """
You are the Evaluator Agent in a knowledge-grounded
question-answering system.

Your task is to evaluate the Generator's answer against
the user's question and the provided external knowledge.

Evaluate the answer using the following criteria:

1. Accuracy
   - Are the factual claims in the answer supported by
     the provided external knowledge?
   - Identify factual errors or contradictions.

2. Relevance
   - Does the answer directly address the user's question?
   - Avoid rewarding unrelated information.

3. Completeness
   - Does the answer contain the important information
     needed to answer the question?
   - Identify important missing information when applicable.

4. Grounding
   - Are the answer's claims grounded in the provided
     external knowledge?
   - Unsupported claims should negatively affect the score.

5. Overall Quality
   - Is the answer clear, coherent, and useful?

Decision rules:

- ACCEPT only if the answer actually answers the user's question
  using the provided external knowledge.

- An answer that merely states that information is unavailable
  MUST be rejected when the user asked a factual question.

- Do not consider an answer complete simply because it correctly
  identifies that the context is insufficient.

- If the provided external knowledge is insufficient to answer the
  question, evaluate whether the answer appropriately communicates
  this limitation, but still mark the answer as REJECT because the
  user's question has not been answered.

- REJECT answers that avoid answering the question, even if they
  correctly avoid hallucination.

Important:
- Evaluate the answer ONLY against the provided external
  knowledge and the user's question.
- Do not use your pretrained knowledge to validate claims
  that are not supported by the provided knowledge.
- Do not invent missing information.
- Scores must be between 0.0 and 1.0.

Output Format:

Return ONLY a valid JSON object.

The JSON must contain exactly these fields:

{
    "decision": "accept" or "reject",
    "feedback": "brief actionable feedback, maximum 30 words",
    "accuracy": 0.0,
    "relevance": 0.0,
    "completeness": 0.0,
    "grounding": 0.0
}

All scores must be numbers between 0.0 and 1.0.

Do not include markdown.
Do not include ```json.
Do not include any explanation outside the JSON object.
Return exactly one JSON object.
Keep feedback under 30 words.
Do not generate any text before or after the JSON.
"""

    def __init__(self):
        self.memory = EvaluatorMemory()
        self.llm_service = LLMService()

    def evaluate(
        self,
        question: str,
        context: list,
        answer: str,
    ) -> EvaluationResult:

        context_str = "\n\n".join(
            f"[Source: {item['source']}]\n{item['content']}"
            for item in context
        )

        previous_evaluations = (
            self.memory.get_previous_evaluations()
        )

        user_message = f"""
        /no_think
Previous Evaluations:
{previous_evaluations}

External Knowledge:
{context_str}

User Question:
{question}

Generated Answer:
{answer}

Evaluate the generated answer.
"""

        response = self.llm_service.chat(
            self.SYSTEM_PROMPT,
            user_message
        )
        print("\n=== RAW EVALUATOR RESPONSE ===")
        print(repr(response))

        response = response.strip()

        if not response:
            raise ValueError(
                "Evaluator LLM returned an empty response."
            )

        try:
            evaluation = EvaluationResult.model_validate(
                json.loads(response)
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(
                f"Invalid evaluator response:\n{response}"
            ) from exc

        self.memory.add_evaluation(
            question=question,
            context=context,
            answer=answer,
            decision=evaluation.decision,
            feedback=evaluation.feedback,
            accuracy=evaluation.accuracy,
            relevance=evaluation.relevance,
            completeness=evaluation.completeness,
            grounding=evaluation.grounding,
        )

        return evaluation