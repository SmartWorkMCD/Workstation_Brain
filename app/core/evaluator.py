import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RuleEvaluator:
    def evaluate_rule(self, condition: str, state) -> bool:
        try:
            return eval(condition, {}, state.to_dict())
        except Exception as e:
            logger.info(f"Error evaluating rule '{condition}': {e}")
            return False
