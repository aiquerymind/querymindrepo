""" 
This file is the entry point for MLAgentBench.
"""

import argparse
import sys
import datetime
from MLAgentBench import LLM
from MLAgentBench.environment import Environment
from MLAgentBench.agents.agent import Agent, SimpleActionAgent, ReasoningActionAgent
# from MLAgentBench.agents.agent_research import ResearchAgent  # Removed for deployment
from MLAgentBench.agents.agent_langchain  import LangChainAgent
try:
    from MLAgentBench.agents.agent_autogpt  import AutoGPTAgent
except:
    print("Failed to import AutoGPTAgent; Make sure you have installed the autogpt dependencies if you want to use it.")


def run(agent_cls, args):
    with Environment(args) as env:

        print("=====================================")
        research_problem, benchmark_folder_name = env.get_task_description()
        print("Benchmark folder name: ", benchmark_folder_name)
        print("Research problem: ", research_problem)
        print("Lower level actions enabled: ", [action.name for action in env.low_level_actions])
        print("High level actions enabled: ", [action.name for action in env.high_level_actions])
        print("Read only files: ", env.read_only_files, file=sys.stderr)
        print("=====================================")  

        agent = agent_cls(args, env)
        final_message = agent.run(env)
        print("=====================================")
        print("Final message: ", final_message)

    env.save("final")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="feedback", help="task name")
    parser.add_argument("--log-dir", type=str, default="./logs", help="log dir")
    parser.add_argument("--work-dir", type=str, default="./workspace", help="work dir")
    parser.add_argument("--max-steps", type=int, default=30, help="number of steps")
    parser.add_argument("--max-time", type=int, default=5* 60 * 60, help="max time")
    parser.add_argument("--device", type=int, default=0, help="device id")
    parser.add_argument("--python", type=str, default="python", help="python command")
    parser.add_argument("--interactive", action="store_true", help="interactive mode")
    parser.add_argument("--resume", type=str, default=None, help="resume from a previous run")
    parser.add_argument("--resume-step", type=int, default=0, help="the step to resume from")

    # general agent configs
    parser.add_argument("--agent-type", type=str, help="agent type")
    parser.add_argument("--llm-name", type=str, default="gpt-4", help="llm name")
    parser.add_argument("--fast-llm-name", type=str, default="gpt-3.5-turbo", help="llm name")
    parser.add_argument("--edit-script-llm-name", type=str, default="gpt-4", help="llm name")
    parser.add_argument("--edit-script-llm-max-tokens", type=int, default=4000, help="llm max tokens")
    parser.add_argument("--agent-max-steps", type=int, default=50, help="max iterations for agent")

    # research agent configs
    parser.add_argument("--actions-remove-from-prompt", type=str, nargs='+', default=["Edit Script and Execute (AI)"])
    parser.add_argument("--actions-add-to-prompt", type=str, nargs='+', default=[], help="actions to add")
    parser.add_argument("--no-retrieval", action="store_true", help="disable retrieval")
    parser.add_argument("--valid-format-entires", type=str, nargs='+', default=None, help="valid format entries")
    parser.add_argument("--max-steps-in-context", type=int, default=3, help="max steps in context")
    parser.add_argument("--max-observation-steps-in-context", type=int, default=3, help="max observation steps in context")
    parser.add_argument("--max-retries", type=int, default=5, help="max retries")

    # langchain configs
    parser.add_argument("--langchain-agent", type=str, default="zero-shot-react-description", help="langchain agent")


    args = parser.parse_args()
    args.log_dir = args.log_dir + f"/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    args.work_dir = args.work_dir + f"/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    print(args, file=sys.stderr)
    LLM.FAST_MODEL = args.fast_llm_name
    run(getattr(sys.modules[__name__], args.agent_type), args)
    