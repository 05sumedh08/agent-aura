'use client';

import Navbar from '@/components/LandingPage/Navbar';
import Hero from '@/components/LandingPage/Hero';
import Features from '@/components/LandingPage/Features';
import Footer from '@/components/LandingPage/Footer';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f0a1e] via-[#1a1236] to-[#1e1b4b] text-white selection:bg-aura-primary/30">
      <Navbar />
      <main>
        <Hero />
        <Features />
      </main>
      <Footer />
    </div>
  );
}
