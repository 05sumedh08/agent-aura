'use client';

export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-12">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-aura-primary/20 rounded-full" />
        <div className="absolute top-0 left-0 w-16 h-16 border-4 border-aura-primary border-t-transparent rounded-full animate-spin" />
      </div>
    </div>
  );
}
