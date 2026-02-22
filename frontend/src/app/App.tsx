import { useState, useEffect } from "react";
import { AnimatePresence } from "motion/react";
import { BackgroundEffects } from "./components/background-effects";
import { HeroSection } from "./components/hero-section";
import { AssessmentForm } from "./components/assessment-form";
import { ResultPanel } from "./components/result-panel";

export default function App() {
  const [showForm, setShowForm] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [assessmentData, setAssessmentData] = useState(null);

  const handleStartAssessment = () => {
    setShowForm(true);
  };

  const handleAssessmentComplete = (data: any) => {
    setAssessmentData(data);
    setShowResult(true);
  };

  const handleCloseResult = () => {
    setShowResult(false);
    setShowForm(false);
  };

  useEffect(() => {
    if (showResult) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [showResult]);

  return (
    <>
      <div className="min-h-screen bg-[#0F172A] overflow-hidden relative">
        {/* Background effects */}
        <BackgroundEffects />

        {/* Main content */}
        <div className="relative z-10 container mx-auto px-4 py-12">
          {/* Logo/Brand */}
          <div className="flex items-center justify-between mb-12">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">InsureAI</h1>
                <p className="text-xs text-slate-400">Intelligent Coverage Solutions</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button className="text-slate-400 hover:text-white transition-colors text-sm">
                About
              </button>
              <button className="text-slate-400 hover:text-white transition-colors text-sm">
                Contact
              </button>
              <button className="px-4 py-2 rounded-lg bg-slate-800 text-white hover:bg-slate-700 transition-colors text-sm">
                Sign In
              </button>
            </div>
          </div>

          {/* Hero section */}
          {!showForm && <HeroSection onStartAssessment={handleStartAssessment} />}

          {/* Assessment form */}
          {showForm && <AssessmentForm onComplete={handleAssessmentComplete} />}
        </div>
      </div>

      {/* Result modal — outside overflow-hidden to allow fixed positioning */}
      <AnimatePresence>
        {showResult && assessmentData && (
          <ResultPanel formData={assessmentData} onClose={handleCloseResult} />
        )}
      </AnimatePresence>
    </>
  );
}
