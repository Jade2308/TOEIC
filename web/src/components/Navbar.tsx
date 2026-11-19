'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Layers,
  AlertCircle,
  BookOpen,
  Download,
  Menu,
  X,
  UploadCloud,
} from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';
import { ExamSwitcher } from '@/components/ExamSwitcher';
import { useMistakeStore } from '@/stores/useMistakeStore';
import { useVocabStore } from '@/stores/useVocabStore';
import { ToeicDataService } from '@/lib/data-service';
import { SystemHealthStatus } from '@/types/toeic';

export function Navbar() {
  const pathname = usePathname();
  const { mistakes, loadMistakes } = useMistakeStore();
  const { vocabList, loadVocab } = useVocabStore();
  const [health, setHealth] = useState<SystemHealthStatus | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadMistakes();
    loadVocab();
    ToeicDataService.getSystemHealth().then(setHealth);
  }, [loadMistakes, loadVocab]);

  const unresolvedCount = mistakes.filter((m) => !m.resolved).length;
  const now = new Date();
  const dueVocabCount = vocabList.filter((v) => new Date(v.due_date) <= now).length;

  const navItems = [
    {
      href: '/',
      label: 'Tổng quan',
      icon: LayoutDashboard,
      active: pathname === '/',
      badge: null as number | null,
      badgeColor: '',
    },
    {
      href: '/practice',
      label: 'Luyện đề',
      icon: Layers,
      active: pathname.startsWith('/practice'),
      badge: null as number | null,
      badgeColor: '',
    },
    {
      href: '/error-log',
      label: 'Sổ câu sai',
      icon: AlertCircle,
      active: pathname.startsWith('/error-log'),
      badge: unresolvedCount > 0 ? unresolvedCount : null,
      badgeColor: 'bg-rose-500 text-white',
    },
    {
      href: '/vocab-srs',
      label: 'Từ vựng SRS',
      icon: BookOpen,
      active: pathname.startsWith('/vocab-srs'),
      badge: dueVocabCount > 0 ? dueVocabCount : null,
      badgeColor: 'bg-emerald-600 text-white',
    },
    {
      href: '/admin',
      label: 'Tải đề',
      icon: UploadCloud,
      active: pathname.startsWith('/admin'),
      badge: null as number | null,
      badgeColor: '',
    },
  ];

  const hasWriteError = Boolean(health && !health.ok);

  return (
    <header className="sticky top-0 z-50 bg-white/90 dark:bg-[#0c1410]/90 backdrop-blur-md border-b border-emerald-950/10 dark:border-emerald-900/30 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 text-white flex items-center justify-center font-black text-sm shadow-md shadow-emerald-600/25 group-hover:scale-105 transition">
              T
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-sm sm:text-base tracking-tight text-neutral-900 dark:text-neutral-100 flex items-center gap-1.5">
                TOEIC <span className="text-emerald-600 dark:text-emerald-400 font-bold">Coach</span>
              </span>
            </div>
          </Link>

          {/* Current Exam Switcher */}
          <ExamSwitcher className="hidden lg:inline-flex" />
        </div>

        {/* Desktop Navigation - Clear function tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-emerald-950/5 dark:bg-emerald-950/30 p-1 rounded-2xl border border-emerald-900/10 dark:border-emerald-800/30">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-2 transition ${
                  item.active
                    ? 'bg-emerald-600 text-white shadow-xs font-bold'
                    : 'text-neutral-600 dark:text-neutral-300 hover:text-emerald-700 dark:hover:text-emerald-300 hover:bg-emerald-500/10'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
                {item.badge !== null && (
                  <span
                    className={`text-[10px] font-bold px-1.5 py-0.2 rounded-full min-w-4 text-center ${item.badgeColor}`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right utilities: Backup & Theme Toggle */}
        <div className="flex items-center gap-2">
          {hasWriteError && (
            <div
              className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-[11px] font-medium border bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800"
              title="Không thể lưu dữ liệu học tập"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
              <span>Lỗi lưu dữ liệu</span>
            </div>
          )}

          <a
            href="/api/user/backup"
            download
            className="p-2 rounded-xl border border-neutral-200 dark:border-emerald-950/60 bg-white/80 dark:bg-neutral-900/80 text-neutral-500 dark:text-neutral-400 hover:text-emerald-600 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition text-xs flex items-center"
            title="Sao lưu dữ liệu học tập"
            aria-label="Sao lưu dữ liệu học tập"
          >
            <Download className="w-3.5 h-3.5" />
          </a>

          {/* Theme Toggle (Light / Dark) */}
          <ThemeToggle />

          {/* Mobile hamburger button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-xl border border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-300"
            aria-label="Toggle Menu"
          >
            {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-emerald-950/10 dark:border-emerald-900/30 bg-white dark:bg-[#0c1410] px-4 py-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between p-2.5 rounded-xl text-xs font-semibold ${
                  item.active
                    ? 'bg-emerald-600 text-white'
                    : 'text-neutral-700 dark:text-neutral-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/30'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                {item.badge !== null && (
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}

          <div className="pt-2.5 mt-1 border-t border-emerald-950/10 dark:border-emerald-900/30">
            <div className="text-[10px] uppercase font-bold tracking-wider text-neutral-400 mb-1.5 px-1">
              Bộ đề đang chọn
            </div>
            <ExamSwitcher className="w-full justify-between" />
          </div>
        </div>
      )}
    </header>
  );
}
