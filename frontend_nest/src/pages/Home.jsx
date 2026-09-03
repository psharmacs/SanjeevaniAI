import { Link } from 'react-router-dom';
import { Shield, Eye } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[#f8f9fa] text-[#3c4043] font-sans">
      <section className="relative flex-1 flex flex-col items-center justify-center min-h-[90vh] px-4">
        
        <div className="relative z-10 text-center max-w-4xl mx-auto">
          <div className="flex flex-col items-center justify-center mb-8">
            <div className="p-6 bg-white rounded-3xl shadow-sm border border-gray-100 mb-6">
              <Shield className="w-16 h-16 text-green-600" />
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight mb-6 text-gray-900">
            A silent guardian that <br/>
            sees, understands, and responds.
          </h1>
          
          <p className="text-xl text-gray-500 mb-10 max-w-2xl mx-auto leading-relaxed">
            Sanjeevani AI is an intelligent monitoring system designed to protect your loved ones. 
            It doesn't just record—it actively analyzes posture, movement, and behavior to detect emergencies instantly.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link 
              to="/guardian" 
              className="px-8 py-4 bg-white text-gray-900 font-medium rounded-full flex items-center gap-2 transition-all shadow-md hover:shadow-lg border border-gray-100"
            >
              <Shield className="w-5 h-5 text-green-600" />
              Open Guardian View
            </Link>
            <Link 
              to="/live" 
              className="px-8 py-4 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-full flex items-center gap-2 transition-all"
            >
              <Eye className="w-5 h-5" />
              Raw Camera Feed
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

