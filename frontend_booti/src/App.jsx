import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Team from './pages/Team';
import Live from './pages/Live';
import Guidebook from './pages/Guidebook';
import Testing from './pages/Testing';
import Camera from './pages/Camera';
import { BotProvider } from './context/BotContext';
import SAIBot from './components/SAIBot';

function App() {
  return (
    <Router>
      <BotProvider>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 font-sans">
          <Navbar />
          <SAIBot />
          <main className="pt-20">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/team" element={<Team />} />
              <Route path="/live" element={<Live />} />`n              <Route path="/camera" element={<Camera />} />
              <Route path="/guidebook" element={<Guidebook />} />
              <Route path="/testing" element={<Testing />} />
            </Routes>
          </main>
        </div>
      </BotProvider>
    </Router>
  );
}

export default App;

