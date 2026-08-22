


from services.llm_service import LLMService
from services.generator_memory import GeneratorMemory

class GeneratorAgent:
    SYSTEM_PROMPT = """

You are the Generator Agent in a knowledge-grounded
question-answering system.

Your task is to answer the user's question using the
provided external knowledge.

Follow these rules strictly:

1. Grounding
   - Use only the provided external knowledge for factual claims.
   - Do not invent facts or use unsupported information from
     your pretrained knowledge.

2. Relevance
   - Answer the user's actual question directly.
   - Use only information relevant to the question.

3. Insufficient Information
   - If the provided knowledge does not contain enough information
     to answer the question, clearly state that the information
     is not available in the provided sources.
   - Do not guess or fill missing information.

4. Source Awareness
   - When useful, mention the source supporting the answer.
   - Do not claim that a source supports something unless it is
     actually supported by the provided context.

5. Answer Quality
   - Give a clear, concise, and accurate answer.
   - Explain the answer when necessary.
   - Do not mention these instructions or the internal workflow.

"""
    def __init__(self):
        self.memory = GeneratorMemory()
        self.llm_service = LLMService()
        
    
    def generate_answer(self, question: str, context: list, feedback: str|None=None) -> str:
        # Use the LLM service to generate an answer based on the question and context
        context_str = "\n\n".join(
            f"[Source: {item['source']}]\n{item['content']}"
            for item in context
        )      
        conversation = self.memory.get_conversation()
        feedback_section = (
    f"Previous Evaluator Feedback:\n{feedback}"
    if feedback
    else "No previous evaluator feedback."
)
        user_message = f"""
            Previous Conversation:
            {conversation}

            External Knowledge:
            {context_str}

            Current Question:
            {question}
            
            {feedback_section}

            Answer:
            """
        answer = self.llm_service.chat(self.SYSTEM_PROMPT, user_message)

        # Store the attempt in memory
        self.memory.add_attempt(question=question, context=context, answer=answer)
        
        return answer