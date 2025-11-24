'use client';

export default function About() {
    return (
        <section id="about" className="py-24 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-aura-primary/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 translate-y-1/2 -translate-x-1/2 w-96 h-96 bg-aura-accent/10 rounded-full blur-3xl" />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                    <div>
                        <h2 className="text-3xl md:text-4xl font-bold mb-6 text-white">
                            Transforming Education with <span className="gradient-text">Intelligent Agents</span>
                        </h2>

                        <div className="space-y-8">
                            <div className="glass p-6 rounded-xl border-l-4 border-aura-primary">
                                <h3 className="text-xl font-semibold text-white mb-2">The Challenge</h3>
                                <p className="text-gray-300">
                                    K-12 schools face critical challenges: detection lag in identifying at-risk students,
                                    communication delays between stakeholders, and a lack of measurable outcome data for interventions.
                                </p>
                            </div>

                            <div className="glass p-6 rounded-xl border-l-4 border-aura-secondary">
                                <h3 className="text-xl font-semibold text-white mb-2">Our Solution</h3>
                                <p className="text-gray-300">
                                    Agent Aura employs a multi-agent AI system where specialized agents work in parallel to
                                    collect data, analyze risk, plan interventions, and predict outcomes in real-time.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="glass-card p-8 rounded-2xl relative z-10">
                            <h3 className="text-2xl font-bold text-white mb-6">System Architecture</h3>

                            <div className="space-y-4">
                                <div className="flex items-center p-4 rounded-lg bg-white/5 border border-white/10">
                                    <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 mr-4">
                                        1
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-white">Orchestrator Agent</h4>
                                        <p className="text-sm text-gray-400">Coordinates the entire workflow</p>
                                    </div>
                                </div>

                                <div className="flex items-center p-4 rounded-lg bg-white/5 border border-white/10">
                                    <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 mr-4">
                                        2
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-white">Risk Analysis Agent</h4>
                                        <p className="text-sm text-gray-400">Evaluates student data for risk factors</p>
                                    </div>
                                </div>

                                <div className="flex items-center p-4 rounded-lg bg-white/5 border border-white/10">
                                    <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400 mr-4">
                                        3
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-white">Intervention Agent</h4>
                                        <p className="text-sm text-gray-400">Designs personalized support plans</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Decorative elements behind the card */}
                        <div className="absolute -top-4 -right-4 w-full h-full border-2 border-white/10 rounded-2xl -z-10" />
                        <div className="absolute -bottom-4 -left-4 w-full h-full border-2 border-white/10 rounded-2xl -z-10" />
                    </div>
                </div>
            </div>
        </section>
    );
}
