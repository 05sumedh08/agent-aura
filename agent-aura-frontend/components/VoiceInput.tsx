import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface VoiceInputProps {
  onResponse: (text: string, data: any) => void;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onResponse }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      // @ts-ignore
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = false;
        recognitionInstance.interimResults = false;
        recognitionInstance.lang = 'en-US';

        recognitionInstance.onstart = () => {
          setIsListening(true);
        };

        recognitionInstance.onend = () => {
          setIsListening(false);
        };

        recognitionInstance.onresult = (event: any) => {
          const text = event.results[0][0].transcript;
          setTranscript(text);
          handleVoiceQuery(text);
        };

        setRecognition(recognitionInstance);
      }
    }
  }, []);

  const handleVoiceQuery = async (text: string) => {
    setIsProcessing(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/v1/voice/query',
        { text },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const { response_text, data, audio_base64 } = response.data;
      onResponse(response_text, data);

      if (audio_base64) {
        playAudio(audio_base64);
      } else {
        speakResponse(response_text);
      }
    } catch (error) {
      console.error('Error processing voice query:', error);
      onResponse("Sorry, I encountered an error processing your request.", null);
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudio = (base64String: string) => {
    const audio = new Audio(`data:audio/mpeg;base64,${base64String}`);
    audio.play().catch(e => console.error("Error playing audio:", e));
  };

  const speakResponse = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const toggleListening = () => {
    if (isListening) {
      recognition?.stop();
    } else {
      setTranscript('');
      recognition?.start();
    }
  };

  if (!recognition) {
    return null; // Web Speech API not supported
  }

  return (
    <div className="relative">
      <button
        onClick={toggleListening}
        className={`p-2 rounded-full transition-all duration-300 ${isListening
            ? 'bg-red-500 animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.5)]'
            : 'bg-indigo-600 hover:bg-indigo-700'
          } text-white`}
        title="Voice Assistant"
      >
        {isProcessing ? (
          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        )}
      </button>

      {/* Transcript Tooltip */}
      {transcript && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-gray-800 text-white text-sm p-3 rounded-lg shadow-xl z-50 border border-gray-700">
          <p className="font-semibold text-gray-400 text-xs mb-1">You said:</p>
          <p>"{transcript}"</p>
        </div>
      )}
    </div>
  );
};

export default VoiceInput;
