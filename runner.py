""" 
This file is the entry point for MLAgentBench.
"""

import argparse
import sys
import datetime
import os
from MLAgentBench import LLM
from MLAgentBench import retrieval
from MLAgentBench.environment import Environment
from MLAgentBench.agents.agent import Agent, SimpleActionAgent, ReasoningActionAgent
from MLAgentBench.agents.dsagent import DSAgent
from MLAgentBench import high_level_actions
from MLAgentBench.high_level_actions import HIGH_LEVEL_ACTIONS
from MLAgentBench.low_level_actions import read_file, write_file, execute_script
from MLAgentBench.schema import ActionInfo, EnvException
from MLAgentBench.LLM import complete_text
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


def main():
    parser = argparse.ArgumentParser(description='Run ML experiments with case-based reasoning')
    parser.add_argument('--problem', type=str, required=True, help='Description of the research problem')
    parser.add_argument('--input', type=str, help='Path to input data file (optional)')
    parser.add_argument('--output', type=str, default='output', help='Path to output directory')
    parser.add_argument('--log', type=str, default='research_log.log', help='Path to research log file')
    parser.add_argument('--log_dir', type=str, default='logs', help='Directory for storing logs')
    parser.add_argument('--work_dir', type=str, default='workspace', help='Working directory for the experiment')
    parser.add_argument('--device', type=str, default='cpu', help='Device to run the experiment on (cpu/cuda)')
    parser.add_argument('--python', type=str, default='python', help='Python interpreter to use')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--resume', type=str, default=None, help='Path to resume from a previous experiment')
    parser.add_argument('--resume_step', type=int, default=0, help='Step number to resume from')
    args = parser.parse_args()

    # Check for Google API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set it using:")
        print("$env:GOOGLE_API_KEY = 'your-api-key'")
        print("You can get an API key from: https://makersuite.google.com/app/apikey")
        print("\nAfter setting the API key, run the command again.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(args.work_dir, exist_ok=True)
    
    # Initialize environment
    env = Environment(args)
    
    # Initialize research log with proper kwargs structure
    write_file(
        file_name=args.log,
        content=f"Research Problem: {args.problem}\n",
        work_dir=args.output,
        trace=env.trace,
        device=args.device,
        python=args.python,
        read_only_files=[args.input] if args.input else []
    )
    
    # Get experiment plan
    experiment_log = read_file(
        file_name=args.log,
        work_dir=args.output,
        trace=env.trace,
        device=args.device,
        python=args.python,
        read_only_files=[args.input] if args.input else []
    )
    
    plan = HIGH_LEVEL_ACTIONS[1].function(
        experiment_log,
        research_problem=args.problem,
        log_file=args.log,
        trace=env.trace,
        device=args.device,
        python=args.python,
        read_only_files=[args.input] if args.input else []
    )
    
    # Execute plan
    execution_log, diff = HIGH_LEVEL_ACTIONS[6].function(
        "experiment.py",
        plan,
        "experiment.py",
        work_dir=args.output,
        research_problem=args.problem,
        log_file=args.log,
        trace=env.trace,
        device=args.device,
        python=args.python,
        read_only_files=[args.input] if args.input else []
    )
    
    # Append execution results to research log
    HIGH_LEVEL_ACTIONS[3].function(
        execution_log,
        work_dir=args.output,
        trace=env.trace,
        device=args.device,
        python=args.python,
        read_only_files=[args.input] if args.input else []
    )
    
    print("Experiment completed. Check the research log for details.")


if __name__ == "__main__":
    main()
    