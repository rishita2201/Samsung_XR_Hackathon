import React, { useState, useEffect } from 'react';
import { Navbar, ActiveTab } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { UploadWorkspace } from './pages/UploadWorkspace';
import { AnalysisWorkspace } from './pages/AnalysisWorkspace';
import { HighlightEditor } from './pages/HighlightEditor';
import { ResultsDashboard } from './pages/ResultsDashboard';
import { TechnicalReport } from './pages/TechnicalReport';
import { api } from './services/api';
import { AnalysisResult, PipelineProgress } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [activeVideoId, setActiveVideoId] = useState<string>('synthetic_demo');
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState<PipelineProgress | null>(null);

  // Load active video analysis details
  const loadVideoDetails = async (vidId: string) => {
    try {
      const data = await api.getVideoDetails(vidId);
      setAnalysis(data);
      setActiveVideoId(vidId);
    } catch (e) {
      console.log('Video details not available yet for', vidId);
    }
  };

  useEffect(() => {
    // Check if synthetic_demo or any video exists on startup
    loadVideoDetails('synthetic_demo');
  }, []);

  const handleVideoSelected = (vidId: string) => {
    setActiveVideoId(vidId);
    loadVideoDetails(vidId);
  };

  const handleSelectSyntheticDemo = () => {
    setActiveVideoId('synthetic_demo');
    loadVideoDetails('synthetic_demo');
    setActiveTab('analysis');
  };

  return (
    <div className="min-h-screen bg-[#0a0d12] text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-slate-950">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeVideoId={activeVideoId}
        isProcessing={isProcessing}
      />

      <main className="flex-1">
        {activeTab === 'overview' && (
          <LandingPage
            onNavigate={(tab) => setActiveTab(tab)}
            onSelectSyntheticDemo={handleSelectSyntheticDemo}
          />
        )}

        {activeTab === 'ingest' && (
          <UploadWorkspace
            onVideoSelected={(id) => {
              handleVideoSelected(id);
              setActiveTab('analysis');
            }}
            activeVideoId={activeVideoId}
            isProcessing={isProcessing}
            setIsProcessing={setIsProcessing}
            progress={progress}
            setProgress={setProgress}
          />
        )}

        {activeTab === 'analysis' && (
          <AnalysisWorkspace
            videoId={activeVideoId}
            analysis={analysis}
            onNavigateToEditor={() => setActiveTab('editor')}
          />
        )}

        {activeTab === 'editor' && (
          <HighlightEditor
            videoId={activeVideoId}
            analysis={analysis}
            onRefreshAnalysis={() => loadVideoDetails(activeVideoId)}
            onNavigateToResults={() => setActiveTab('results')}
          />
        )}

        {activeTab === 'results' && (
          <ResultsDashboard
            videoId={activeVideoId}
            analysis={analysis}
          />
        )}

        {activeTab === 'report' && (
          <TechnicalReport />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#1b212c] py-6 px-4 sm:px-6 lg:px-8 mt-12 bg-[#090b0f] text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-300">MOMENTIQ</span>
            <span>·</span>
            <span>Samsung XR Hackathon 2026</span>
            <span>·</span>
            <span className="text-emerald-400">Track 4: Action-Aware Video Summarization</span>
          </div>

          <div className="flex items-center space-x-4 font-mono text-[11px]">
            <span>Budget: &le; 15.0%</span>
            <span>EPIC-KITCHENS-100 / FPVSum</span>
            <span className="text-slate-400">Offline CLIP ViT-B/32</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
