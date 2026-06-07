import React, { useState, useEffect } from 'react';
import { Filter, Users, TrendingUp, FlaskConical, ChevronRight, Download, Activity, RotateCcw } from 'lucide-react';

interface CohortAnalysisProps {
  sessionId: string;
}

const CohortAnalysis: React.FC<CohortAnalysisProps> = ({ sessionId }) => {
  const [diseases, setDiseases] = useState<string[]>([]);
  const [medications, setMedications] = useState<string[]>([]);
  const [outcomes, setOutcomes] = useState<string[]>([]);
  const [selectedDisease, setSelectedDisease] = useState('');
  const [selectedMedication, setSelectedMedication] = useState('');
  const [selectedOutcome, setSelectedOutcome] = useState('');
  const [selectedAgeGroup, setSelectedAgeGroup] = useState('');
  const [cohortResult, setCohortResult] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [visibleRecords, setVisibleRecords] = useState(10);

  const handleCreateCohort = async (diseaseOverride?: string, medicationOverride?: string, outcomeOverride?: string, ageGroupOverride?: string) => {
    if (!sessionId) return;
    setLoading(true);
    setVisibleRecords(10);
    
    try {
      const filters = {
        session_id: sessionId,
        disease: diseaseOverride !== undefined ? (diseaseOverride || undefined) : (selectedDisease || undefined),
        medication: medicationOverride !== undefined ? (medicationOverride || undefined) : (selectedMedication || undefined),
        outcome: outcomeOverride !== undefined ? (outcomeOverride || undefined) : (selectedOutcome || undefined),
        age_group: ageGroupOverride !== undefined ? (ageGroupOverride || undefined) : (selectedAgeGroup || undefined),
      };
      
      console.log('Sending cohort request:', filters);
      const response = await fetch('/api/cohort/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters),
      });
      
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Failed to filter population' }));
        throw new Error(errData.detail || 'Filter failed');
      }
      
      const data = await response.json();
      console.log('Analysis result received:', data);
      setCohortResult(data);
      fetchInsights(data.cohort_name);
    } catch (err: any) {
      console.error('Cohort creation error:', err);
      alert(err.message || "No patients match these specific criteria.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!sessionId) return;
    
    const fetchFilters = async () => {
      console.log('Fetching filters for session:', sessionId);
      try {
        const [dRes, mRes, oRes] = await Promise.all([
          fetch(`/api/cohort/diseases/${sessionId}`),
          fetch(`/api/cohort/medications/${sessionId}`),
          fetch(`/api/cohort/outcomes/${sessionId}`)
        ]);
        
        const dData = dRes.ok ? await dRes.json() : { diseases: [] };
        const mData = mRes.ok ? await mRes.json() : { medications: [] };
        const oData = oRes.ok ? await oRes.json() : { outcomes: [] };
        
        setDiseases(dData.diseases || []);
        setMedications(mData.medications || []);
        setOutcomes(oData.outcomes || []);
      } catch (err) {
        console.error("Failed to fetch filter options:", err);
      }
    };
    fetchFilters();
    handleCreateCohort('', '', '', ''); // Baseline load
  }, [sessionId]);

  const fetchInsights = async (cohortName: string) => {
    setLoadingInsights(true);
    try {
      const response = await fetch('/api/insights/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          cohort_name: cohortName,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setInsights(data);
      }
    } catch (err) {
      console.error("Failed to fetch insights:", err);
    } finally {
      setLoadingInsights(false);
    }
  };

  const clearFilters = () => {
    setSelectedDisease('');
    setSelectedMedication('');
    setSelectedOutcome('');
    setSelectedAgeGroup('');
    handleCreateCohort('', '', '', '');
  };

  return (
    <div className="space-y-12 animate-in fade-in duration-700">
      {/* Filters Card */}
      <div className="card p-8 bg-white shadow-xl shadow-slate-200/40 border-slate-200/50">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3 text-slate-900">
            <div className="p-1.5 bg-blue-50 rounded-lg">
              <Filter className="w-4 h-4 text-blue-600" />
            </div>
            <h3 className="text-sm font-bold uppercase tracking-[0.1em]">Target Population Parameters</h3>
          </div>
          {(selectedDisease || selectedMedication || selectedOutcome || selectedAgeGroup) && (
            <button 
              onClick={clearFilters}
              className="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-widest hover:text-blue-600 transition-colors"
            >
              <RotateCcw className="w-3 h-3" /> Reset Filters
            </button>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Pathology</label>
            <select className="input-field text-sm h-11 px-4" value={selectedDisease} onChange={(e) => setSelectedDisease(e.target.value)}>
              <option value="">All Diseases</option>
              {diseases.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Regimen</label>
            <select className="input-field text-sm h-11 px-4" value={selectedMedication} onChange={(e) => setSelectedMedication(e.target.value)}>
              <option value="">All Medications</option>
              {medications.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Outcome Status</label>
            <select className="input-field text-sm h-11 px-4" value={selectedOutcome} onChange={(e) => setSelectedOutcome(e.target.value)}>
              <option value="">All Outcomes</option>
              {outcomes.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Cohort Age</label>
            <select className="input-field text-sm h-11 px-4" value={selectedAgeGroup} onChange={(e) => setSelectedAgeGroup(e.target.value)}>
              <option value="">Baseline (All)</option>
              <option value="child">Pediatric (0-17)</option>
              <option value="adult">Adult (18-59)</option>
              <option value="senior">Geriatric (60+)</option>
            </select>
          </div>
        </div>

        <button 
          onClick={() => handleCreateCohort()}
          disabled={loading}
          className="mt-10 w-full btn-primary h-12 flex items-center justify-center gap-3 shadow-lg shadow-blue-600/10 text-base font-bold"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <Activity className="w-5 h-5 animate-pulse" />
              Processing Cohort...
            </span>
          ) : (
            <>
              Update Analysis
              <ChevronRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>

      {cohortResult && (
        <div className="space-y-12 animate-in slide-in-from-bottom-4 duration-1000">
          {/* Insights Panel */}
          {insights && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 card p-8 bg-gradient-to-br from-indigo-900 to-slate-900 text-white border-none shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-indigo-500/20 rounded-lg backdrop-blur-md">
                    <Activity className="w-5 h-5 text-indigo-300" />
                  </div>
                  <h3 className="text-lg font-bold tracking-tight">Clinical AI Executive Summary</h3>
                </div>
                <p className="text-indigo-100/80 leading-relaxed text-lg italic font-medium">
                  "{insights.summary}"
                </p>
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="text-[10px] font-black text-indigo-300 uppercase tracking-[0.2em]">Key Insights</h4>
                    <ul className="space-y-3">
                      {insights.insights.slice(0, 3).map((item: string, i: number) => (
                        <li key={i} className="flex gap-3 text-sm text-indigo-50/70">
                          <span className="text-indigo-400 font-bold">•</span> {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="space-y-4">
                    <h4 className="text-[10px] font-black text-indigo-300 uppercase tracking-[0.2em]">Recommendations</h4>
                    <ul className="space-y-3">
                      {insights.recommendations.slice(0, 3).map((item: string, i: number) => (
                        <li key={i} className="flex gap-3 text-sm text-indigo-50/70">
                          <span className="text-emerald-400 font-bold">→</span> {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="card p-8 bg-white border-slate-200">
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6">Risk Stratification</h4>
                <div className="space-y-6">
                  {['Critical', 'High', 'Moderate', 'Low'].map(level => {
                    const count = cohortResult.patients.filter((p: any) => p.risk_level === level).length;
                    const percentage = Math.round((count / cohortResult.total_patients) * 100);
                    return (
                      <div key={level} className="space-y-2">
                        <div className="flex justify-between items-end">
                          <span className={`text-xs font-bold ${
                            level === 'Critical' ? 'text-red-600' : 
                            level === 'High' ? 'text-orange-600' : 
                            level === 'Moderate' ? 'text-amber-600' : 'text-emerald-600'
                          }`}>{level} Risk</span>
                          <span className="text-[10px] font-black text-slate-400">{percentage}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all duration-1000 ${
                              level === 'Critical' ? 'bg-red-500' : 
                              level === 'High' ? 'bg-orange-500' : 
                              level === 'Moderate' ? 'bg-amber-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {insights?.protocol_analysis && (
            <div className="card p-8 bg-slate-50 border-slate-200 border-dashed animate-in fade-in zoom-in duration-700">
              <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
                <div className="flex-shrink-0 flex flex-col items-center gap-2">
                  <div className="relative w-24 h-24 flex items-center justify-center">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-200" />
                      <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" 
                        strokeDasharray={251}
                        strokeDashoffset={251 - (251 * insights.protocol_analysis.alignment_score) / 100}
                        className="text-blue-600 transition-all duration-1000 ease-out" />
                    </svg>
                    <span className="absolute text-xl font-black text-slate-900">{insights.protocol_analysis.alignment_score}%</span>
                  </div>
                  <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Protocol Alignment</span>
                </div>
                
                <div className="flex-grow space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-[10px] font-black uppercase tracking-widest">
                      {insights.protocol_analysis.protocol_name}
                    </div>
                    <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border
                      ${insights.protocol_analysis.alignment_status === 'High' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 
                        insights.protocol_analysis.alignment_status === 'Moderate' ? 'bg-amber-50 text-amber-700 border-amber-100' : 'bg-red-50 text-red-700 border-red-100'}`}>
                      {insights.protocol_analysis.alignment_status} Alignment
                    </div>
                  </div>
                  <h4 className="text-lg font-bold text-slate-900">Agentic Protocol Validation Reasoning</h4>
                  <p className="text-sm text-slate-600 leading-relaxed font-medium">
                    {insights.protocol_analysis.reasoning}
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                    <div className="p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                      <h5 className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-2">Medication Alignment</h5>
                      <p className="text-xs text-slate-700 font-bold">{insights.protocol_analysis.medication_alignment}</p>
                    </div>
                    <div className="p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                      <h5 className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-2">Research Hypothesis</h5>
                      <p className="text-xs text-slate-700 font-bold">{insights.protocol_analysis.suggested_hypothesis}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card p-8 border-t-4 border-t-blue-600 shadow-md">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Cohort Size</p>
                  <p className="text-4xl font-extrabold text-slate-900 tracking-tight">{cohortResult.total_patients}</p>
                </div>
                <div className="p-3 bg-blue-50 rounded-2xl">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="card p-8 border-t-4 border-t-emerald-600 shadow-md">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Avg. Age</p>
                  <p className="text-4xl font-extrabold text-slate-900 tracking-tight">{cohortResult.statistics.age?.mean || 'N/A'}</p>
                </div>
                <div className="p-3 bg-emerald-50 rounded-2xl">
                  <TrendingUp className="w-6 h-6 text-emerald-600" />
                </div>
              </div>
            </div>

            <div className="card p-8 border-t-4 border-t-indigo-600 shadow-md">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Avg. BMI</p>
                  <p className="text-4xl font-extrabold text-slate-900 tracking-tight">{cohortResult.statistics.avg_bmi || 'N/A'}</p>
                </div>
                <div className="p-3 bg-indigo-50 rounded-2xl">
                  <FlaskConical className="w-6 h-6 text-indigo-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Table Card */}
          <div className="card shadow-xl shadow-slate-200/30">
            <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/30">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Verified Patient Records</h4>
              </div>
              <button className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-[10px] font-black text-slate-600 flex items-center gap-2 hover:bg-slate-50 transition-all shadow-sm">
                <Download className="w-3.5 h-3.5" /> EXPORT DATA
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/20">
                    <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Identifier</th>
                    <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Condition & Risk</th>
                    <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Vitals</th>
                    <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Medication</th>
                    <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Patient Outcome</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {cohortResult.patients.slice(0, visibleRecords).map((p: any, i: number) => (
                    <tr key={i} className="hover:bg-blue-50/30 transition-all duration-300 group">
                      <td className="px-8 py-5">
                        <div className="space-y-1">
                          <p className="text-sm font-bold text-slate-700 tabular-nums">#{ (p.patient_id || i + 1).toString().slice(-6) }</p>
                          <p className="text-[10px] font-medium text-slate-400">{p.age}y • {p.gender || 'N/A'}</p>
                        </div>
                      </td>
                      <td className="px-8 py-5">
                        <div className="space-y-2">
                          <p className="text-sm text-slate-800 font-bold group-hover:text-blue-700 transition-colors">
                            {p.disease}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter border
                              ${p.risk_level === 'Critical' ? 'bg-red-50 text-red-600 border-red-100' : 
                                p.risk_level === 'High' ? 'bg-orange-50 text-orange-600 border-orange-100' : 
                                p.risk_level === 'Moderate' ? 'bg-amber-50 text-amber-600 border-amber-100' : 
                                'bg-emerald-50 text-emerald-600 border-emerald-100'}`}>
                              {p.risk_level} Risk
                            </span>
                            {p.risk_factors?.slice(0, 2).map((f: string) => (
                              <span key={f} className="px-2 py-0.5 bg-slate-100 text-slate-500 rounded text-[8px] font-bold uppercase tracking-tighter">
                                {f}
                              </span>
                            ))}
                          </div>
                        </div>
                      </td>
                      <td className="px-8 py-5">
                        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                          <div className="flex items-center gap-1.5">
                            <span className="text-[9px] font-black text-slate-400 uppercase">BMI</span>
                            <span className={`text-xs font-bold ${p.bmi > 30 ? 'text-red-600' : 'text-slate-700'}`}>{p.bmi}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-[9px] font-black text-slate-400 uppercase">GLU</span>
                            <span className={`text-xs font-bold ${p.blood_sugar > 140 ? 'text-red-600' : 'text-slate-700'}`}>{p.blood_sugar}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-8 py-5 text-sm text-slate-500 font-medium italic">
                        {p.medication}
                      </td>
                      <td className="px-8 py-5">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border
                          ${p.outcome?.toLowerCase() === 'recovered' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 
                            p.outcome?.toLowerCase() === 'improved' ? 'bg-blue-50 text-blue-700 border-blue-100' : 'bg-slate-50 text-slate-600 border-slate-100'}`}>
                          {p.outcome}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="px-8 py-6 bg-slate-50/30 border-t border-slate-100 flex items-center justify-between">
                <div className="flex flex-col gap-1">
                  <span className="text-xs text-slate-400 font-bold italic">
                    Showing {Math.min(visibleRecords, cohortResult.total_patients)} results out of {cohortResult.total_patients} matching records
                  </span>
                  {visibleRecords < cohortResult.total_patients && (
                    <button 
                      onClick={() => setVisibleRecords(prev => prev + 10)}
                      className="text-[10px] font-black text-blue-600 uppercase tracking-widest hover:text-blue-700 transition-colors text-left flex items-center gap-1 group/btn"
                    >
                      Show More Records 
                      <ChevronRight className="w-3 h-3 group-hover/btn:translate-x-0.5 transition-transform" />
                    </button>
                  )}
                </div>
                <div className="flex gap-2">
                   {[...Array(Math.min(5, Math.ceil(cohortResult.total_patients / 10)))].map((_, i) => (
                     <div key={i} className={`w-2 h-2 rounded-full transition-all duration-300 ${i === Math.floor((visibleRecords - 1) / 10) ? 'bg-blue-600 w-4' : 'bg-slate-200'}`}></div>
                   ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CohortAnalysis;
