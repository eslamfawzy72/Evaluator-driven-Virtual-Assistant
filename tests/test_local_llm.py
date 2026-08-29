from services.local_llm_service import LocalLLMService


def main():
    llm = LocalLLMService()

    response = llm.chat(
        system_message="You are a helpful assistant.",
        user_message="Say hello and tell me that you are running locally.",
    )

    print("\n========== RESPONSE ==========")
    print(response)
    print("===============================")


if __name__ == "__main__":
    main()