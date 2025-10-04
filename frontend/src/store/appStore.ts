import { create } from 'zustand';
import { AppState } from '@/types';

export const useAppStore = create<AppState>((set) => ({
  selectedDate: '', // Will be set to today's date on initialization
  setSelectedDate: (date: string) => set({ selectedDate: date }),
}));

// Helper function to get today's date in the format used by the JSON
export function getTodayDateString(): string {
  const today = new Date();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  const year = today.getFullYear();
  return `${month}/${day}/${year} 00:00:00`;
}

// Initialize the store with today's date
if (typeof window !== 'undefined') {
  useAppStore.getState().setSelectedDate(getTodayDateString());
}
