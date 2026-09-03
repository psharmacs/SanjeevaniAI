import { Link, useLocation } from 'react-router-dom';
import { HeartPulse } from 'lucide-react';
import clsx from 'clsx';

export default function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-[1600px] mx-auto px-6 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-full bg-teal-50 flex items-center justify-center group-hover:bg-teal-100 transition-colors">
            <HeartPulse className="w-6 h-6 text-teal-600" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-widest text-slate-800">
              SANJEEVANI<span className="text-teal-600">.AI</span>
            </h1>
          </div>
        </Link>
        <div className="flex gap-8">
          <Link to="/" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Home</Link>
          <Link to="/team" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/team') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Team</Link>
          <Link to="/live" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/live') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Live Feed</Link>
          <Link to="/guidebook" className={clsx("text-xs font-bold tracking-[0.15em] uppercase transition-colors", isActive('/guidebook') ? "text-teal-600" : "text-slate-500 hover:text-teal-700")}>Guidebook</Link>
        </div>
      </div>
    </nav>
  );
}
