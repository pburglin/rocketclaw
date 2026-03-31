from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from rocketclaw.core.context_builder import ContextBuilder
from rocketclaw.core.planner import Planner
from rocketclaw.engine.model_provider import ModelProvider
from rocketclaw.engine.sub_agents import SubAgentRunner
from rocketclaw.tools.tool_registry import ToolRegistry
from rocketclaw.transports.base import MessageEnvelope, OutboundMessage


@dataclass
class AgentRuntime:
    model: ModelProvider
    tools: ToolRegistry
    context_builder: ContextBuilder = field(default_factory=ContextBuilder)
    planner: Planner = field(default_factory=Planner)

    def handle(self, envelope: MessageEnvelope) -> OutboundMessage:
        plan = self.planner.plan(envelope.text)
        if len(plan.steps) > 1:
            runner = SubAgentRunner(model=self.model, context_builder=self.context_builder)
            results = runner.run(plan.steps)
            combined = "\n\n".join([f"Step: {r.step}\n{r.response}" for r in results])
            self._record_episode(envelope, combined)
            return OutboundMessage(text=combined, session=envelope.session)

        context = self.context_builder.build(envelope.text, semantic_query=envelope.text)
        prompt = self.context_builder.debug_view(context)
        response_text = self.model.complete(prompt)
        self._record_episode(envelope, response_text)
        return OutboundMessage(text=response_text, session=envelope.session)

    def _record_episode(self, envelope: MessageEnvelope, response_text: str) -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        entry = (
            f"- {timestamp} user: {envelope.text}\n"
            f"- {timestamp} assistant: {response_text}\n"
        )
        filename = f"{datetime.now().strftime('%Y-%m-%d')}.md"
        self.context_builder.memory.append("episodic", filename, entry)


def run_loop(
    receive: Callable[[], MessageEnvelope | None],
    send: Callable[[OutboundMessage], None],
    runtime: AgentRuntime,
) -> None:
    while True:
        envelope = receive()
        if envelope is None:
            break
        reply = runtime.handle(envelope)
        send(reply)
