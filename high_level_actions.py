""" This file contains high level actions that may contain multiple low level actions and LLM calls. """

import os
import datetime
import shutil
import difflib
import tiktoken
from .low_level_actions import read_file, write_file, append_file, execute_script
from .schema import ActionInfo, EnvException
from .LLM import complete_text_fast, complete_text
from .retrieval import RetrievalDatabase

def reflection(things_to_reflect_on, work_dir = ".", research_problem = "", **kwargs):

    research_log_content = read_file("research_log.log", work_dir = work_dir,  **kwargs)

    prompt = f"""We are trying to solve this research problem: {research_problem}
    Your current research log:
    ```
    {research_log_content}
    ```
    Reflect on this: {things_to_reflect_on} 
    Give an answer in natural language paragraphs as truthfully as possible. 
    """
    reflection = complete_text_fast(prompt, log_file=kwargs["log_file"])
    return f"Reflection: {reflection}\n"

def plan_experiment_design_cbr(experiment_log, **kwargs):
    research_problem = kwargs["research_problem"]
    retrieval_database = RetrievalDatabase([
           "../data/nlp_cases",
           "../data/tsa_cases",
           "../data/tabular_cases",
        ],
        model="BAAI/llm-embedder",
    )
    query = f"""{research_problem}{experiment_log}"""
    
    try:
        case_prompt = retrieval_database.retrieve_then_rerank(query, research_problem, experiment_log, topk=5, log_file=kwargs["log_file"])
    except Exception as e:
        print(f"Warning: Case retrieval failed: {str(e)}")
        case_prompt = "No relevant cases found. Please proceed with basic implementation."
    
    prompt = f"""You are a helpful AI expert assistant, responsible for decision making on the experiment plans. You have the following information including, research problem, research log, and a relevant case so far. 
The research problem is: 
``` Research Problem:
{research_problem}
```
The current research log is:
``` Current Research Log:
{experiment_log}
```
Here is a past experience case written by an human expert for a relevant (but not the same) research problem:
``` Case:
{case_prompt}
```
Follow these instructions and do not forget them:
- Incrementally introduce new techniques in your plans to solve the research problem, since the programmer who follows your decision cannot handle too many instructions at one time.
- Focus on decision making of next single step of experiment. Do not include plans in [Decision] that requires mutiple experiment trials.
- Make sure [Decision] includes all the key points for next step experiment.
- Highlight the supporting experiment results and reasoning before drawing any conclusions.
Make sure that the following prohibitions are not violated:
- Never perform any visualization analysis, since you do not have the ability to view the figures. 
- Never change the way of the dataset split in any way during the experiment.
- Never introduce any new features, unless you have enough knowledge of the features and their meanings.
- Never tune more than two hyper-parameters in one experiment step, since this will lead to computation costs.
- Never introduce any technique for distributed training. We only have one single GPU card.

Please carefully reason over this relevant case and the provided research problem, and then response exactly in the following format:
[Reflection]: What is the progress of the experiment for this research problem? What does the current research log reveal?
[Reasoning]: How can the current research problem benefit from the relevant case?
[Thought]: To solve this research problem and iteratively improve the performance, what is the plans for next experiment trial?
[Check]: List all plans in [Thought] and carefully check (1) whether the plan needs multiple experiment trials; (2) violates the listed prohibitions above.
[Decision]: Give a short, precise but detailed instruction summary on the final experiment plan in next single trial.
"""
    print("\nSending prompt to model:")
    print("="*80)
    print(prompt)
    print("="*80)
    
    try:
        design = complete_text(prompt, log_file=kwargs["log_file"], model=EDIT_SCRIPT_MODEL)
        print("\nReceived response from model:")
        print("="*80)
        print(design)
        print("="*80)
        
        if design and '[Decision]:' in design:
            return f"{design.split('[Decision]:')[1].strip()}\n"
        else:
            print("Warning: Model response did not contain expected format. Using default plan.")
            return "Proceed with basic implementation: Load the data, perform basic preprocessing, and train a simple model to establish a baseline."
    except Exception as e:
        print(f"Warning: Model completion failed: {str(e)}")
        return "Proceed with basic implementation: Load the data, perform basic preprocessing, and train a simple model to establish a baseline."

