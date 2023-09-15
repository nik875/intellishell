import collections
from llm import LLMAgent
from profiler import parse_generation


class PlanningModule:
    def __init__(self, profile):
        self.model = LLMAgent(profile)
        self.plan = collections.deque()
        self.raw_plan = ''

    def next_step(self):
        return self.plan.popleft() if self.plan else None

    def gen_plan(self, feedback=''):
        prompt = f"""
Generate a plan to accomplish your $OBJECTIVE. Consider the following feedback:\n
{feedback if feedback else 'No feedback'}.
If you had a previous plan, prioritize revising it over writing a new one from scratch.
Start with a single-step plan where the only step is the $OBJECTIVE:
        """
        generation = self.model.prompt(prompt)
        for _ in range(7):
            new_generation = self.model.prompt("""
Now determine whether the steps are specific enough. If so, respond with END. If not, rewrite the
plan with one additional step:
            """)
            if 'END' in new_generation:
                break
            generation = new_generation
            print(generation)
            print('-'*20)
        self.raw_plan = parse_generation(generation)['MAIN_CONTENT']
        self.plan = collections.deque()
        for line in self.raw_plan.strip().split('\n'):
            expected_header = f'Step {len(self.plan)+1}: '
            if line.startswith(expected_header):
                self.plan.append(line.lstrip(expected_header))

