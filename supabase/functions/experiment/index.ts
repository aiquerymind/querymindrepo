import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'npm:@supabase/supabase-js@2.38.4'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

interface ExperimentRequest {
  problem: string
  input_data?: string
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    )

    const { problem, input_data } = await req.json() as ExperimentRequest

    // Create new experiment record
    const { data: experiment, error: insertError } = await supabase
      .from('experiments')
      .insert({
        problem,
        input_data,
        status: 'pending'
      })
      .select()
      .single()

    if (insertError) {
      throw insertError
    }

    // Simulate ML processing
    const results = `Processed experiment for problem: ${problem}`

    // Update experiment with results
    const { error: updateError } = await supabase
      .from('experiments')
      .update({ 
        results,
        status: 'completed'
      })
      .eq('id', experiment.id)

    if (updateError) {
      throw updateError
    }

    return new Response(
      JSON.stringify({ 
        status: 'success',
        results
      }),
      { 
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({
        status: 'error',
        error: error.message
      }),
      { 
        status: 500,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      }
    )
  }
})