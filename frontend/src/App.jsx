import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity, Shield, Cpu, Play, Info } from 'lucide-react';
import Home from './pages/Home';
import Guardian from './pages/Guardian';
import Intelligence from './pages/Intelligence';
import Live from './pages/Live';
import About from './pages/About';

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-gray-800 bg-gray-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <Shield className="w-6 h-6 text-emerald-400" />
            <span className="text-xl font-semibold tracking-wide text-white">SANJEEVANI<span className="text-emerald-400">AI</span></span>
          </Link>
          <div className="hidden md:flex space-x-8">
            <Link to="/" className="text-gray-300 hover:text-white transition-colors">Home</Link>
            <Link to="/guardian" className="text-gray-300 hover:text-emerald-400 transition-colors">Guardian</Link>
            <Link to="/intelligence" className="text-gray-300 hover:text-amber-400 transition-colors">Intelligence</Link>
            <Link to="/live" className="text-gray-300 hover:text-red-400 transition-colors">Live Mode</Link>
            <Link to="/about" className="text-gray-300 hover:text-white transition-colors">Team</Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-950 text-gray-100 font-sans selection:bg-emerald-500/30">
        <Navbar />
        <main className="pt-16">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/guardian" element={<Guardian />} />
            <Route path="/intelligence" element={<Intelligence />} />
            <Route path="/live" element={<Live />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
