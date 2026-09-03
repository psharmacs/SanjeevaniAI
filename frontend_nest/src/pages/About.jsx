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
    image: "/team/2.jpg"
  },
  {
    name: "Barsha Rani Das",
    linkedin: "#",
    email: "#",
    image: null
  },
  {
    name: "Sachin Sengar",
    linkedin: "https://www.linkedin.com/in/sachin-sengar26",
    email: "sachinsengar2609@gmail.com",
    image: "/team/4.jpg"
  },
  {
    name: "Mohit Sikarwar",
    linkedin: "https://www.linkedin.com/in/mohit-sikarwar-819aa7342",
    email: "#",
    image: "/team/1.jpg"
  },
  {
    name: "Rishikant Sharma",
    linkedin: "#",
    email: "#",
    image: "/team/3.jpg"
  }
];

export default function About() {
  return (
    <div className="min-h-[calc(100vh-4rem)] p-6 md:p-12 max-w-7xl mx-auto flex flex-col">
      <header className="mb-16">
        <h1 className="text-4xl font-light tracking-wide text-gray-200">The Prometheus</h1>
        <p className="text-emerald-400 mt-2 font-medium tracking-wider uppercase text-sm">Smart India Hackathon Team</p>
        <p className="text-gray-400 mt-6 max-w-3xl leading-relaxed text-lg">
          We are <strong className="text-gray-300">The Prometheus</strong>, a team of passionate developers and engineers united by a single vision: to build technology that saves lives. For the Smart India Hackathon, we developed <strong>Sanjeevani AI</strong> to solve the critical challenge of elderly safety and fall detection using advanced computer vision and real-time processing.
          <br /><br />
          Meet the innovators behind the intelligence:
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {TEAM.map((member, i) => (
          <div key={i} className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 flex flex-col hover:bg-gray-900 transition-colors">
            
            <div className="flex items-center gap-4 mb-4">
              {member.image ? (
                <img src={member.image} alt={member.name} className="w-16 h-16 rounded-full object-cover border border-gray-700" />
              ) : (
                <div className="w-16 h-16 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-xl text-gray-500 font-semibold">
                  {member.name.charAt(0)}
                </div>
              )}
              <h2 className="text-xl font-semibold text-gray-200">{member.name}</h2>
            </div>
            
            <div className="flex-1"></div>
            
            <div className="flex flex-col gap-3 pt-4 border-t border-gray-800">
              {member.email !== "#" && (
                <a href={`https://mail.google.com/mail/?view=cm&fs=1&to=${member.email}`} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-gray-400 hover:text-emerald-400 transition-colors text-sm">
                  <Mail className="w-4 h-4" />
                  {member.email}
                </a>
              )}
              {member.linkedin !== "#" && (
                <a href={member.linkedin} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-gray-400 hover:text-blue-400 transition-colors text-sm">
                  <LinkIcon className="w-4 h-4" />
                  LinkedIn Profile
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
