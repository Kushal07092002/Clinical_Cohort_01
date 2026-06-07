import React, { useState, useRef } from 'react';
import CohortAnalysis from './components/CohortAnalysis';
import ChatBox from './components/ChatBox';
import { Upload, FileText, Activity, Layers, CheckCircle, MessageSquare } from 'lucide-react';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [session, setSession] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      console.log('Uploading file:', file.name);
      const response = await fetch('/api/upload/', { method: 'POST', body: formData });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errData.detail || 'Upload failed');
      }
      const data = await response.json();
      console.log('Upload successful:', data);
      setSession(data);
    } catch (error: any) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fcfcfd] text-slate-900 font-sans antialiased">
      {/* Navigation */}
      <nav className="border-b border-slate-200/60 bg-white/70 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-[1440px] mx-auto px-8 h-18 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-xl shadow-sm shadow-blue-200">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight text-slate-900">Clinical AI</span>
          </div>
          {session && (
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 rounded-full border border-emerald-100">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span className="text-xs font-semibold text-emerald-700 tracking-tight">
                  {session.filename}
                </span>
              </div>
              <button 
                onClick={() => {setSession(null); setFile(null);}}
                className="text-xs font-bold text-slate-400 hover:text-red-500 transition-colors uppercase tracking-widest"
              >
                Reset
              </button>
            </div>
          )}
        </div>
      </nav>

      <main className="max-w-[1440px] mx-auto px-8 py-16">
        {!session ? (
          <div className="max-w-2xl mx-auto mt-20">
            <div className="text-center mb-16">
              <h1 className="text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">
                Clinical Cohort Analysis
              </h1>
              <p className="text-lg text-slate-500 max-w-lg mx-auto leading-relaxed">
                Transform raw clinical data into actionable patient insights with our agentic AI platform.
              </p>
            </div>

            <div 
              onClick={() => fileInputRef.current?.click()}
              className={`group relative border-2 border-dashed rounded-3xl p-20 transition-all cursor-pointer bg-white
                ${file ? 'border-blue-400 bg-blue-50/20 shadow-inner' : 'border-slate-200 hover:border-blue-400 hover:bg-slate-50/50'}`}
            >
              <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".csv" />
              
              <div className="flex flex-col items-center">
                <div className={`w-20 h-20 rounded-2xl flex items-center justify-center mb-8 transition-all duration-300 group-hover:scale-105 group-hover:rotate-3
                  ${file ? 'bg-blue-600 text-white shadow-xl shadow-blue-200' : 'bg-slate-50 text-slate-400 border border-slate-100'}`}>
                  {file ? <FileText className="w-10 h-10" /> : <Upload className="w-10 h-10" />}
                </div>
                
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  {file ? file.name : 'Choose a clinical dataset'}
                </h3>
                <p className="text-base text-slate-400 font-medium">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : 'CSV files only • Max 50MB'}
                </p>
              </div>
            </div>

            {file && (
              <button 
                onClick={handleUpload}
                disabled={uploading}
                className="w-full mt-10 btn-primary h-14 text-lg font-bold shadow-xl shadow-blue-500/20"
              >
                {uploading ? 'Processing Dataset...' : 'Begin Analysis'}
              </button>
            )}
            
            <div className="mt-24 flex items-center justify-center gap-12 opacity-30 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-500">
              <div className="flex flex-col items-center gap-3">
                <Layers className="w-6 h-6" />
                <span className="text-[10px] uppercase tracking-[0.2em] font-black">Cohorts</span>
              </div>
              <div className="w-px h-8 bg-slate-300"></div>
              <div className="flex flex-col items-center gap-3">
                <Activity className="w-6 h-6" />
                <span className="text-[10px] uppercase tracking-[0.2em] font-black">Outcomes</span>
              </div>
              <div className="w-px h-8 bg-slate-300"></div>
              <div className="flex flex-col items-center gap-3">
                <CheckCircle className="w-6 h-6" />
                <span className="text-[10px] uppercase tracking-[0.2em] font-black">Validation</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="duration-700">
            <div className="mb-12 border-b border-slate-100 pb-10">
              <div className="flex items-center gap-3 text-blue-600 mb-2">
                <Activity className="w-5 h-5" />
                <span className="text-xs font-bold uppercase tracking-widest">Live Analysis</span>
              </div>
              <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-3">Clinical Dashboard</h2>
              <p className="text-slate-500 text-base max-w-2xl">
                Analysis of <span className="text-slate-900 font-semibold">{session.rows}</span> patient records across <span className="text-slate-900 font-semibold">{session.columns.length}</span> clinical parameters.
              </p>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
              <div className="lg:col-span-2">
                <CohortAnalysis sessionId={session.session_id} />
              </div>
              <div className="lg:col-span-1 sticky top-24">
                <ChatBox sessionId={session.session_id} />
              </div>
            </div>
          </div>
        )}
      </main>
      
      <footer className="py-20 text-center">
        <div className="flex items-center justify-center gap-2 mb-4 opacity-20">
          <Activity className="w-4 h-4" />
          <div className="h-px w-12 bg-slate-400"></div>
          <Layers className="w-4 h-4" />
        </div>
        <p className="text-[10px] text-slate-400 uppercase tracking-[0.3em] font-bold">
          Standard Clinical Protocol &copy; 2026
        </p>
      </footer>
    </div>
  );
}

export default App;
