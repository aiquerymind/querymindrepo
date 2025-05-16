from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from MLAgentBench.environment import Environment
from MLAgentBench.agents.dsagent import DSAgent

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExperimentRequest(BaseModel):
    problem: str
    input_data: Optional[str] = None

class ExperimentResponse(BaseModel):
    status: str
    results: Optional[str] = None
    error: Optional[str] = None

@app.post("/api/experiment", response_model=ExperimentResponse)
async def run_experiment(request: ExperimentRequest):
    try:
        # Set up environment args
        class Args:
            def __init__(self):
                self.problem = request.problem
                self.input = request.input_data
                self.output = 'output'
                self.log_dir = 'logs'
                self.work_dir = 'workspace'
                self.device = 'cpu'
                self.python = 'python'
                self.interactive = False
                self.resume = None
                self.resume_step = 0

        args = Args()
        
        # Initialize environment
        env = Environment(args)
        agent = DSAgent(args, env)
        
        # Run experiment
        result = agent.run(env)
        
        return ExperimentResponse(
            status="success",
            results=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    return {"status": "running"}