import { motion } from 'framer-motion';
import { Shield, ArrowRight, Eye, Brain, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative flex-1 flex flex-col items-center justify-center min-h-[90vh] px-4 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-gray-950" />
          
          {/* Subtle Grid Background */}
          <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
          
          {/* Glowing Orbs */}
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-900/20 rounded-full blur-[128px]" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-teal-900/10 rounded-full blur-[128px]" />
          
          {/* Scanning Line Animation (CSS only) */}
          <motion.div 
            className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent"
            animate={{ top: ["0%", "100%", "0%"] }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          />
        </div>
        
        <motion.div 
          className="relative z-10 text-center max-w-4xl mx-auto"
          initial="initial"
          animate="animate"
          variants={{
            initial: { opacity: 0 },
            animate: { opacity: 1, transition: { staggerChildren: 0.2 } }
          }}
        >
          <motion.div variants={fadeIn} className="flex flex-col items-center justify-center mb-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-sm font-medium mb-8">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Built for Smart India Hackathon
            </div>
            <div className="p-4 bg-gray-900/50 rounded-2xl border border-gray-800 backdrop-blur-md shadow-2xl">
              <Shield className="w-16 h-16 text-emerald-400" />
            </div>
          </motion.div>
          
          <motion.h1 variants={fadeIn} className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
            A silent guardian that <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-200">
              sees, understands, and responds.
            </span>
          </motion.h1>
          
          <motion.p variants={fadeIn} className="text-xl md:text-2xl text-gray-400 mb-10 max-w-2xl mx-auto font-light leading-relaxed">
            Sanjeevani AI is an intelligent monitoring system designed to protect the elderly. 
            It doesn't just record—it actively analyzes posture, movement, and behavior to detect emergencies instantly.
          </motion.p>
          
          <motion.div variants={fadeIn} className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link 
              to="/guardian" 
              className="px-8 py-4 bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-semibold rounded-full flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)]"
            >
              <Shield className="w-5 h-5" />
              Guardian Dashboard
            </Link>
            <Link 
              to="/live" 
              className="px-8 py-4 bg-gray-900 hover:bg-gray-800 text-white font-semibold rounded-full border border-gray-700 flex items-center gap-2 transition-all"
            >
              <Eye className="w-5 h-5" />
              Live Raw Feed
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Story Section */}
      <section className="py-24 bg-gray-950 border-t border-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="flex flex-col items-start">
              <div className="p-3 bg-gray-900 rounded-xl mb-6">
                <Eye className="w-8 h-8 text-amber-400" />
              </div>
              <h3 className="text-2xl font-semibold mb-4">Continuous Awareness</h3>
              <p className="text-gray-400 leading-relaxed">
                A normal camera only records after the fact. Sanjeevani AI uses advanced computer vision to constantly observe the environment, remaining calm during normal activity.
              </p>
            </div>
            <div className="flex flex-col items-start">
              <div className="p-3 bg-gray-900 rounded-xl mb-6">
                <Brain className="w-8 h-8 text-emerald-400" />
              </div>
              <h3 className="text-2xl font-semibold mb-4">Intelligent Observation</h3>
              <p className="text-gray-400 leading-relaxed">
                By understanding human posture and motion over time, it differentiates between safely lying down to rest and a sudden, dangerous fall.
              </p>
            </div>
            <div className="flex flex-col items-start">
              <div className="p-3 bg-gray-900 rounded-xl mb-6">
                <Shield className="w-8 h-8 text-red-400" />
              </div>
              <h3 className="text-2xl font-semibold mb-4">Urgent Response</h3>
              <p className="text-gray-400 leading-relaxed">
                When an emergency is confirmed, it triggers immediate alerts and saves critical footage, ensuring help arrives when seconds matter most.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
