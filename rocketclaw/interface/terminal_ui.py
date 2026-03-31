from prompt_toolkit import PromptSession


class TerminalUI:
    def __init__(self) -> None:
        self.session = PromptSession()

    def prompt(self, text: str = "> ") -> str:
        return self.session.prompt(text)

    def print(self, text: str) -> None:
        print(text)
