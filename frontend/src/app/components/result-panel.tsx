import { motion } from "motion/react";
import { Shield, TrendingUp, Users, Car, Home, Heart, X } from "lucide-react";
import { useState, useEffect } from "react";

interface ResultPanelProps {
  formData: any;
  onClose: () => void;
}

export function ResultPanel({ formData, onClose }: ResultPanelProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [confidenceScore, setConfidenceScore] = useState(0);

  // Calculate confidence score based on form data
  const calculateConfidence = () => {
    let score = 75; // Base score
    
    if (formData.income > 100000) score += 5;
    if (formData.homeOwner) score += 5;
    if (formData.claimsHistory === 0) score += 7;
    if (formData.dependents > 0) score += 3;
    if (formData.currentInsurance !== "none") score += 2;
    
    return Math.min(score, 98); // Cap at 98%
  };

  // Determine bundle based on form data
  const getBundleRecommendation = () => {
    if (formData.homeOwner && formData.vehicles >= 2 && formData.dependents > 0) {
      return {
        id: 4,
        name: "Premium Family Bundle",
        coverages: [
          { icon: Home, label: "Home Insurance", value: "$350K coverage" },
          { icon: Car, label: "Auto Insurance", value: "2 vehicles" },
          { icon: Heart, label: "Life Insurance", value: "$500K policy" },
          { icon: Shield, label: "Umbrella Policy", value: "$1M liability" },
        ],
        estimatedSavings: "32%",
        monthlyPremium: 487,
      };
    } else if (formData.homeOwner && formData.vehicles >= 1) {
      return {
        id: 3,
        name: "Homeowner Plus Bundle",
        coverages: [
          { icon: Home, label: "Home Insurance", value: "$350K coverage" },
          { icon: Car, label: "Auto Insurance", value: `${formData.vehicles} vehicle${formData.vehicles > 1 ? 's' : ''}` },
          { icon: Shield, label: "Personal Liability", value: "$500K coverage" },
        ],
        estimatedSavings: "24%",
        monthlyPremium: 358,
      };
    } else if (formData.vehicles >= 1 && formData.dependents > 0) {
      return {
        id: 2,
        name: "Essential Family Bundle",
        coverages: [
          { icon: Car, label: "Auto Insurance", value: `${formData.vehicles} vehicle${formData.vehicles > 1 ? 's' : ''}` },
          { icon: Heart, label: "Life Insurance", value: "$250K policy" },
          { icon: Users, label: "Health Rider", value: "Family coverage" },
        ],
        estimatedSavings: "18%",
        monthlyPremium: 245,
      };
    } else {
      return {
        id: 1,
        name: "Young Professional Bundle",
        coverages: [
          { icon: Car, label: "Auto Insurance", value: "Standard coverage" },
          { icon: Shield, label: "Renters Insurance", value: "$50K personal property" },
          { icon: Heart, label: "Life Insurance", value: "$100K policy" },
        ],
        estimatedSavings: "15%",
        monthlyPremium: 178,
      };
    }
  };

  const bundle = getBundleRecommendation();

  useEffect(() => {
    // Simulate AI processing
    const timer = setTimeout(() => {
      setIsLoading(false);
      // Animate confidence score
      const targetScore = calculateConfidence();
      let current = 0;
      const increment = targetScore / 50;
      const scoreTimer = setInterval(() => {
        current += increment;
        if (current >= targetScore) {
          current = targetScore;
          clearInterval(scoreTimer);
        }
        setConfidenceScore(Math.round(current));
      }, 20);
    }, 2000);

    return () => clearTimeout(timer);
  }, [formData]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        transition={{ type: "spring", duration: 0.5 }}
        className="relative max-w-2xl w-full"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute -top-4 -right-4 z-10 w-10 h-10 bg-slate-800 hover:bg-slate-700 rounded-full flex items-center justify-center text-slate-400 hover:text-white transition-colors border border-slate-700"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Glassmorphism card */}
        <div className="relative backdrop-blur-xl bg-slate-900/90 border border-slate-700/50 rounded-3xl p-8 shadow-2xl max-h-[90vh] overflow-y-auto">
          {/* Gradient glow */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-50 blur-2xl" />
          
          <div className="relative z-10">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-16">
                <motion.div
                  className="w-20 h-20 border-4 border-blue-500/30 border-t-blue-500 rounded-full mb-6"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
                <h3 className="text-xl font-semibold text-white mb-2">Analyzing Your Profile...</h3>
                <p className="text-slate-400">AI is processing your information</p>
              </div>
            ) : (
              <>
                {/* Recommended Bundle Badge */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", delay: 0.2 }}
                  className="text-center mb-8"
                >
                  <div className="inline-flex items-center gap-3 px-6 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 shadow-2xl shadow-blue-500/30 mb-4">
                    <Shield className="w-8 h-8 text-white" />
                    <div className="text-left">
                      <div className="text-sm text-blue-100 font-medium">Recommended Bundle</div>
                      <div className="text-2xl font-bold text-white">#{bundle.id}</div>
                    </div>
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-2">{bundle.name}</h2>
                  <p className="text-slate-400">Tailored to your unique profile</p>
                </motion.div>

                {/* Confidence Score with Animated Ring */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="flex items-center justify-center mb-8"
                >
                  <div className="relative w-40 h-40">
                    {/* Background circle */}
                    <svg className="w-full h-full transform -rotate-90">
                      <circle
                        cx="80"
                        cy="80"
                        r="70"
                        stroke="rgba(71, 85, 105, 0.3)"
                        strokeWidth="12"
                        fill="none"
                      />
                      {/* Animated progress circle */}
                      <motion.circle
                        cx="80"
                        cy="80"
                        r="70"
                        stroke="url(#scoreGradient)"
                        strokeWidth="12"
                        fill="none"
                        strokeLinecap="round"
                        initial={{ strokeDashoffset: 440 }}
                        animate={{ strokeDashoffset: 440 - (440 * confidenceScore) / 100 }}
                        transition={{ duration: 1, ease: "easeOut" }}
                        style={{ strokeDasharray: 440 }}
                      />
                      <defs>
                        <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#3B82F6" />
                          <stop offset="50%" stopColor="#8B5CF6" />
                          <stop offset="100%" stopColor="#EC4899" />
                        </linearGradient>
                      </defs>
                    </svg>
                    
                    {/* Center score */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.6, type: "spring" }}
                        className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"
                      >
                        {confidenceScore}%
                      </motion.div>
                      <div className="text-sm text-slate-400 font-medium">Confidence</div>
                    </div>
                  </div>
                </motion.div>

                {/* Explanation */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="bg-slate-800/40 rounded-2xl p-6 mb-6 border border-slate-700/50"
                >
                  <div className="flex items-start gap-3 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-white font-semibold mb-2">Why This Bundle?</h3>
                      <p className="text-slate-400 text-sm leading-relaxed">
                        Based on your {formData.homeOwner ? 'homeowner status' : 'rental situation'}, 
                        {formData.dependents > 0 ? ` ${formData.dependents} dependent${formData.dependents > 1 ? 's' : ''}` : ' independent lifestyle'}, 
                        {formData.vehicles > 0 ? ` ${formData.vehicles} vehicle${formData.vehicles > 1 ? 's' : ''}` : ' no vehicles'}, 
                        and {formData.claimsHistory === 0 ? 'clean claims history' : 'claims history'}, 
                        our AI recommends comprehensive coverage optimized for your risk profile and financial situation.
                      </p>
                    </div>
                  </div>
                </motion.div>

                {/* Coverage Details */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                  className="space-y-3 mb-6"
                >
                  <h4 className="text-white font-semibold mb-3">Included Coverages:</h4>
                  {bundle.coverages.map((coverage, index) => {
                    const Icon = coverage.icon;
                    return (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.8 + index * 0.1 }}
                        className="flex items-center justify-between p-4 bg-slate-800/40 rounded-xl border border-slate-700/50 hover:border-blue-500/30 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
                            <Icon className="w-5 h-5 text-blue-400" />
                          </div>
                          <div>
                            <div className="text-white font-medium">{coverage.label}</div>
                            <div className="text-sm text-slate-400">{coverage.value}</div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </motion.div>

                {/* Pricing */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.2 }}
                  className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-2xl border border-blue-500/30"
                >
                  <div>
                    <div className="text-sm text-blue-300 mb-1">Estimated Monthly Premium</div>
                    <div className="text-3xl font-bold text-white">${bundle.monthlyPremium}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-purple-300 mb-1">Bundle Savings</div>
                    <div className="text-2xl font-bold text-transparent bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text">
                      {bundle.estimatedSavings}
                    </div>
                  </div>
                </motion.div>
              </>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
