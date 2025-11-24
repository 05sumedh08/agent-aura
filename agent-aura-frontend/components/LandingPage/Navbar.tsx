'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/store';
import { useEffect, useState } from 'react';

export default function Navbar() {
    const { isAuthenticated, user } = useAuth();
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'glass-dark py-3' : 'bg-transparent py-5'
            }`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-aura-primary to-aura-secondary flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24">
                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-300">
                        Agent Aura
                    </span>
                </div>

                <div className="flex items-center space-x-4">
                    {isAuthenticated ? (
                        <Link
                            href={user?.role === 'admin' ? '/admin' : user?.role === 'teacher' ? '/teacher' : '/student'}
                            className="btn-primary"
                        >
                            Dashboard
                        </Link>
                    ) : (
                        <Link href="/login" className="btn-primary">
                            Login
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
}
