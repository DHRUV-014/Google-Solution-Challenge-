import Link from 'next/link';
import { Activity, Heart, Phone, GitFork, ExternalLink } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-background-secondary border-t border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Left: Brand */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
                <Activity className="h-5 w-5 text-white" />
              </div>
              <div>
                <span className="text-lg font-bold text-white">JanArogya</span>
                <div className="text-xs text-muted leading-none">जनआरोग्य</div>
              </div>
            </div>
            <p className="text-sm text-muted mb-4">
              Health for every person in rural India. Free AI-powered cancer screening via WhatsApp.
            </p>
            {/* SDG Badges */}
            <div className="flex gap-2">
              <span className="inline-flex items-center rounded-lg bg-green-900/30 text-green-400 border border-green-800/50 px-2.5 py-1 text-xs font-semibold">
                SDG 3 · Good Health
              </span>
              <span className="inline-flex items-center rounded-lg bg-green-900/30 text-green-400 border border-green-800/50 px-2.5 py-1 text-xs font-semibold">
                SDG 10 · Equality
              </span>
            </div>
          </div>

          {/* Center: Links */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="text-muted hover:text-white transition-colors">
                  About the Project
                </Link>
              </li>
              <li>
                <Link href="/scan" className="text-muted hover:text-white transition-colors">
                  Try Cancer Screening
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted hover:text-white transition-colors inline-flex items-center gap-1"
                >
                  <Github className="h-3.5 w-3.5" />
                  GitHub Repository
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
            </ul>
            <div className="mt-6 flex items-center gap-2 bg-background-card rounded-xl px-4 py-3 border border-border">
              <Phone className="h-4 w-4 text-success shrink-0" />
              <div>
                <div className="text-xs text-muted">Cancer Helpline</div>
                <div className="text-sm font-semibold text-white">1800-11-2345</div>
              </div>
            </div>
          </div>

          {/* Right: Disclaimer */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Important Notice</h4>
            <p className="text-xs text-muted leading-relaxed">
              JanArogya is an AI-assisted screening tool and does not replace professional medical
              diagnosis. All results should be confirmed by a qualified healthcare provider. This
              tool is designed to improve early detection and healthcare access in underserved
              communities.
            </p>
            <p className="text-xs text-muted mt-3">
              Data sources: ICMR NCRP, GLOBOCAN 2021, WHO
            </p>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 pt-6 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted">
          <span>
            Built with <Heart className="inline h-3 w-3 text-danger fill-danger" /> for{' '}
            <span className="text-white font-medium">Google Solution Challenge 2025</span>
          </span>
          <span>© 2025 JanArogya. MIT License.</span>
        </div>
      </div>
    </footer>
  );
}
