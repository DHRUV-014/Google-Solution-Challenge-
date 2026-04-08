'use client';

import { motion } from 'framer-motion';
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

const levels = [
  {
    icon: CheckCircle,
    title: 'LOW RISK',
    subtitle: 'Continue regular monitoring',
    description:
      'The AI model found no significant markers suggesting cancer. You should continue annual screenings and maintain good oral hygiene.',
    action: 'Schedule annual check-up',
    iconColor: 'text-success',
    borderColor: 'border-success/20 hover:border-success/50',
    bgColor: 'bg-success/5',
    glow: 'hover:glow-green',
    badge: 'bg-success/10 text-success',
  },
  {
    icon: AlertTriangle,
    title: 'HIGH RISK',
    subtitle: 'Immediate medical attention required',
    description:
      'The AI detected markers consistent with potential malignancy. Please see a specialist within 7 days. Early detection saves lives.',
    action: 'Find nearby cancer centre',
    iconColor: 'text-danger',
    borderColor: 'border-danger/20 hover:border-danger/50',
    bgColor: 'bg-danger/5',
    glow: 'hover:glow-red',
    badge: 'bg-danger/10 text-danger',
  },
  {
    icon: XCircle,
    title: 'INVALID',
    subtitle: 'Image quality insufficient',
    description:
      'The uploaded image was too blurry, poorly lit, or did not show the correct area. Please retake the photo in good lighting.',
    action: 'Retake photo with instructions',
    iconColor: 'text-warning',
    borderColor: 'border-warning/20 hover:border-warning/50',
    bgColor: 'bg-warning/5',
    glow: 'hover:glow',
    badge: 'bg-warning/10 text-warning',
  },
];

export default function RiskLevelsSection() {
  return (
    <section className="py-20 bg-background-secondary">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-14">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">
              Understanding Your Results
            </h2>
            <p className="text-muted text-lg">
              JanArogya provides three clear result categories
            </p>
          </motion.div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {levels.map((level, i) => {
            const Icon = level.icon;
            return (
              <motion.div
                key={level.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ scale: 1.03 }}
                className={`rounded-2xl p-8 border ${level.borderColor} ${level.bgColor} transition-all duration-300 cursor-default`}
              >
                <div className={`w-14 h-14 rounded-2xl ${level.badge} flex items-center justify-center mb-5`}>
                  <Icon className={`h-7 w-7 ${level.iconColor}`} />
                </div>
                <div className={`inline-flex px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-3 ${level.badge}`}>
                  {level.title}
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">{level.subtitle}</h3>
                <p className="text-muted text-sm leading-relaxed mb-4">{level.description}</p>
                <div className={`text-xs font-medium ${level.iconColor} flex items-center gap-1`}>
                  → {level.action}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
