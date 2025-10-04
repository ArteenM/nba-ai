'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAppStore } from '@/store/appStore';
import { getAvailableDates, formatDateForDisplay } from '@/lib/dataSource';
import Calendar from './Calendar';

export default function Header() {
  const { selectedDate, setSelectedDate } = useAppStore();
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [currentDateIndex, setCurrentDateIndex] = useState(0);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);

  useEffect(() => {
    const loadDates = async () => {
      try {
        const dates = await getAvailableDates();
        setAvailableDates(dates);
        
        // Find current date index
        const currentIndex = dates.findIndex(date => date === selectedDate);
        if (currentIndex !== -1) {
          setCurrentDateIndex(currentIndex);
        }
      } catch (error) {
        console.error('Error loading dates:', error);
      }
    };

    loadDates();
  }, [selectedDate]);

  const handlePreviousDate = () => {
    if (currentDateIndex > 0) {
      const newIndex = currentDateIndex - 1;
      setCurrentDateIndex(newIndex);
      setSelectedDate(availableDates[newIndex]);
    }
  };

  const handleNextDate = () => {
    if (currentDateIndex < availableDates.length - 1) {
      const newIndex = currentDateIndex + 1;
      setCurrentDateIndex(newIndex);
      setSelectedDate(availableDates[newIndex]);
    }
  };

  const handleToday = () => {
    const today = new Date();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const year = today.getFullYear();
    const todayString = `${month}/${day}/${year} 00:00:00`;
    
    const todayIndex = availableDates.findIndex(date => date === todayString);
    if (todayIndex !== -1) {
      setCurrentDateIndex(todayIndex);
      setSelectedDate(todayString);
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="text-2xl font-bold text-gray-900">
              HoopPredict
            </Link>
          </div>

          {/* Date Controls */}
          <div className="flex items-center space-x-4">
            {/* Date Switcher */}
            <div className="flex items-center space-x-2">
              <button
                onClick={handlePreviousDate}
                disabled={currentDateIndex === 0}
                className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <div className="text-center min-w-[200px]">
                <div className="text-sm font-medium text-gray-900">
                  {selectedDate ? formatDateForDisplay(selectedDate) : 'Loading...'}
                </div>
                <button
                  onClick={handleToday}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Today
                </button>
              </div>
              
              <button
                onClick={handleNextDate}
                disabled={currentDateIndex === availableDates.length - 1}
                className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            {/* Calendar Button */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsCalendarOpen(true)}
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>Calendar</span>
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex space-x-8">
            <Link
              href="/"
              className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              Dashboard
            </Link>
            <Link
              href="/teams"
              className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              Teams
            </Link>
            <Link
              href="/about"
              className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              About
            </Link>
          </nav>
        </div>
      </div>

      {/* Calendar Modal */}
      <Calendar
        isOpen={isCalendarOpen}
        onClose={() => setIsCalendarOpen(false)}
        selectedDate={selectedDate}
        availableDates={availableDates}
        onDateSelect={(date) => {
          const selectedIndex = availableDates.findIndex(d => d === date);
          if (selectedIndex !== -1) {
            setCurrentDateIndex(selectedIndex);
            setSelectedDate(date);
          }
        }}
      />
    </header>
  );
}
