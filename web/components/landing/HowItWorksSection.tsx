'use client';

import { motion } from 'framer-motion';
import { MessageSquare, Brain, FileText, ArrowRight } from 'lucide-react';

const steps = [
  {
    step: '01',
    icon: MessageSquare,
    title: 'Send a Photo',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/20',
    description:
      'Take a clear photo of the area you want to screen — oral cavity or skin lesion — and send it via WhatsApp or upload directly.',
    iconBg: 'bg-blue-500/20',
  },
  {
    step: '02',
    icon: Brain,
    title: 'AI Analyzes',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/20',
    description:
      'Google Gemini Vision and our trained TFLite model analyze your image in under 3 seconds, identifying potential cancer markers.',
    iconBg: 'bg-purple-500/20',
    pulse: true,
  },
  {
    step: '03',
    icon: FileText,
    title: 'Get Your Result',
    color: 'text-green-400',
    bg: 'bg-green-500/10 border-green-500/20',
    description:
      'Receive a clear risk assessment in your language — Hindi, Tamil, Telugu, or English — with actionable next steps and nearest screening centres.',
    iconBg: 'bg-green-500/20',
  },
];

export default function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-20 bg-background-primary">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Title */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              Three steps.{' '}
              <span className="text-accent">Ten seconds.</span>{' '}
              Could save a life.
            </h2>
            <p className="text-muted text-lg max-w-2xl mx-auto">
              No hospital visit required. No app to download. No cost.
            </p>
          </motion.div>
        </div>

        {/* Steps */}
        <div className="grid md:grid-cols-3 gap-6 relative">
          {/* Connecting arrows */}
          <div className="hidden md:flex absolute top-1/2 left-1/3 -translate-y-1/2 -translate-x-1/2 items-center justify-center w-12 z-10">
            <ArrowRight className="h-6 w-6 text-border-light" />
          </div>
          <div className="hidden md:flex absolute top-1/2 left-2/3 -translate-y-1/2 -translate-x-1/2 items-center justify-center w-12 z-10">
            <ArrowRight className="h-6 w-6 text-border-light" />
          </div>

          {steps.map((step, i) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.15 }}
                className={`rounded-2xl p-8 border ${step.bg} hover:scale-[1.02] transition-all duration-200 cursor-default`}
              >
                <div className="flex items-start gap-4 mb-6">
                  <div className={`relative w-12 h-12 rounded-xl ${step.iconBg} flex items-center justify-center shrink-0`}>
                    <Icon className={`h-6 w-6 ${step.color}`} />
                    {step.pulse && (
                      <span className={`absolute inset-0 rounded-xl animate-pulse-ring border ${step.bg}`} />
                    )}
                  </div>
                  <div>
                    <div className={`text-xs font-bold uppercase tracking-widest ${step.color} mb-1`}>
                      Step {step.step}
                    </div>
                    <h3 className="text-xl font-bold text-white">{step.title}</h3>
                  </div>
                </div>
                <p className="text-muted leading-relaxed">{step.description}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
