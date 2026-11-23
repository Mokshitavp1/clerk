import React from 'react';
import { Check } from 'lucide-react';

export type StepperStage = 'IDLE' | 'RETRIEVE' | 'GRADE' | 'VERIFY' | 'COMPLETE';

interface PipelineStepperProps {
  stage: StepperStage;
  caption: string;
  droppedCount?: number;
  retryCount?: number;
  executedMode?: 'FAST' | 'DEEP THINKING';
}

export const PipelineStepper: React.FC<PipelineStepperProps> = ({
  stage,
  caption,
  droppedCount = 0,
  retryCount = 0,
  executedMode
}) => {
  if (stage === 'IDLE') return null;

  const steps: { key: 'RETRIEVE' | 'GRADE' | 'VERIFY'; num: number; label: string }[] = [
    { key: 'RETRIEVE', num: 1, label: 'RETRIEVE' },
    { key: 'GRADE', num: 2, label: 'GRADE' },
    { key: 'VERIFY', num: 3, label: 'VERIFY' }
  ];

  const getStepStatus = (stepKey: 'RETRIEVE' | 'GRADE' | 'VERIFY') => {
    const order = ['RETRIEVE', 'GRADE', 'VERIFY', 'COMPLETE'];
    const currentIdx = order.indexOf(stage);
    const stepIdx = order.indexOf(stepKey);
    if (currentIdx > stepIdx) return 'done';
    if (currentIdx === stepIdx) return 'active';
    return 'pending';
  };

  return (
    <div className="mt-6 bg-[#FDFBF8] border border-[#493628]/15 rounded-[10px] px-5 py-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* 3-Node Connected Stepper Track */}
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          {steps.map((step, index) => {
            const status = getStepStatus(step.key);
            return (
              <React.Fragment key={step.key}>
                <div
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-[6px] font-mono-tech text-[11px] font-semibold uppercase tracking-[0.09em] border transition-colors whitespace-nowrap shrink-0 ${
                    status === 'done'
                      ? 'bg-[#EBF0E8] border-[#4A6741]/35 text-[#4A6741]'
                      : status === 'active'
                      ? 'bg-[#493628] border-[#342219] text-[#FDFBF8]'
                      : 'bg-[#F1EEE9] border-[#D6C0B3] text-[#806C5D]'
                  }`}
                >
                  {status === 'done' ? (
                    <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                  ) : (
                    <span className="font-mono-tech">{step.num}</span>
                  )}
                  <span>
                    {step.num} {step.label}
                  </span>
                </div>

                {index < steps.length - 1 && (
                  <div
                    className={`h-[2px] w-6 sm:w-10 transition-colors ${
                      status === 'done' ? 'bg-[#4A6741]/50' : 'bg-[#D6C0B3]'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Mode & Telemetry Summary */}
        <div className="flex items-center gap-2 font-mono-tech text-[10px] uppercase tracking-[0.08em] text-[#806C5D]">
          {executedMode && (
            <span>
              PIPELINE: <strong className="text-[#493628]">{executedMode}</strong>
            </span>
          )}
          {droppedCount > 0 && (
            <>
              <span>·</span>
              <span className="text-[#B87D1E]">{droppedCount} BELOW 0.40 FLOOR</span>
            </>
          )}
          {retryCount > 0 && (
            <>
              <span>·</span>
              <span>{retryCount} RETRY</span>
            </>
          )}
        </div>
      </div>

      {/* Live Context Caption */}
      <p className="mt-2.5 text-[13px] text-[#806C5D] font-serif-editorial italic">
        “{caption}”
      </p>
    </div>
  );
};
