import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "Video Clip Tagger",
  description: "Auto tag video clips",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="max-w-6xl mx-auto p-6">
          <header className="flex items-center justify-between mb-6">
            <div>
              <div className="text-xl font-bold">video-clip-tagger</div>
              <div className="text-sm text-gray-600">Dashboard · Library · Tagging · Settings</div>
            </div>
            <nav className="flex gap-3">
              <Link className="btn" href="/">Dashboard</Link>
              <Link className="btn" href="/library">Library</Link>
              <Link className="btn" href="/tagging">Tagging</Link>
              <Link className="btn" href="/settings">Model Settings</Link>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
