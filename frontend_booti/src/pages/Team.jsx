import React from 'react';
import { Users, Code, Paintbrush, Database, BrainCircuit } from 'lucide-react';

export default function Team() {
  const team = [
    { 
      name: "Raj Pratap Singh Sengar", 
      role: "AI & ML Engineer", 
      photo: "/team/2.jpg",
      icon: <BrainCircuit className="w-8 h-8 text-teal-500" />,
      linkedin: "https://www.linkedin.com/in/raj-pratap-singh-sengar-3202183a9",
      email: "rajsengar1804@gmail.com"
    },
    { 
      name: "Prakhar Sharma", 
      role: "Frontend Developer", 
      photo: "/team/1.jpg",
      icon: <Code className="w-8 h-8 text-cyan-500" />,
      linkedin: "https://www.linkedin.com/in/prakhar-sharma-511b943b0",
      email: "prakhar0897sh@gmail.com"
    },
    { 
      name: "Sachin Sengar", 
      role: "Backend Developer", 
      photo: "/team/3.jpg",
      icon: <Database className="w-8 h-8 text-emerald-500" />,
      linkedin: "https://www.linkedin.com/in/sachin-sengar26",
      email: "sachinsengar2609@gmail.com"
    },
    { 
      name: "Barsha Rani Das", 
      role: "Team Member", 
      photo: "/team/4.jpg",
      icon: <Users className="w-8 h-8 text-pink-500" />,
      linkedin: "https://www.linkedin.com/in/barsha-rani-das-1476283a8",
      email: "dasbarsharani424@gmail.com"
    },
    { 
      name: "Mohit Sikarwar", 
      role: "Team Member", 
      photo: "/team/5.jpg",
      icon: <Paintbrush className="w-8 h-8 text-amber-500" />,
      linkedin: "https://www.linkedin.com/in/mohit-sikarwar-819aa7342",
      email: "msikarwar743@gmail.com"
    },
    { 
      name: "Rishikant Sharma", 
      role: "Team Member", 
      photo: "/team/6.jpg",
      icon: <Users className="w-8 h-8 text-indigo-500" />,
      linkedin: null,
      email: "rishikantbhardwaj6@gmail.com"
    }
  ];

  return (
    <div className="min-h-[calc(100vh-5rem)] p-6 max-w-7xl mx-auto flex flex-col items-center justify-center bg-transparent py-12">
      
      <div className="inline-flex items-center gap-2 bg-slate-800 text-white px-4 py-2 rounded-full font-bold text-sm tracking-widest mb-6 shadow-sm">
        <Users className="w-4 h-4 text-teal-400" />
        TEAM PROMETHEUS
      </div>
      
      <h1 className="text-5xl font-black tracking-tight text-slate-800 mb-4 text-center">
        Meet the Innovators
      </h1>
      
      <div className="max-w-4xl mx-auto text-center mb-16 space-y-5">
        <p className="text-xl text-slate-700 font-medium leading-relaxed max-w-2xl mx-auto">
          We are a team of aspirational engineers dedicated to building Sanjeevani AI—an intelligent safety system that observes, understands, and responds to protect the elderly.
        </p>
        <p className="text-lg text-slate-500 font-medium leading-relaxed max-w-3xl mx-auto">
          Coming together for the Smart India Hackathon 2026, Team Prometheus combines expertise in Computer Vision, Artificial Intelligence, and full-stack engineering. Our mission is to bridge the gap between passive surveillance and active, life-saving intervention.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
        {team.map((member, i) => (
          <div key={i} className="glass-panel p-8 rounded-[2rem] border border-slate-200 flex flex-col items-center text-center hover:-translate-y-2 transition-transform duration-300 shadow-lg relative group overflow-hidden">
            
            <div className="w-24 h-24 rounded-full bg-slate-50 flex items-center justify-center mb-6 shadow-inner border-4 border-white overflow-hidden relative z-10">
              {member.photo ? (
                <img src={member.photo} alt={member.name} className="w-full h-full object-cover" />
              ) : (
                member.icon
              )}
            </div>
            
            <h3 className="text-xl font-bold text-slate-800 mb-1 relative z-10">{member.name}</h3>
            <p className="text-sm font-bold tracking-widest text-slate-400 uppercase relative z-10 mb-6">{member.role}</p>
            
            <div className="flex gap-4 relative z-10">
              {member.linkedin && (
                <a href={member.linkedin} target="_blank" rel="noreferrer" className="text-xs font-bold text-slate-400 hover:text-blue-600 transition-colors">
                  LINKEDIN
                </a>
              )}
              {member.email && (
                <a href={`mailto:${member.email}`} className="text-xs font-bold text-slate-400 hover:text-red-500 transition-colors">
                  {member.email}
                </a>
              )}
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
