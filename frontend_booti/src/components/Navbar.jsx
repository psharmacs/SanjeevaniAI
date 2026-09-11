import { Link, useLocation } from 'react-router-dom';
import { Shield } from 'lucide-react';
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
          <div className="w-10 h-10 rounded-full bg-teal-50 flex items-center justify-center group-hover:bg-teal-100 transition-colors">
            <Shield className="w-6 h-6 text-teal-600" />
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
          <Link to="/live" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/live') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Live Feed</Link>
          <Link to="/guidebook" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/guidebook') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Guidebook</Link>
          <Link to="/testing" className="px-6 py-2.5 bg-teal-600 text-white rounded-full font-bold text-xs tracking-widest hover:bg-teal-700 transition-colors shadow-md shadow-teal-500/20">
            Get Started ?
          </Link>
        </div>
      </div>
    </nav>
  );
}
