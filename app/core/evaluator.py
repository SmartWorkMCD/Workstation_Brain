class RuleEvaluator:
    def evaluate_rule(self, condition: str, state) -> bool:
        try:
            return eval(condition, {}, state.to_dict())
        except Exception as e:
            print(f"Error evaluating rule '{condition}': {e}")
            return False
