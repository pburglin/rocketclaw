from __future__ import annotations

from dataclasses import dataclass

from rocketclaw.core.context_builder import ContextBuilder
from rocketclaw.engine.model_provider import ModelProvider


@dataclass
class SubAgentResult:
    step: str
    response: str


@dataclass
class SubAgentRunner:
    model: ModelProvider
    context_builder: ContextBuilder

    def run(self, steps: list[str]) -> list[SubAgentResult]:
        results: list[SubAgentResult] = []
        for step in steps:
            slices = self.context_builder.build_for_subagent(step)
            prompt = self.context_builder.debug_view(slices)
            response = self.model.complete(prompt)
            results.append(SubAgentResult(step=step, response=response))
        return results