def understand_file(file_name, things_to_look_for, work_dir = ".", **kwargs):

    lines = read_file(file_name, work_dir = work_dir, **kwargs).split("\n")
    # group lines to blocks so that each block has at most 10000 characters
    counter = 0
    blocks = []
    while counter < len(lines):
        block = []
        start_line_number = counter + 1
        while counter < len(lines) and len("\n".join(block)) + len(lines[counter]) < 10000:
            block.append(lines[counter])
            counter += 1
        if len(block) > 0:
            end_line_number = counter 
            blocks.append(("\n".join(block), start_line_number, end_line_number))
        else:
            end_line_number = start_line_number
            # probably a file of one/few very long line; split by 10000 characters
            for i in range(0, len(lines[counter]), 10000):
                blocks.append((lines[counter][i:i+10000], start_line_number, end_line_number))
            counter += 1

    descriptions  = []
    for idx, (b, start_line_number, end_line_number) in enumerate(blocks):
        start_char_number = sum([len(b) for b in blocks[:idx]])
        end_char_number = start_line_number + len(b)
        prompt = f"""Given this (partial) file from line {start_line_number} character {start_char_number} to line {end_line_number} character {end_char_number}: 
    ``` 
    {b}
    ```
    Here is a detailed description on what to look for and what should returned: {things_to_look_for}
    The description should short and also reference crtical lines in the script relevant to what is being looked for. Only describe what is objectively confirmed by the file content. Do not include guessed numbers. If you cannot find the answer to certain parts of the request, you should say "In this segment, I cannot find ...".
    """

        completion = complete_text_fast(prompt, log_file=kwargs["log_file"]+f"_{idx}")
        descriptions.append(completion)
    if len(descriptions) == 1:
        return descriptions[0]
    else:
        descriptions = "\n\n".join(["Segment {idx}: \n\n" + s for s in descriptions])
        prompt = f"""Given the relevant observations for each segments of a file, summarize to get a cohesive description of the entire file on what to look for and what should returned: {things_to_look_for}
    {descriptions}
    """

        completion = complete_text_fast(prompt, log_file=kwargs["log_file"])

        return completion

def summary_progress(file_name, work_dir=".", **kwargs):

    lines = read_file(file_name, work_dir=work_dir, **kwargs).split("\n")
    # group lines to blocks so that each block has at most 10000 characters
    counter = 0
    blocks = []
    while counter < len(lines):
        block = []
        start_line_number = counter + 1
        while counter < len(lines) and len("\n".join(block)) + len(lines[counter]) < 10000:
            block.append(lines[counter])
            counter += 1
        if len(block) > 0:
            end_line_number = counter 
            blocks.append(("\n".join(block), start_line_number, end_line_number))
        else:
            end_line_number = start_line_number
            # probably a file of one/few very long line; split by 10000 characters
            for i in range(0, len(lines[counter]), 10000):
                blocks.append((lines[counter][i:i+10000], start_line_number, end_line_number))
            counter += 1

    descriptions  = []
    for idx, (b, start_line_number, end_line_number) in enumerate(blocks):
        start_char_number = sum([len(b) for b in blocks[:idx]])
        end_char_number = start_line_number + len(b)
        prompt = f"""Given this (partial) file from line {start_line_number} character {start_char_number} to line {end_line_number} character {end_char_number}: 
    ``` 
    {b}
    ```
    Based on this file, please give a summary on the current progress on this research problem: 
    ```
    {kwargs["research_problem"]}
    ```
    The description should short and also reference crtical lines in the script relevant to what is being looked for. Only describe what is objectively confirmed by the file content. Do not include guessed numbers. If you cannot find the answer to certain parts of the request, you should say "In this segment, I cannot find ...".
    """

        completion = complete_text_fast(prompt, log_file=kwargs["log_file"]+f"_{idx}")
        descriptions.append(completion)
    if len(descriptions) == 1:
        return descriptions[0]
    else:
        descriptions = "\n\n".join(["Segment {idx}: \n\n" + s for s in descriptions])
        prompt = f"""Given the relevant observations for each segments of a file, please give a summary on the current progress on this research problem: {kwargs['research_problem']}
    {descriptions}
    """

        completion = complete_text_fast(prompt, log_file=kwargs["log_file"])

        return completion


