import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  User, 
  Users, 
  Car, 
  Shield, 
  ChevronRight, 
  ChevronLeft,
  Check
} from "lucide-react";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";

interface AssessmentFormProps {
  onComplete: (data: any) => void;
}

const steps = [
  { id: 1, title: "Personal Info", icon: User },
  { id: 2, title: "Family Profile", icon: Users },
  { id: 3, title: "Assets & Vehicles", icon: Car },
  { id: 4, title: "Insurance History", icon: Shield },
];

export function AssessmentForm({ onComplete }: AssessmentFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Personal Info
    age: 35,
    occupation: "",
    income: 75000,
    
    // Family Profile
    maritalStatus: "",
    dependents: 2,
    hasChildren: true,
    
    // Assets & Vehicles
    homeOwner: true,
    vehicles: 2,
    propertyValue: 350000,
    
    // Insurance History
    currentInsurance: "",
    claimsHistory: 0,
    riskTolerance: "medium",
  });

  const updateFormData = (key: string, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(formData);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="relative max-w-3xl mx-auto"
    >
      {/* Glassmorphism card */}
      <div className="relative backdrop-blur-xl bg-slate-900/40 border border-slate-700/50 rounded-3xl p-8 shadow-2xl overflow-hidden">
        {/* Gradient border glow */}
        <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-blue-500/20 opacity-50 blur-xl" />
        
        <div className="relative z-10">
          {/* Step indicator */}
          <div className="flex items-center justify-between mb-8">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = step.id === currentStep;
              const isCompleted = step.id < currentStep;
              
              return (
                <div key={step.id} className="flex items-center flex-1">
                  <div className="flex flex-col items-center">
                    <motion.div
                      className={`
                        relative w-12 h-12 rounded-full flex items-center justify-center
                        ${isActive ? 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg shadow-blue-500/50' : ''}
                        ${isCompleted ? 'bg-gradient-to-r from-blue-500 to-purple-500' : ''}
                        ${!isActive && !isCompleted ? 'bg-slate-800 border border-slate-700' : ''}
                      `}
                      animate={isActive ? {
                        boxShadow: [
                          "0 0 20px rgba(59, 130, 246, 0.5)",
                          "0 0 30px rgba(168, 85, 247, 0.6)",
                          "0 0 20px rgba(59, 130, 246, 0.5)",
                        ],
                      } : {}}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      {isCompleted ? (
                        <Check className="w-5 h-5 text-white" />
                      ) : (
                        <Icon className={`w-5 h-5 ${isActive || isCompleted ? 'text-white' : 'text-slate-500'}`} />
                      )}
                    </motion.div>
                    <span className={`text-xs mt-2 font-medium ${isActive ? 'text-blue-400' : 'text-slate-500'}`}>
                      {step.title}
                    </span>
                  </div>
                  
                  {index < steps.length - 1 && (
                    <div className="flex-1 h-0.5 mx-2 bg-slate-800 relative overflow-hidden">
                      {isCompleted && (
                        <motion.div
                          className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500"
                          initial={{ scaleX: 0 }}
                          animate={{ scaleX: 1 }}
                          transition={{ duration: 0.5 }}
                        />
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Form content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="min-h-[400px]"
            >
              {currentStep === 1 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-white mb-6">Personal Information</h2>
                  
                  <div className="space-y-2">
                    <Label className="text-slate-300">Age</Label>
                    <Input
                      type="number"
                      value={formData.age}
                      onChange={(e) => updateFormData("age", parseInt(e.target.value))}
                      className="bg-slate-800/50 border-slate-700 text-white"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="text-slate-300">Occupation</Label>
                    <Select value={formData.occupation} onValueChange={(value) => updateFormData("occupation", value)}>
                      <SelectTrigger className="bg-slate-800/50 border-slate-700 text-white">
                        <SelectValue placeholder="Select occupation" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="professional">Professional</SelectItem>
                        <SelectItem value="business">Business Owner</SelectItem>
                        <SelectItem value="employee">Employee</SelectItem>
                        <SelectItem value="retired">Retired</SelectItem>
                        <SelectItem value="self-employed">Self-Employed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3">
                    <Label className="text-slate-300">Annual Income: ${formData.income.toLocaleString()}</Label>
                    <Slider
                      value={[formData.income]}
                      onValueChange={(value) => updateFormData("income", value[0])}
                      min={20000}
                      max={500000}
                      step={5000}
                      className="py-4"
                    />
                    <div className="flex justify-between text-xs text-slate-500">
                      <span>$20K</span>
                      <span>$500K</span>
                    </div>
                  </div>
                </div>
              )}

              {currentStep === 2 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-white mb-6">Family Profile</h2>
                  
                  <div className="space-y-2">
                    <Label className="text-slate-300">Marital Status</Label>
                    <Select value={formData.maritalStatus} onValueChange={(value) => updateFormData("maritalStatus", value)}>
                      <SelectTrigger className="bg-slate-800/50 border-slate-700 text-white">
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="single">Single</SelectItem>
                        <SelectItem value="married">Married</SelectItem>
                        <SelectItem value="divorced">Divorced</SelectItem>
                        <SelectItem value="widowed">Widowed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3">
                    <Label className="text-slate-300">Number of Dependents: {formData.dependents}</Label>
                    <Slider
                      value={[formData.dependents]}
                      onValueChange={(value) => updateFormData("dependents", value[0])}
                      min={0}
                      max={6}
                      step={1}
                      className="py-4"
                    />
                    <div className="flex justify-between text-xs text-slate-500">
                      <span>0</span>
                      <span>6+</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-xl border border-slate-700/50">
                    <div>
                      <Label className="text-slate-300">Children Under 18</Label>
                      <p className="text-sm text-slate-500 mt-1">Do you have children under 18?</p>
                    </div>
                    <Switch
                      checked={formData.hasChildren}
                      onCheckedChange={(checked) => updateFormData("hasChildren", checked)}
                    />
                  </div>
                </div>
              )}

              {currentStep === 3 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-white mb-6">Assets & Vehicles</h2>
                  
                  <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-xl border border-slate-700/50">
                    <div>
                      <Label className="text-slate-300">Home Owner</Label>
                      <p className="text-sm text-slate-500 mt-1">Do you own your home?</p>
                    </div>
                    <Switch
                      checked={formData.homeOwner}
                      onCheckedChange={(checked) => updateFormData("homeOwner", checked)}
                    />
                  </div>

                  {formData.homeOwner && (
                    <div className="space-y-3">
                      <Label className="text-slate-300">Property Value: ${formData.propertyValue.toLocaleString()}</Label>
                      <Slider
                        value={[formData.propertyValue]}
                        onValueChange={(value) => updateFormData("propertyValue", value[0])}
                        min={100000}
                        max={2000000}
                        step={25000}
                        className="py-4"
                      />
                      <div className="flex justify-between text-xs text-slate-500">
                        <span>$100K</span>
                        <span>$2M+</span>
                      </div>
                    </div>
                  )}

                  <div className="space-y-3">
                    <Label className="text-slate-300">Number of Vehicles: {formData.vehicles}</Label>
                    <Slider
                      value={[formData.vehicles]}
                      onValueChange={(value) => updateFormData("vehicles", value[0])}
                      min={0}
                      max={5}
                      step={1}
                      className="py-4"
                    />
                    <div className="flex justify-between text-xs text-slate-500">
                      <span>0</span>
                      <span>5+</span>
                    </div>
                  </div>
                </div>
              )}

              {currentStep === 4 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-white mb-6">Insurance History</h2>
                  
                  <div className="space-y-2">
                    <Label className="text-slate-300">Current Insurance Provider</Label>
                    <Select value={formData.currentInsurance} onValueChange={(value) => updateFormData("currentInsurance", value)}>
                      <SelectTrigger className="bg-slate-800/50 border-slate-700 text-white">
                        <SelectValue placeholder="Select provider or none" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">No Current Insurance</SelectItem>
                        <SelectItem value="state-farm">State Farm</SelectItem>
                        <SelectItem value="geico">GEICO</SelectItem>
                        <SelectItem value="progressive">Progressive</SelectItem>
                        <SelectItem value="allstate">Allstate</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3">
                    <Label className="text-slate-300">Claims in Last 5 Years: {formData.claimsHistory}</Label>
                    <Slider
                      value={[formData.claimsHistory]}
                      onValueChange={(value) => updateFormData("claimsHistory", value[0])}
                      min={0}
                      max={5}
                      step={1}
                      className="py-4"
                    />
                    <div className="flex justify-between text-xs text-slate-500">
                      <span>0</span>
                      <span>5+</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-slate-300">Risk Tolerance</Label>
                    <Select value={formData.riskTolerance} onValueChange={(value) => updateFormData("riskTolerance", value)}>
                      <SelectTrigger className="bg-slate-800/50 border-slate-700 text-white">
                        <SelectValue placeholder="Select risk tolerance" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low - Maximum Coverage</SelectItem>
                        <SelectItem value="medium">Medium - Balanced</SelectItem>
                        <SelectItem value="high">High - Minimal Coverage</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          {/* Navigation buttons */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-700/50">
            <motion.button
              onClick={handlePrev}
              disabled={currentStep === 1}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800/50 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 transition-colors"
              whileHover={currentStep > 1 ? { x: -5 } : {}}
              whileTap={currentStep > 1 ? { scale: 0.95 } : {}}
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </motion.button>

            <div className="text-sm text-slate-500">
              Step {currentStep} of {steps.length}
            </div>

            <motion.button
              onClick={handleNext}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium hover:shadow-lg hover:shadow-blue-500/30 transition-all"
              whileHover={{ x: 5 }}
              whileTap={{ scale: 0.95 }}
            >
              {currentStep === steps.length ? "Generate Recommendation" : "Next"}
              <ChevronRight className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
