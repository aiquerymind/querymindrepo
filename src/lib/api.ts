export interface ExperimentRequest {
  problem: string;
  input_data?: string;
}

export interface ExperimentResponse {
  status: string;
  results?: string;
  error?: string;
}

export async function runExperiment(request: ExperimentRequest): Promise<ExperimentResponse> {
  const response = await fetch('/api/experiment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to run experiment');
  }

  return response.json();
}

export async function getStatus(): Promise<{ status: string }> {
  const response = await fetch('/api/status');
  
  if (!response.ok) {
    throw new Error('Failed to get status');
  }
  
  return response.json();
}