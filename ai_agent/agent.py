from ai_agent.decision_engine import DecisionEngine
from ai_agent.risk_engine import RiskEngine
from ai_agent.rule_engine import HospitalRuleEngine
from ai_agent.schemas import (
    AgentDecision,
    AppointmentContext,
    Decision,
)


class AppointmentAgent:
    """
    Main orchestration layer for appointment decisions.
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.risk_engine = RiskEngine()
        self.rule_engine = HospitalRuleEngine()
        self.decision_engine = DecisionEngine()

    def evaluate(self, context: AppointmentContext) -> AgentDecision:
        # 1. Calculate risk
        risk_result = self.risk_engine.evaluate(context)

        # 2. Apply hospital rules
        triggered_rules = self.rule_engine.evaluate(
            context,
            risk_result,
        )

        # 3. Make operational decision
        decision = self.decision_engine.decide(
            context,
            risk_result,
            triggered_rules,
        )

        # 4. Determine whether staff intervention is required
        requires_staff = decision == Decision.ESCALATE_TO_STAFF

        # 5. Determine updated appointment status
        if decision == Decision.SEND_REMINDER:
            updated_status = "REMINDER_PENDING"

        elif decision == Decision.OFFER_RESCHEDULE:
            updated_status = "RESCHEDULE_OFFERED"

        elif decision == Decision.ESCALATE_TO_STAFF:
            updated_status = "STAFF_REVIEW"

        else:
            updated_status = "NO_ACTION"

        # 6. Generate explanation
        reasoning = self._build_reasoning(
            risk_result.risk_score,
            risk_result.risk_level.value,
            decision,
            triggered_rules,
        )

        return AgentDecision(
            appointment_id=context.appointment_id,
            decision=decision,
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level,
            reasoning=reasoning,
            risk_factors=risk_result.risk_factors,
            rules_triggered=triggered_rules,
            recommended_slots=context.alternative_slots,
            requires_staff=requires_staff,
            updated_status=updated_status,
            agent_version=self.VERSION,
        )

    def _build_reasoning(
        self,
        risk_score: float,
        risk_level: str,
        decision: Decision,
        triggered_rules,
    ) -> str:
        rule_names = ", ".join(
            rule.rule_id for rule in triggered_rules
        )

        if rule_names:
            rules_text = f"Triggered rules: {rule_names}."
        else:
            rules_text = "No hospital rules were triggered."

        return (
            f"Appointment risk is {risk_level} "
            f"with a score of {risk_score:.1f}/100. "
            f"The selected action is {decision.value}. "
            f"{rules_text}"
        )