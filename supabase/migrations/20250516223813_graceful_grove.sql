/*
  # Create experiments table

  1. New Tables
    - `experiments`
      - `id` (uuid, primary key)
      - `problem` (text)
      - `input_data` (text, nullable)
      - `results` (text, nullable) 
      - `status` (text)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
      
  2. Security
    - Enable RLS on experiments table
    - Add policies for authenticated users
*/

CREATE TABLE IF NOT EXISTS experiments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  problem text NOT NULL,
  input_data text,
  results text,
  status text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own experiments"
  ON experiments
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own experiments"
  ON experiments
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own experiments"
  ON experiments
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = id);