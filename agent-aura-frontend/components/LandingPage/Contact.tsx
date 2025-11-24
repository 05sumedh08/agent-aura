'use client';

export default function Contact() {
    return (
        <section id="contact" className="py-24 relative">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <h2 className="text-3xl md:text-4xl font-bold mb-8 text-white">
                    Get in Touch
                </h2>

                <div className="glass-card p-10 rounded-3xl">
                    <p className="text-xl text-gray-300 mb-8">
                        Interested in learning more about Agent Aura or deploying it in your school?
                        We'd love to hear from you.
                    </p>

                    <div className="inline-flex items-center justify-center space-x-3 px-8 py-4 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-colors cursor-pointer group">
                        <svg className="w-6 h-6 text-aura-primary group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <a href="mailto:zenshiro@example.com" className="text-xl font-medium text-white">
                            zenshiro@example.com
                        </a>
                    </div>

                    <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                        <div className="p-4 rounded-xl bg-white/5">
                            <h4 className="font-bold text-white mb-2">Support</h4>
                            <p className="text-sm text-gray-400">Technical assistance and troubleshooting for your deployment.</p>
                        </div>
                        <div className="p-4 rounded-xl bg-white/5">
                            <h4 className="font-bold text-white mb-2">Sales</h4>
                            <p className="text-sm text-gray-400">Enterprise licensing and custom integration solutions.</p>
                        </div>
                        <div className="p-4 rounded-xl bg-white/5">
                            <h4 className="font-bold text-white mb-2">Demo</h4>
                            <p className="text-sm text-gray-400">Schedule a live walkthrough of the Agent Aura platform.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
