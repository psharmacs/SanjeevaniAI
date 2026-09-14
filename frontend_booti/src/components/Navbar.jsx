import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';

export default function Navbar() {
  const location = useLocation();
  const isHome = location.pathname === '/';
  const isActive = (path) => location.pathname === path;

  return (
    <nav className={clsx(
      "fixed top-0 left-0 right-0 z-40 transition-all duration-300",
      isHome 
        ? "bg-transparent py-2" 
        : "bg-white/90 backdrop-blur-xl border-b border-slate-200/60 shadow-sm"
    )}>
      <div className="max-w-[1600px] mx-auto px-6 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden transition-transform group-hover:scale-105">
            <img src="/LOGO.jpeg" alt="Sanjeevani AI Logo" className="w-full h-full object-cover" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-widest text-slate-800 uppercase">
              Sanjeevani<span className="text-teal-600">AI</span>
            </h1>
          </div>
        </Link>
        <div className="flex gap-8 items-center">
          <Link to="/" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Home</Link>
          <Link to="/team" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/team') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Team</Link>
          <Link to="/live" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/live') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Simulation</Link>
          <Link to="/camera" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/camera') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Live Node</Link>
          <Link to="/guidebook" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/guidebook') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Guidebook</Link>
        </div>
      </div>
    </nav>
  );
}

