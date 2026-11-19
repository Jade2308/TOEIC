'use client';

import React, { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';

export function ThemeToggle({ className = '' }: { className?: string }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const isDark = document.documentElement.classList.contains('dark');
    setTheme(isDark ? 'dark' : 'light');
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    if (nextTheme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  if (!mounted) {
    return (
      <div className={`w-9 h-9 rounded-xl border border-neutral-200 dark:border-neutral-800 ${className}`} />
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className={`p-2 rounded-xl border border-neutral-200 dark:border-emerald-950/60 bg-white/80 dark:bg-neutral-900/80 text-neutral-600 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 hover:text-emerald-600 hover:border-emerald-300 dark:hover:border-emerald-700 transition flex items-center justify-center shadow-xs ${className}`}
      title={theme === 'dark' ? 'Chuyển sang chế độ Sáng' : 'Chuyển sang chế độ Tối'}
      aria-label="Đổi giao diện Sáng / Tối"
    >
      {theme === 'dark' ? (
        <Sun className="w-4 h-4 text-amber-400 animate-fade-in" />
      ) : (
        <Moon className="w-4 h-4 text-emerald-600 animate-fade-in" />
      )}
    </button>
  );
}
