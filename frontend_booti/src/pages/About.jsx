import { Link as LinkIcon, Mail } from 'lucide-react';

const TEAM = [
  {
    name: "Raj Pratap Singh Sengar",
    linkedin: "https://www.linkedin.com/in/raj-pratap-singh-sengar-3202183a9",
    email: "rajsengar1804@gmail.com",
    image: "/team/5.jpg"
  },
  {
    name: "Prakhar Sharma",
    linkedin: "https://www.linkedin.com/in/prakhar-sharma-511b943b0",
    email: "prakhar0897sh@gmail.com",
    image: "/team/prakhar_new.jpg"
  },
  {
    name: "Rishikant Sharma",
    linkedin: "#",
    email: "rishikantbhardwaj06@gmail.com",
    image: "/team/rishikant_new.jpg"
  },
  {
    name: "Barsha Rani Das",
    linkedin: "https://www.linkedin.com/in/barsha-rani-das-1476283a8",
    email: "dasbarsharani424@gmail.com",
    image: "/team/barsha.jpg"
  },
  {
    name: "Sachin Sengar",
    linkedin: "https://www.linkedin.com/in/sachin-sengar26",
    email: "sachinsengar2609@gmail.com",
    image: "/team/sachin_new.jpg"
  },
  {
    name: "Mohit Sikarwar",
    linkedin: "https://www.linkedin.com/in/mohit-sikarwar-819aa7342",
    email: "#",
    image: "/team/1.jpg"
  }
];

export default function About() {
  return (
    <div className="min-h-[calc(100vh-5rem)] p-6 md:p-12 max-w-7xl mx-auto flex flex-col bg-transparent">
      <header className="mb-16">
        <h1 className="text-4xl font-normal tracking-wide text-slate-900" style={{ fontFamily: 'Georgia, serif' }}>The Prometheus</h1>
        <p className="text-teal-600 mt-2 font-bold tracking-wider uppercase text-sm">Smart India Hackathon Team</p>
        <p className="text-slate-600 mt-6 max-w-3xl leading-relaxed text-lg font-light">
          We are <strong className="text-slate-900 font-medium">The Prometheus</strong>, a team of passionate developers and engineers united by a single vision: to build technology that saves lives. For the Smart India Hackathon, we developed <strong className="text-teal-600 font-medium">Sanjeevani AI</strong> to solve the critical challenge of elderly safety and fall detection using advanced computer vision and real-time processing.
          <br /><br />
          Meet the innovators behind the intelligence:
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {TEAM.map((member, i) => (
          <div key={i} className="glass-panel rounded-2xl p-6 flex flex-col hover:border-teal-500/30 hover:shadow-2xl transition-all group">
            
            <div className="flex items-center gap-4 mb-4">
              {member.image ? (
                <img src={member.image} alt={member.name} className="w-16 h-16 rounded-full object-cover shadow-sm ring-2 ring-slate-100 group-hover:ring-teal-200 transition-colors" />
              ) : (
                <div className="w-16 h-16 rounded-full bg-slate-100 shadow-sm ring-2 ring-slate-100 flex items-center justify-center text-xl text-slate-400 font-semibold group-hover:ring-teal-200 transition-colors">
                  {member.name.charAt(0)}
                </div>
              )}
              <h2 className="text-xl font-medium text-slate-800">{member.name}</h2>
            </div>
            
            <div className="flex-1"></div>
            
            <div className="flex flex-col gap-3 pt-4 border-t border-slate-100">
              {/* Always show exactly two rows for consistency */}
              
              {/* Email Row */}
              {member.email !== "#" ? (
                <a href={`https://mail.google.com/mail/?view=cm&fs=1&to=${member.email}`} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-slate-500 hover:text-teal-600 transition-colors text-sm font-medium truncate">
                  <Mail className="w-4 h-4 flex-shrink-0" />
                  <span className="truncate">{member.email}</span>
                </a>
              ) : (
                <div className="flex items-center gap-2 text-slate-300 text-sm font-medium select-none">
                  <Mail className="w-4 h-4 flex-shrink-0" />
                  <span>Email</span>
                </div>
              )}

              {/* LinkedIn Row */}
              {member.linkedin !== "#" ? (
                <a href={member.linkedin} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-slate-500 hover:text-blue-600 transition-colors text-sm font-medium">
                  <LinkIcon className="w-4 h-4 flex-shrink-0" />
                  <span>LinkedIn Profile</span>
                </a>
              ) : (
                <div className="flex items-center gap-2 text-slate-300 text-sm font-medium select-none">
                  <LinkIcon className="w-4 h-4 flex-shrink-0" />
                  <span>LinkedIn Profile</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
