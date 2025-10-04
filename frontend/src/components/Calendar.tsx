'use client';

import { useEffect, useRef } from 'react';
import flatpickr from 'flatpickr';
import 'flatpickr/dist/flatpickr.min.css';

interface CalendarProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDate: string;
  availableDates: string[];
  onDateSelect: (date: string) => void;
}

export default function Calendar({ isOpen, onClose, selectedDate, availableDates, onDateSelect }: CalendarProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const flatpickrRef = useRef<flatpickr.Instance | null>(null);

  useEffect(() => {
    if (isOpen && inputRef.current && !flatpickrRef.current) {
      // Convert available dates to the format Flatpickr expects (YYYY-MM-DD)
      const enabledDates = availableDates.map(dateStr => {
        const date = new Date(dateStr);
        return date.toISOString().split('T')[0];
      });

      flatpickrRef.current = flatpickr(inputRef.current, {
        inline: true,
        dateFormat: 'Y-m-d',
        enable: enabledDates,
        defaultDate: selectedDate ? new Date(selectedDate).toISOString().split('T')[0] : undefined,
        onChange: function(selectedDates) {
          if (selectedDates.length > 0) {
            // Convert back to the format our app expects
            const selectedDate = selectedDates[0];
            const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
            const day = String(selectedDate.getDate()).padStart(2, '0');
            const year = selectedDate.getFullYear();
            const formattedDate = `${month}/${day}/${year} 00:00:00`;
            onDateSelect(formattedDate);
            onClose();
          }
        },
        onClose: function() {
          // Optional: close our modal when Flatpickr closes
        }
      });
    }

    return () => {
      if (flatpickrRef.current) {
        flatpickrRef.current.destroy();
        flatpickrRef.current = null;
      }
    };
  }, [isOpen, availableDates, selectedDate, onDateSelect, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-lg shadow-xl p-6 max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Select Date</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            ✕
          </button>
        </div>

        {/* Flatpickr Calendar */}
        <div className="calendar-container">
          <input
            ref={inputRef}
            type="text"
            className="hidden"
            readOnly
          />
        </div>

        {/* Legend */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            
          </div>
        </div>
      </div>
    </div>
  );
}