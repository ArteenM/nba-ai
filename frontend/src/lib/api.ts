import { PredictionRequest, PredictionResult } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function predictWinner(request: PredictionRequest): Promise<PredictionResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/predict_winner/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling prediction API:', error);
    throw error;
  }
}
