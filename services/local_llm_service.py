from transformers import AutoModelForCausalLM, AutoTokenizer


class LocalLLMService:

    MODEL_PATH = (
        r"D:\D\huggingface_cache\hub\models--Qwen--Qwen2.5-3B-Instruct\snapshots\aa8e72537993ba99e69dfaafa59ed015b17504d1"
    )

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_PATH,
            local_files_only=True,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_PATH,
            local_files_only=True,
        )

    def chat(self, system_message: str, user_message: str) -> str:
        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
        )

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,
        )

        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

        return self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        )