EDIT_SCRIPT_MODEL = "models/gemini-2.0-flash"
EDIT_SCRIPT_MAX_TOKENS = 4000
def edit_script(script_name, edit_instruction, save_name, work_dir = ".", **kwargs):
    #TODO: handle long file editing
    try:
        content = read_file(script_name, work_dir = work_dir, **kwargs)
    except:
        write_file(script_name, "", work_dir = work_dir, **kwargs)
        content = ""
        
    prompt = f"""Given this python script:
    ```python 
    {content}
    ```
    Edit the script by following the instruction:
    {edit_instruction}
    Note that you should provide and only provide the **full** code after the edit, making no other changes. Start the python code with "```python". Please ensure the completeness of the codes so that it can be run without additional modifications.
    Your codes will be executed with the support of a NVIDIA GPU card with 24 GB memory.
    """
    ##### Edit the prompt to make sure the coding completeness

    completion = complete_text(prompt, log_file=kwargs["log_file"], model=EDIT_SCRIPT_MODEL, max_tokens=EDIT_SCRIPT_MAX_TOKENS)

    new_content = completion.split("```python")[1].split("```")[0].strip()

    # backup all old file with prefix script_name
    backup_name = os.path.join(work_dir,"backup", f"{script_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    shutil.copyfile(os.path.join(work_dir,script_name), backup_name)

    write_file(save_name, new_content, work_dir = work_dir, **kwargs)

    diff = list(difflib.unified_diff(content.splitlines(keepends=True), new_content.splitlines(keepends=True)))
    diff = "".join(diff)

    return f"The edited file is saved to {save_name}. Here is the diff, please check if the edit is correct and desirable:\n\n" + diff

def execute(script_name, plan, save_name, work_dir = ".", **kwargs):
    """
    In DS-Agent, we execute the experiment plan via cooperation between Programmer and Debugger.
    """
    max_iteration = 5
    
    # Create a unique experiment folder with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    experiment_dir = os.path.join(work_dir, "output", f"experiment_{timestamp}")
    os.makedirs(experiment_dir, exist_ok=True)
    
    # Create project structure
    project_structure = {
        'src': os.path.join(experiment_dir, 'src'),  # Source code
        'data': os.path.join(experiment_dir, 'data'),  # Data files
        'models': os.path.join(experiment_dir, 'models'),  # Saved models
        'results': os.path.join(experiment_dir, 'results'),  # Results and outputs
        'logs': os.path.join(experiment_dir, 'logs'),  # Log files
        'backup': os.path.join(experiment_dir, 'backup')  # Backup files
    }
    
    # Create all directories
    for dir_path in project_structure.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # Handle input data if provided
    if 'input' in kwargs and kwargs['input']:
        input_file = kwargs['input']
        if os.path.exists(input_file):
            # Copy input file to data directory
            input_filename = os.path.basename(input_file)
            data_path = os.path.join(project_structure['data'], input_filename)
            try:
                shutil.copy2(input_file, data_path)
                print(f"Copied input file to: {data_path}")
                # Update input path in kwargs to be relative to experiment directory
                kwargs['input'] = os.path.join('data', input_filename)
            except Exception as e:
                print(f"Warning: Could not copy input file: {str(e)}")
        else:
            print(f"Warning: Input file not found: {input_file}")
    
    # Update save_name to be in the src directory
    save_name = os.path.join('src', os.path.basename(save_name))
    
    # Edge case: there is no file.
    try:
        content = read_file(script_name, work_dir = work_dir, **kwargs)
    except:
        write_file(script_name, "", work_dir = work_dir, **kwargs)
        content = ""
    
    # Loop
    iteration = 0
    last_content = ""
    observation = ""
    while iteration < max_iteration:
        if iteration == 0:
            # Here is the Programmer.
            prompt = f"""You are a helpful AI-oriented programming expert. Now, we are solving a machine learning task. Given this python script:
```python 
{content}
```
Now please edit this script according to the following instructions:
```instruction
{plan}
```
Note that you should provide the **full** code after the edit, making no other changes. Please ensure the completeness of the codes so that it can be run without additional modifications. Your codes will be executed with the support of a NVIDIA GPU card with 24 GB memory. 

For large projects, you can split the code into multiple files. If you need to create additional files, specify them in your response using the following format:
```python:src/filename.py
# Code for filename.py
```

Your response must start with ```python and end with ```. Do not include any other text or explanations.
"""
        else:
            # Here is the Debugger.
            prompt = f"""You are a helpful AI-oriented programming expert. Now, we are solving a machine learning task. Given this original python script:
```python 
{content}
```
The instruction for modification is:
```instruction
{plan}
```
This is the current python code:
```python
{last_content}
```
However, there are some bugs in this version. Here is the execution log:
```log
{observation}
```
Please revise the script to fix these bugs. Note that you should provide the **full** code after the edit, making no other changes. Please ensure the completeness of the codes so that it can be run without additional modifications. Your codes will be executed with the support of a NVIDIA GPU card with 24 GB memory. 

For large projects, you can split the code into multiple files. If you need to create additional files, specify them in your response using the following format:
```python:src/filename.py
# Code for filename.py
```

Your response must start with ```python and end with ```. Do not include any other text or explanations.
"""
        max_retry = 0
        while max_retry < 5:
            max_retry += 1
            try:
                completion = complete_text(prompt, log_file=kwargs["log_file"], model=EDIT_SCRIPT_MODEL, max_tokens=EDIT_SCRIPT_MAX_TOKENS)
                
                # Handle multiple files in the response
                files_to_write = {}
                current_file = None
                current_content = []
                
                for line in completion.split('\n'):
                    if line.startswith('```python:'):
                        if current_file and current_content:
                            files_to_write[current_file] = '\n'.join(current_content)
                        current_file = line.split(':', 1)[1].strip()
                        current_content = []
                    elif line.startswith('```python'):
                        if current_file and current_content:
                            files_to_write[current_file] = '\n'.join(current_content)
                        current_file = save_name
                        current_content = []
                    elif line.startswith('```'):
                        if current_file and current_content:
                            files_to_write[current_file] = '\n'.join(current_content)
                        current_file = None
                        current_content = []
                    elif current_file is not None:
                        current_content.append(line)
                
                if not files_to_write:
                    print("Warning: No valid Python code found in response")
                    if max_retry == 5:
                        execution_log = f"The instruction cannot be perfectly performed by another Python programming Agent in {max_retry} times. Please give a more simplified and feasible instruction and retry."
                        return execution_log, None
                    continue
                
                # Write all files
                for file_path, content in files_to_write.items():
                    print(f"\nWriting code to {file_path}")
                    write_file(file_path, content, work_dir=experiment_dir, **kwargs)
                
                new_content = files_to_write.get(save_name, "")
                break
                
            except Exception as e:
                print(f"Error in model completion: {str(e)}")
                if max_retry == 5:
                    execution_log = f"The instruction cannot be perfectly performed by another Python programming Agent in {max_retry} times. Please give a more simplified and feasible instruction and retry."
                    return execution_log, None
                continue
    
        # backup all old files
        for file_path in files_to_write.keys():
            backup_name = os.path.join('backup', f"{os.path.basename(file_path)}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
            try:
                shutil.copyfile(os.path.join(experiment_dir, file_path), os.path.join(experiment_dir, backup_name))
            except Exception as e:
                print(f"Warning: Could not create backup for {file_path}: {str(e)}")
        
        # Execute the main script
        try:
            observation = execute_script(save_name, work_dir=experiment_dir, **kwargs)
            ## If observation is too long, we only keep the last ~2k tokens.
            enc = tiktoken.get_encoding("cl100k_base")
            tokens = len(enc.encode(observation))
            while tokens >= 2000:
                observation = observation[2000:]
                tokens = len(enc.encode(observation))
        except Exception as e:
            print(f"Error executing script: {str(e)}")
            observation = f"Error: {str(e)}"
        
        # If the script has been successfully executed: Exit.
        if "Traceback (most recent call last):" not in observation and "SyntaxError: invalid syntax" not in observation:
            execution_log = "The instructions have been performed. Here is the result log:\n" + observation
            diff = list(difflib.unified_diff(content.splitlines(keepends=True), new_content.splitlines(keepends=True)))
            diff = "".join(diff)
            return execution_log, diff
        # Else: Go to the Debugger.
        last_content = new_content
        iteration += 1
    print("="*10 + f"Iteration: {iteration}")
    write_file(save_name, content, work_dir=experiment_dir, **kwargs)
    execution_log = f"The instruction cannot be perfectly performed by another Python programming Agent in {iteration} times. Please give a more simplified and feasible instruction and retry."
    return execution_log, None

def append_to_research_log( content, work_dir = ".", **kwargs):
    append_file("research_log.log", content+"\n", work_dir = work_dir, **kwargs)

    return "Successfully appended to research log"

def edit_script_lines( script_name, start_line_number, end_line_number,edit_instruction, save_name, work_dir = ".", **kwargs):
    try:
        start_line_number = int(start_line_number)
        end_line_number = int(end_line_number)
    except:
        raise EnvException("start_line_number and end_line_number must be integers")
    
    try:
        orig_content = read_file(script_name, work_dir = work_dir, **kwargs)
    except:
        write_file(script_name, "", work_dir = work_dir, **kwargs)
        orig_content = ""
    lines = orig_content.split("\n")
    content = "\n".join(lines[max(int(start_line_number)-1, 0):int(end_line_number)])
        
    prompt = f"""Given this segment of a python script:
    ```python 
    {content}
    ```
    Edit this segemnt by following the instruction:
    {edit_instruction}
    Provide the full code after the edit, making no other changes. Start the python code with "```python". 

    """

    completion = complete_text(prompt, log_file=kwargs["log_file"], model=EDIT_SCRIPT_MODEL, max_tokens=EDIT_SCRIPT_MAX_TOKENS)

    new_content = "\n".join(lines[:int(start_line_number)-1]) + "\n" + completion.split("```python")[1].split("```")[0].strip() + "\n" + "\n".join(lines[int(end_line_number):])

    # backup all old file with prefix script_name
    backup_name = os.path.join(work_dir,"backup", f"{script_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    shutil.copyfile(os.path.join(work_dir,script_name), backup_name)

    write_file(save_name, new_content, work_dir = work_dir, **kwargs)

    diff = list(difflib.unified_diff(content.splitlines(keepends=True), new_content.splitlines(keepends=True)))
    diff = "".join(diff)

    return f"The edited file is saved to {save_name}. Here is the diff, please check if the edit is correct and desirable:\n\n" + diff


def inspect_script_lines( script_name, start_line_number, end_line_number, work_dir = ".", **kwargs):
    try:
        start_line_number = int(start_line_number)
        end_line_number = int(end_line_number)
    except:
        raise EnvException("start_line_number and end_line_number must be integers")
    if end_line_number - start_line_number > 100:
        raise EnvException("the number of lines to display is limited to 100 lines")
    try:
        
        # lines = open(os.path.join(work_dir,script_name)).readlines()
        lines = read_file(script_name, work_dir = work_dir, **kwargs).split("\n")
    except:
        raise EnvException(f"cannot find script {script_name}")

    content = "\n".join(lines[max(int(start_line_number)-1, 0):int(end_line_number)])
    return f"Here are the lines (the file ends at line {len(lines)}):\n\n" + content

def retrieval_from_research_log(current_plan, work_dir = ".", **kwargs):

    research_problem = kwargs["research_problem"]

    research_log_content = read_file("research_log.log", work_dir = work_dir, **kwargs)
    
    prompt = f"""We are trying to solve this research problem: {research_problem}
Your current Research Plan and Status
{current_plan}
    
Your current research log:
```
{research_log_content}
```
Concisely summarize and list all relevant information from the research log that will be helpful for future step in this format:
"""

    retrieval = complete_text_fast(prompt, log_file=kwargs["log_file"])

    return retrieval


HIGH_LEVEL_ACTIONS = [
    ActionInfo(
        name="Summary Progress",
        description="Use this to read the whole file and understand certain aspects. You should provide detailed description on what to look for and what should be returned. To get a better understanding of the file, you can use Inspect Script Lines action to inspect specific part of the file.",
        usage={
            "file_name": "a valid file name with relative path to current directory if needed",
        },
        return_value="The observation will be a description of relevant content and lines in the file. If the file does not exist, the observation will be an error message.",
        function=summary_progress
    ),
    ActionInfo(
        name="Develop An Experiment Plan via CBR",
        description="N/A",
        usage={
            "experiment_log": "N/A"
        },
        return_value="N/A",
        function=plan_experiment_design_cbr
    ),
    ActionInfo(
        name="Understand File",
        description="Use this to read the whole file and understand certain aspects. You should provide detailed description on what to look for and what should be returned. To get a better understanding of the file, you can use Inspect Script Lines action to inspect specific part of the file.",
        usage={
            "file_name": "a valid file name with relative path to current directory if needed",
            "things_to_look_for": "a detailed description on what to look for and what should returned"
        },
        return_value="The observation will be a description of relevant content and lines in the file. If the file does not exist, the observation will be an error message.",
        function=understand_file
    ),
    ActionInfo(
        name="Append Summary to Research Log",
        description="Append to the summary of previous step to research log",
        usage={
            "content": "a string within 500 character limit"
        },
        return_value="The observation will be a success message if the content is appended to the research log. Otherwise, the observation will be an error message.",
        function=append_to_research_log
    ),
    ActionInfo(
        name="Inspect Script Lines",
        description="Use this to inspect specific part of a python script precisely, or the full content of a short script. The number of lines to display is limited to 100 lines. This is especially helpful when debugging.",
        usage={
            "script_name": "a valid python script name with relative path to current directory if needed",
            "start_line_number": "a valid line number",
            "end_line_number": "a valid line number"
        },
        return_value="The observation will be the content of the script between start_line_number and end_line_number . If the script does not exist, the observation will be an error message.",
        function=inspect_script_lines
    ),
    ActionInfo(
        name="Edit Script (AI)",
        description="Use this to do a relatively large but cohesive edit over a python script. Instead of editing the script directly, you should describe the edit instruction so that another AI can help you do this.",
        usage={
            "script_name": "a valid python script name with relative path to current directory if needed. An empty script will be created if it does not exist.",
            "edit_instruction": "a detailed step by step description on how to edit it.",
            "save_name": "a valid file name with relative path to current directory if needed"
        },
        return_value="The observation will be the edited content of the script. If the script does not exist, the observation will be an error message. You should always double check whether the edit is correct. If it is far from correct, you can use the Undo Edit Script action to undo the edit.",
        function=edit_script
    ),
    ActionInfo(
        name="Execute the Experiment Plan",
        description="Use this to perform an experiment of a given plan and derive the empirical performance. Specifically, another AI agent will help you edit the script based on your instruction, and then, execute the script and return the execution logs.",
        usage={
            "script_name": "a valid python script name with relative path to current directory if needed. An empty script will be created if it does not exist.",
            "plan": "a detailed step by step description of the plan for the experiment.",
            "save_name": "a valid file name with relative path to current directory if needed"
        },
        return_value="The observation will be the execution log of the edited script, if it successfully completes your plan within at most five trials.",
        function=execute
    ),
    ActionInfo(
        name="Edit Script Segment (AI)",
        description="Use this to do a relatively large but cohesive edit over a python script over a segment. Instead of editing the script directly, you should describe the edit instruction so that another AI can help you do this.",
        usage={
            "script_name": "a valid python script name with relative path to current directory if needed. An empty sctipt will be created if it does not exist.",
            "start_line_number": "a valid line number",
            "end_line_number": "a valid line number",
            "edit_instruction": "a detailed step by step description on how to edit it.",
            "save_name": "a valid file name with relative path to current directory if needed"
        },
        return_value="The observation will be the edited content of the script. If the script does not exist, the observation will be an error message. You should always double check whether the edit is correct. If it is far from correct, you can use the Undo Edit Script action to undo the edit.",
        function=edit_script_lines
    ),
    ActionInfo(
        name="Reflection",
        description="Use this to look over all the past steps and reflect. You should provide detailed description on what to reflect on and what should be returned.",
        usage={
            "things_to_reflect_on": "a detailed description on what to reflect on and what should be returned"
        },
        return_value="The observation will be a the reflection.",
        function=reflection
    ),
    ActionInfo(
        name="Retrieval from Research Log",
        description="Use this to retrieve relevant information from the research log. You should provide detailed description on what to look for and what should be returned.",
        usage={
            "current_plan": "a detailed description of the current research plan and status",
        },
        return_value="The observation will be a description of relevant content and lines in the research log.",
        function=retrieval_from_research_log
    ),
]

