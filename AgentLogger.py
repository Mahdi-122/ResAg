from langchain_core.callbacks import BaseCallbackHandler


class AgentLogger(BaseCallbackHandler):

    def __init__(self):
        super().__init__()
        self.steps = []

    def on_chain_start(self, serialized, inputs, **kwargs):
        name = kwargs.get("name") or serialized.get("name", "Unknown")

        self.steps.append({
            "name": name,
            "input": inputs,
            "output": None
        })

    def on_chain_end(self, outputs, **kwargs):
        if self.steps:
            self.steps[-1]["output"] = outputs

    def on_chain_error(self, error, **kwargs):
        if self.steps:
            self.steps[-1]["output"] = f"ERROR: {error}"