import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';
import { Users, Target, BookOpen, GraduationCap } from 'lucide-react';

const KPICard = ({ title, value, icon: Icon, color }) => (
    <div className="glass-card p-6 flex flex-col space-y-4">
        <div className="flex justify-between items-center">
            <h3 className="text-textMuted font-medium">{title}</h3>
            <div className={`p-2 rounded-lg bg-${color}-500/10 text-${color}-400`}>
                <Icon className="w-5 h-5" />
            </div>
        </div>
        <div className="text-3xl font-bold">{value}</div>
    </div>
);

const DashboardPage = () => {
    const [kpis, setKpis] = useState(null);
    const [dist, setDist] = useState(null);
    const [scatter, setScatter] = useState(null);
    const [loading, setLoading] = useState(true);

    const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchData = async () => {
            try {
                const kpiRes = await axios.get(`${API}/api/analytics/kpis`);
                const distRes = await axios.get(`${API}/api/analytics/distributions`);
                const scatterRes = await axios.get(`${API}/api/analytics/scatter`);
                
                setKpis(kpiRes.data);
                setDist(distRes.data);
                setScatter(scatterRes.data);
            } catch (error) {
                console.error("Error fetching analytics", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div className="flex h-64 items-center justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div>
                <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
                <p className="text-textMuted">Overview of applicant data and ML metrics</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <KPICard title="Total Applicants" value={kpis?.total_students} icon={Users} color="blue" />
                <KPICard title="Avg Admit Chance" value={`${kpis?.avg_admit_chance}%`} icon={Target} color="green" />
                <KPICard title="Average GRE" value={kpis?.avg_gre} icon={GraduationCap} color="purple" />
                <KPICard title="Research Exp." value={`${kpis?.research_percentage}%`} icon={BookOpen} color="yellow" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-6 pb-2 border-b border-white/5">GRE Score Distribution</h3>
                    <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={dist?.gre_distribution}>
                                <defs>
                                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                <XAxis dataKey="range" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f8fafc' }} />
                                <Area type="monotone" dataKey="count" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCount)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-6 pb-2 border-b border-white/5">GRE vs Admit Chance</h3>
                    <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <ScatterChart>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                <XAxis type="number" dataKey="GRE Score" name="GRE Score" domain={['auto', 'auto']} stroke="#94a3b8" />
                                <YAxis type="number" dataKey="Chance of Admit" name="Chance (%)" domain={['auto', 'auto']} stroke="#94a3b8" />
                                <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                                <Scatter name="Students" data={scatter} fill="#8b5cf6" opacity={0.6} />
                            </ScatterChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
