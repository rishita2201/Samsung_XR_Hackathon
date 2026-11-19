import React from 'react';
import { Layers, Video, Activity, Scissors, BarChart3, FileText, CheckCircle2, Cpu } from 'lucide-react';

export type ActiveTab = 'overview' | 'ingest' | 'analysis' | 'editor' | 'results' | 'report';

interface NavbarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  activeVideoId?: string;
  isProcessing?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  activeVideoId,
  isProcessing
}) => {
  const tabs = [
    { id: 'overview' as ActiveTab, label: 'Overview', icon: Layers },
    { id: 'ingest' as ActiveTab, label: 'Ingestion', icon: Video },
    { id: 'analysis' as ActiveTab, label: 'Analysis Studio', icon: Activity },
    { id: 'editor' as ActiveTab, label: 'Highlight Editor', icon: Scissors },
    { id: 'results' as ActiveTab, label: 'Results & Export', icon: BarChart3 },
    { id: 'report' as ActiveTab, label: 'Technical Report', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#0a0d12]/95 backdrop-blur border-b border-[#222936]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Logo & Identity */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setActiveTab('overview')}
              className="flex items-center space-x-2.5 text-left group"
            >
              <div className="w-8 h-8 rounded bg-[#161c26] border border-[#2c3647] flex items-center justify-center text-emerald-400 group-hover:border-emerald-500/50 transition">
                <Scissors className="w-4 h-4" />
              </div>
              <div>
                <span className="text-sm font-semibold tracking-wider text-slate-100">
                  MOMENTIQ
                </span>
                <span className="hidden sm:inline-block ml-2 text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-emerald-950/70 border border-emerald-800/60 text-emerald-300">
                  Samsung XR Track 4
                </span>
              </div>
            </button>
          </div>

          {/* Navigation Items */}
          <nav className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium transition ${
                    isActive
                      ? 'bg-[#18202c] text-emerald-400 border border-[#2d3a4e]'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#12161f]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Active Target Video & Telemetry */}
          <div className="flex items-center space-x-3">
            {activeVideoId ? (
              <div className="flex items-center space-x-2 text-xs font-mono bg-[#111620] px-2.5 py-1 rounded border border-[#222a38]">
                <div className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'}`} />
                <span className="text-slate-300 truncate max-w-[120px]">{activeVideoId}</span>
              </div>
            ) : (
              <div className="hidden lg:flex items-center space-x-1.5 text-[11px] font-mono text-slate-400 bg-[#11151c] px-2.5 py-1 rounded border border-[#202633]">
                <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                <span>EPIC-KITCHENS-100 / FPVSum</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

