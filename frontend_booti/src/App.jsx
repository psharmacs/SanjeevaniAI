import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Team from './pages/Team';
import Live from './pages/Live';
import Guidebook from './pages/Guidebook';
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
              <Route path="/live" element={<Live />} />
              <Route path="/guidebook" element={<Guidebook />} />
            </Routes>
          </main>
        </div>
      </BotProvider>
    </Router>
  );
}

export default App;
