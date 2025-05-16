import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export interface ExperimentRequest {
  problem: string
  input_data?: string
}

export interface ExperimentResponse {
  status: string
  results?: string
  error?: string
}

export async function runExperiment(request: ExperimentRequest): Promise<ExperimentResponse> {
  const response = await fetch(`${supabaseUrl}/functions/v1/experiment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${supabaseAnonKey}`
    },
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    throw new Error('Failed to run experiment')
  }

  return response.json()
}

export async function getExperiments() {
  const { data, error } = await supabase
    .from('experiments')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    throw error
  }

  return data
}

export async function getExperiment(id: string) {
  const { data, error } = await supabase
    .from('experiments')
    .select('*')
    .eq('id', id)
    .single()

  if (error) {
    throw error
  }

  return data
}