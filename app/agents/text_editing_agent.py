import os
from app.services.llm_provider import LLMProvider

class TextToTextAgent:
    _handlers = {}

    def __init__(self, platform):
        """
        platform: str
            Identifier for the LLM platform to use in LLMProvider (e.g., "openai", "anthropic")
        """
        self.platform = platform
        self.llm = LLMProvider(platform)

    @classmethod
    def register(cls, intent):
        """
        Decorator to register prompt generator functions by intent.
        """
        def wrapper(func):
            cls._handlers[intent] = func
            return func
        return wrapper

    def generate_prompt(self, intent, input_text, **kwargs):
        """
        Generates the prompt text for the given intent using registered handler.
        """
        if intent not in self._handlers:
            raise ValueError(f"Unsupported intent: {intent}")
        return self._handlers[intent](input_text, **kwargs)

    def run(self, intent, input_text, **kwargs):
        """
        Executes the agent: generates prompt and sends to LLMProvider,
        returning the LLM response.
        """
        system_prompt = "You are a helpful text transformation assistant."
        prompt = self.generate_prompt(intent, input_text, **kwargs)
        response = self.llm.generate_response(system_prompt, prompt)
        return response

    @classmethod
    def supported_intents(cls):
        """
        Returns a list of supported intent keys.
        """
        return list(cls._handlers.keys())


# === Intent Handlers ===

@TextToTextAgent.register("summarize")
def summarize(text, **_):
    return f"Summarize this:\n\n{text}"

@TextToTextAgent.register("rewrite")
def rewrite(text, **kwargs):
    tone = kwargs.get("tone", "neutral")
    return f"Rewrite this in a {tone} tone:\n\n{text}"

@TextToTextAgent.register("translate")
def translate(text, **kwargs):
    target_lang = kwargs.get("target_language", "English")
    return f"Translate into {target_lang}:\n\n{text}"

@TextToTextAgent.register("correct_grammar")
def correct_grammar(text, **_):
    return f"Fix grammar, spelling, and punctuation:\n\n{text}"

@TextToTextAgent.register("simplify")
def simplify(text, **_):
    return f"Simplify for a young reader:\n\n{text}"

@TextToTextAgent.register("expand")
def expand(text, **_):
    return f"Expand this idea:\n\n{text}"

@TextToTextAgent.register("style")
def style(text, **kwargs):
    style_type = kwargs.get("style", "professional")
    return f"Rewrite in a {style_type} style:\n\n{text}"

@TextToTextAgent.register("generate_questions")
def generate_questions(text, **_):
    return f"Generate 3 questions from:\n\n{text}"

@TextToTextAgent.register("answer_question")
def answer_question(text, **kwargs):
    question = kwargs.get("question", "")
    return f"Answer this question using the context:\nContext: {text}\nQuestion: {question}"


# if __name__ == "__main__":
#     agent = TextToTextAgent("chatgpt")
#     result = agent.run("summarize", "Artificial Intelligence is a branch of computer science that aims to create intelligent machines.")
#     print("Output:\n", result)
