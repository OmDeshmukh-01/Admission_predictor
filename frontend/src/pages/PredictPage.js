import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Target, TrendingUp, AlertCircle, Info } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from 'recharts';

const PredictPage = () => {
    const [formData, setFormData] = useState({
        gre_score: 310,
        toefl_score: 105,
        university_rating: 3,
        sop: 3.5,
        lor: 3.5,
        cgpa: 8.5,
        research: 0
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) });
    };

    const predict = async () => {
        setLoading(true);
        setError('');
        try {
            const res = await axios.post('http://localhost:8000/api/predict/', formData);
            setResult(res.data);
        } catch (err) {
            setError('Prediction failed. Ensure backend models are trained and server is running.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Auto-predict on form change with a simple debounce
    useEffect(() => {
        const timer = setTimeout(() => {
            predict();
        }, 500);
        return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [formData]);

    const InputSlider = ({ label, name, min, max, step }) => (
        <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
                <label className="text-textMuted font-medium">{label}</label>
                <div className="bg-white/5 px-3 py-1 rounded text-white font-mono">{formData[name]}</div>
            </div>
            <input 
                type="range" name={name} min={min} max={max} step={step}
                value={formData[name]} onChange={handleChange}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary"
            />
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div>
                <h1 className="text-3xl font-bold mb-2">Admit Predictor & What-If Analysis</h1>
                <p className="text-textMuted">Adjust the sliders to see how your chances change in real-time.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Form Section */}
                <div className="lg:col-span-4 glass-card p-6 space-y-6">
                    <h3 className="text-lg font-semibold flex items-center gap-2 border-b border-white/5 pb-3">
                        <Target className="w-5 h-5 text-primary" /> Profile Parameters
                    </h3>
                    
                    <InputSlider label="GRE Score" name="gre_score" min={290} max={340} step={1} />
                    <InputSlider label="TOEFL Score" name="toefl_score" min={92} max={120} step={1} />
                    <InputSlider label="CGPA (out of 10.0)" name="cgpa" min={6.8} max={9.92} step={0.01} />
                    <InputSlider label="University Rating" name="university_rating" min={1} max={5} step={1} />
                    <InputSlider label="Statement of Purpose (SOP)" name="sop" min={1} max={5} step={0.5} />
                    <InputSlider label="Letter of Recommendation (LOR)" name="lor" min={1} max={5} step={0.5} />
                    
                    <div className="space-y-2">
                        <label className="text-sm text-textMuted font-medium">Research Experience</label>
                        <div className="flex gap-4">
                            <label className="flex items-center space-x-2 cursor-pointer">
                                <input type="radio" name="research" value={1} checked={formData.research === 1} onChange={handleChange} className="accent-primary" />
                                <span>Yes</span>
                            </label>
                            <label className="flex items-center space-x-2 cursor-pointer">
                                <input type="radio" name="research" value={0} checked={formData.research === 0} onChange={handleChange} className="accent-primary" />
                                <span>No</span>
                            </label>
                        </div>
                    </div>
                </div>

                {/* Results Section */}
                <div className="lg:col-span-8 flex flex-col space-y-8">
                    {/* Top Result Card */}
                    <div className="glass-card p-8 flex flex-col md:flex-row items-center justify-between gap-8 h-48 relative overflow-hidden">
                        {loading && (
                            <div className="absolute inset-0 bg-surface/50 backdrop-blur-sm z-10 flex items-center justify-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                            </div>
                        )}
                        <div className="flex-1 space-y-2 relative z-20">
                            <h2 className="text-lg font-medium text-textMuted uppercase tracking-wider">Admission Chance</h2>
                            <div className="flex items-baseline gap-3">
                                <span className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                                    {result ? result.percentage.toFixed(1) : '--'}%
                                </span>
                                {result && <span className={`px-3 py-1 rounded-full text-sm font-medium ${result.category === 'Safe' ? 'bg-green-500/20 text-green-400' : result.category === 'Moderate' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                                    {result.category}
                                </span>}
                            </div>
                            {error && <p className="text-red-400 text-sm flex items-center gap-1 mt-2"><AlertCircle className="w-4 h-4" /> {error}</p>}
                        </div>

                        {/* Circular Progress (Simplified UI representation) */}
                        <div className="relative w-32 h-32 flex-shrink-0 z-20">
                            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="45" className="stroke-slate-700" strokeWidth="8" fill="none" />
                                <circle cx="50" cy="50" r="45" className="stroke-primary transition-all duration-1000 ease-out" strokeWidth="8" fill="none" 
                                    strokeDasharray="283" strokeDashoffset={result ? 283 - (283 * result.percentage) / 100 : 283} strokeLinecap="round" />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center flex-col">
                                <Target className="w-6 h-6 text-primary/80" />
                            </div>
                        </div>
                    </div>

                    {/* AI Explanation / SHAP Chart */}
                    <div className="glass-card p-6 flex-1 flex flex-col">
                        <h3 className="text-lg font-semibold flex items-center gap-2 mb-6">
                            <TrendingUp className="w-5 h-5 text-secondary" /> Feature Impact (Explainable AI)
                        </h3>
                        {result && result.shap_contributions ? (
                            <div className="flex-1 min-h-[250px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={result.shap_contributions} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#ffffff10" />
                                        <XAxis type="number" stroke="#94a3b8" />
                                        <YAxis dataKey="feature" type="category" width={100} stroke="#94a3b8" tick={{fontSize: 12}} />
                                        <Tooltip 
                                            contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
                                            formatter={(val) => [val > 0 ? `+${(val*100).toFixed(2)}%` : `${(val*100).toFixed(2)}%`, "Impact"]}
                                        />
                                        <Bar dataKey="contribution" radius={4}>
                                            {result.shap_contributions.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.contribution > 0 ? '#10b981' : '#ef4444'} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <div className="flex-1 flex items-center justify-center text-textMuted h-[250px] border border-dashed border-white/10 rounded-xl">
                                <p className="flex items-center gap-2"><Info className="w-4 h-4" /> Change values to generate explainability chart</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PredictPage;
