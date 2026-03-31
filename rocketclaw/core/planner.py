from dataclasses import dataclass


@dataclass
class Plan:
    steps: list[str]


class Planner:
    def plan(self, goal: str) -> Plan:
        # Simple heuristic: split on " and " / "," / "then"
        separators = [" and ", ",", " then "]
        steps = [goal]
        for sep in separators:
            next_steps: list[str] = []
            for step in steps:
                if sep in step:
                    next_steps.extend([part.strip() for part in step.split(sep) if part.strip()])
                else:
                    next_steps.append(step)
            steps = next_steps
        return Plan(steps=steps)
