'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/store';

export default function Hero() {
    const { isAuthenticated, user } = useAuth();

    const ctaLink = isAuthenticated
        ? (user?.role === 'admin' ? '/admin' : user?.role === 'teacher' ? '/teacher' : '/student')
        : '/login';

    return (
        <section className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-aura-primary/20 rounded-full blur-3xl animate-pulse-slow" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-aura-secondary/20 rounded-full blur-3xl animate-pulse-slow delay-1000" />
            </div>

            <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <div className="animate-slide-up">
                    <div className="inline-block mb-4 px-4 py-1.5 rounded-full glass border border-white/10 text-sm font-medium text-aura-accent">
                        ✨ Revolutionizing Education with AI
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
                        <span className="block text-white mb-2">Unlock Your Potential</span>
                        <span className="block gradient-text">With Agent Aura</span>
                    </h1>

                    <p className="max-w-2xl mx-auto text-lg md:text-xl text-gray-300 mb-10 leading-relaxed">
                        Experience the future of learning with our AI-powered platform.
                        Real-time analytics, personalized insights, and seamless collaboration
                        for students, teachers, and administrators.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link
                            href={ctaLink}
                            className="btn-primary text-lg px-8 py-4 min-w-[200px] hover-scale group"
                        >
                            Get Started
                            <span className="inline-block ml-2 transition-transform group-hover:translate-x-1">→</span>
                        </Link>
                        <a
                            href="#features"
                            className="btn-secondary text-lg px-8 py-4 min-w-[200px] hover-scale bg-white/5 border-white/10 text-white hover:bg-white/10"
                        >
                            Learn More
                        </a>
                    </div>
                </div>

                {/* Floating Cards Preview */}
                <div className="mt-20 relative max-w-5xl mx-auto hidden md:block animate-fade-in delay-500">
                    <div className="glass-card rounded-2xl p-1 border border-white/10 shadow-2xl transform rotate-x-12 perspective-1000">
                        <div className="bg-gray-900/50 rounded-xl overflow-hidden aspect-video relative">
                            <div className="absolute inset-0 flex items-center justify-center text-gray-500">
                                <div className="text-center">
                                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
                                        <svg className="w-8 h-8 text-aura-primary" fill="none" viewBox="0 0 24 24">
                                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                        </svg>
                                    </div>
                                    <p>Interactive Dashboard Preview</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
