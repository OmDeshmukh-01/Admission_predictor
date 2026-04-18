import React from 'react';
import { ArrowRight, CheckCircle2, BarChart2, Shield, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const FeatureCard = ({ icon: Icon, title, description }) => (
    <div className="glass-card p-6 flex flex-col items-center text-center space-y-4 hover:border-primary/50 transition-colors">
        <div className="p-4 bg-primary/10 rounded-full text-primary">
            <Icon className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-semibold">{title}</h3>
        <p className="text-textMuted">{description}</p>
    </div>
);

const LandingPage = () => {
    return (
        <div className="space-y-24 animate-in fade-in duration-1000">
            {/* Hero Section */}
            <div className="relative pt-20 pb-16 flex flex-col items-center text-center max-w-4xl mx-auto space-y-8">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary/20 blur-[120px] rounded-full pointer-events-none" />
                
                <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight">
                    Data-Driven <br />
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">
                        Graduate Admissions
                    </span>
                </h1>
                
                <p className="text-xl text-textMuted max-w-2xl">
                    AdmitScope leverages advanced Machine Learning and Explainable AI to predict your university admission chances with enterprise-grade accuracy.
                </p>

                <div className="flex gap-4 pt-4">
                    <Link to="/predict" className="px-8 py-4 bg-primary hover:bg-primary/90 text-white rounded-xl font-semibold flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)]">
                        Start Prediction <ArrowRight className="w-5 h-5" />
                    </Link>
                    <Link to="/dashboard" className="px-8 py-4 bg-surface hover:bg-surface/80 border border-white/10 text-white rounded-xl font-semibold transition-all">
                        View Analytics
                    </Link>
                </div>
            </div>

            {/* Features Section */}
            <div className="max-w-6xl mx-auto space-y-12 pb-20">
                <div className="text-center space-y-4">
                    <h2 className="text-3xl md:text-4xl font-bold">Why Choose AdmitScope</h2>
                    <p className="text-textMuted">Built for data science portfolios and real-world applicants.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <FeatureCard 
                        icon={Zap}
                        title="Real-time What-If Analysis"
                        description="Adjust your GRE, TOEFL, and CGPA scores on the fly to see how your chances change instantly."
                    />
                    <FeatureCard 
                        icon={BarChart2}
                        title="Explainable AI (SHAP)"
                        description="Understand why you got your score. See the exact contribution of each profile feature to your final prediction."
                    />
                    <FeatureCard 
                        icon={Shield}
                        title="State of the Art Models"
                        description="Powered by XGBoost, Random Forest, and Deep Neural Networks (ANN) trained on historical applicant data."
                    />
                </div>
            </div>
            
            {/* Footer Mock */}
            <div className="border-t border-white/10 py-12 text-center text-textMuted flex flex-col items-center gap-4">
                <div className="flex items-center space-x-2 text-white">
                    <CheckCircle2 className="w-5 h-5 text-primary" />
                    <span className="font-semibold text-lg">AdmitScope Pro</span>
                </div>
                <p>Designed for elite portfolios and data professionals.</p>
                <p className="text-sm opacity-50">&copy; 2026 AdmitScope. All rights reserved.</p>
            </div>
        </div>
    );
};

export default LandingPage;
