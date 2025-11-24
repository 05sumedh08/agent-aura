'use client';

export default function Footer() {
    return (
        <footer className="relative border-t border-white/10 bg-black/20 backdrop-blur-lg mt-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    <div className="mb-4 md:mb-0">
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                            Agent Aura
                        </span>
                        <p className="text-gray-500 text-sm mt-2">
                            Empowering education through artificial intelligence.
                        </p>
                    </div>

                    <div className="flex space-x-6">
                        <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy</a>
                        <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms</a>
                        <a href="#" className="text-gray-400 hover:text-white transition-colors">Contact</a>
                    </div>
                </div>

                <div className="mt-8 pt-8 border-t border-white/5 text-center text-gray-600 text-sm">
                    &copy; {new Date().getFullYear()} Agent Aura. All rights reserved.
                </div>
            </div>
        </footer>
    );
}
