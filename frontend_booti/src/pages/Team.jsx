import { Link as LinkIcon, Mail, Code2 } from 'lucide-react';

const TEAM = [
  {
    name: "Raj Pratap Singh Sengar",
    role: "AI & Backend Engineer",
    linkedin: "https://www.linkedin.com/in/raj-pratap-singh-sengar-3202183a9",
    email: "rajsengar1804@gmail.com",
    image: "/team/5.jpg"
  },
  {
    name: "Prakhar Sharma",
    role: "Frontend & UX Engineer",
    linkedin: "https://www.linkedin.com/in/prakhar-sharma-511b943b0",
    email: "prakhar0897sh@gmail.com",
    image: "/team/prakhar_new.jpg"
  }
];

export default function Team() {
  return (
    <div className="min-h-[calc(100vh-5rem)] py-12 px-6 relative overflow-hidden">
      {/* Decorative Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-teal-200/30 rounded-full blur-[100px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-teal-300/20 rounded-full blur-[100px]"></div>
      </div>

      <div className="max-w-5xl mx-auto relative z-10 flex flex-col items-center">
        <header className="mb-28 text-center mt-8">
          <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-teal-50 border border-teal-200 text-teal-800 font-bold tracking-widest uppercase text-xs mb-8 shadow-sm">
             <Code2 className="w-4 h-4" />
             Smart India Hackathon 2024
          </div>
          <h1 className="text-5xl md:text-6xl font-black tracking-tight text-slate-900 mb-6">
            We are <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-teal-400">The Prometheus</span>
          </h1>
          <p className="text-slate-600 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed font-light">
            A specialized two-man engineering squad united by a single vision: to build technology that saves lives. We developed <strong className="text-teal-700 font-medium">Sanjeevani AI</strong> to solve the critical challenge of elderly safety through advanced computer vision and real-time edge processing.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 lg:gap-24 w-full max-w-4xl">
          {TEAM.map((member, i) => (
            <div key={i} className="relative bg-white/70 backdrop-blur-xl rounded-[2.5rem] p-8 pt-20 shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-white hover:-translate-y-2 hover:shadow-[0_20px_40px_rgb(13,148,136,0.15)] transition-all duration-500 group text-center">
              
              <div className="absolute -top-20 left-1/2 -translate-x-1/2">
                <div className="w-40 h-40 rounded-full p-1.5 bg-gradient-to-br from-teal-400 to-teal-600 shadow-xl group-hover:scale-105 transition-transform duration-500">
                  {member.image ? (
                    <img src={member.image} alt={member.name} className="w-full h-full rounded-full object-cover border-[6px] border-white" />
                  ) : (
                    <div className="w-full h-full rounded-full bg-white flex items-center justify-center text-4xl text-teal-600 font-bold">
                      {member.name.charAt(0)}
                    </div>
                  )}
                </div>
              </div>
              
              <h2 className="text-2xl font-bold text-slate-800 mb-2">{member.name}</h2>
              <p className="text-teal-600 font-semibold text-xs tracking-[0.2em] uppercase mb-8">{member.role}</p>
              
              <div className="flex flex-col gap-4">
                <a href={`https://mail.google.com/mail/?view=cm&fs=1&to=${member.email}`} target="_blank" rel="noreferrer" className="flex items-center justify-center gap-3 py-3.5 px-4 rounded-2xl bg-slate-50 hover:bg-teal-50 text-slate-600 hover:text-teal-700 transition-colors text-sm font-bold tracking-wide border border-slate-100 hover:border-teal-200">
                  <Mail className="w-5 h-5" />
                  {member.email}
                </a>
                <a href={member.linkedin} target="_blank" rel="noreferrer" className="flex items-center justify-center gap-3 py-3.5 px-4 rounded-2xl bg-slate-50 hover:bg-blue-50 text-slate-600 hover:text-blue-700 transition-colors text-sm font-bold tracking-wide border border-slate-100 hover:border-blue-200">
                  <LinkIcon className="w-5 h-5" />
                  LinkedIn Profile
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
