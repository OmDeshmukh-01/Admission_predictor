import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Crosshair, GraduationCap, ExternalLink } from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();
    
    const links = [
        { path: '/', label: 'Home', icon: <GraduationCap className="w-5 h-5" /> },
        { path: '/predict', label: 'Predictor', icon: <Crosshair className="w-5 h-5" /> },
        { path: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> }
    ];

    return (
        <div className="w-64 bg-surface border-r border-white/10 h-screen fixed flex flex-col pt-8">
            <div className="px-8 pb-8 flex items-center space-x-3">
                <div className="bg-primary p-2 rounded-lg">
                    <GraduationCap className="text-white w-6 h-6" />
                </div>
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                    AdmitScope
                </h1>
            </div>
            
            <nav className="flex-1 px-4 space-y-2">
                {links.map((link) => {
                    const active = location.pathname === link.path;
                    return (
                        <Link key={link.path} to={link.path} className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${active ? 'bg-primary/10 text-primary border border-primary/20' : 'text-textMuted hover:bg-white/5 hover:text-white'}`}>
                            {link.icon}
                            <span className="font-medium">{link.label}</span>
                        </Link>
                    )
                })}
            </nav>
            
            <div className="p-6">
                <div className="glass-card p-4 flex items-center justify-center space-x-2 text-sm text-textMuted cursor-pointer hover:text-white transition-colors">
                    <ExternalLink className="w-4 h-4" />
                    <span>View Project</span>
                </div>
            </div>
        </div>
    );
};

const BaseLayout = ({ children }) => {
    return (
        <div className="flex bg-background min-h-screen text-textMain font-sans">
            <Sidebar />
            <div className="ml-64 flex-1">
                <main className="p-8">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default BaseLayout;
