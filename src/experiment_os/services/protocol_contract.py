from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProtocolStep:
    id: str
    metric_key: str
    required: bool
    description: str


@dataclass(frozen=True)
class ProtocolDefinition:
    id: str
    version: str
    steps: tuple[ProtocolStep, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "steps": [asdict(step) for step in self.steps],
        }


@dataclass(frozen=True)
class ProtocolComplianceResult:
    protocol_id: str
    condition_count: int
    mean_rate: float | None
    all_required_loaded: bool
    steps: dict[str, float | None]

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["all_pre_work_loaded"] = self.all_required_loaded
        return data


PRE_WORK_PROTOCOL = ProtocolDefinition(
    id="experiment_os.pre_work",
    version="v1",
    steps=(
        ProtocolStep(
            id="pre_work",
            metric_key="mcp_pre_work_protocol_called",
            required=True,
            description="Agent loaded Experiment OS pre-work before editing.",
        ),
        ProtocolStep(
            id="dependency_graph",
            metric_key="mcp_dependency_graph_loaded",
            required=True,
            description="Agent loaded the dependsOn graph before editing.",
        ),
        ProtocolStep(
            id="final_answer",
            metric_key="mcp_final_answer_recorded",
            required=True,
            description="Agent recorded final answer through the run protocol.",
        ),
        ProtocolStep(
            id="summary",
            metric_key="mcp_summary_requested",
            required=False,
            description="Agent requested the compact run summary.",
        ),
    ),
)


class ProtocolComplianceCalculator:
    def __init__(self, protocol: ProtocolDefinition = PRE_WORK_PROTOCOL) -> None:
        self._protocol = protocol

    def condition_compliance(self, metrics: dict[str, dict]) -> dict[str, Any]:
        steps = {
            step.id: _metric_rate(metrics, step.metric_key)
            for step in self._protocol.steps
        }
        required_steps = [step for step in self._protocol.steps if step.required]
        required_rates = [steps[step.id] for step in required_steps]
        return {
            "protocol": self._protocol.as_dict(),
            "steps": steps,
            "pre_work_rate": steps["pre_work"],
            "dependency_graph_rate": steps["dependency_graph"],
            "final_answer_rate": steps["final_answer"],
            "summary_rate": steps["summary"],
            "all_required_loaded": all(rate == 1 for rate in required_rates),
        }

    def overall(self, conditions: dict[str, dict[str, Any]]) -> ProtocolComplianceResult:
        gated = {
            condition: values
            for condition, values in conditions.items()
            if "gated" in condition or condition == "mcp_brief"
        }
        values = gated or conditions
        step_rates: dict[str, float | None] = {}
        for step in self._protocol.steps:
            rates = [
                condition_values.get("steps", {}).get(step.id)
                for condition_values in values.values()
            ]
            numeric_rates = [rate for rate in rates if isinstance(rate, int | float)]
            step_rates[step.id] = (
                sum(numeric_rates) / len(numeric_rates) if numeric_rates else None
            )
        numeric_all = [
            rate for rate in step_rates.values() if isinstance(rate, int | float)
        ]
        required_step_ids = {step.id for step in self._protocol.steps if step.required}
        return ProtocolComplianceResult(
            protocol_id=self._protocol.id,
            condition_count=len(values),
            mean_rate=sum(numeric_all) / len(numeric_all) if numeric_all else None,
            all_required_loaded=all(
                step_rates.get(step_id) == 1 for step_id in required_step_ids
            )
            if values
            else False,
            steps=step_rates,
        )


def _metric_rate(metrics: dict[str, dict], key: str) -> float | None:
    value = metrics.get(key)
    if not isinstance(value, dict):
        return None
    rate = value.get("rate")
    return float(rate) if isinstance(rate, int | float) else None
