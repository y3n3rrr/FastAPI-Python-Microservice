"use client";

import type { ReactNode } from "react";

type ModalProps = {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
};

export function Modal({ open, title, onClose, children }: ModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-5 shadow-card">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-extrabold">{title}</h3>
          <button type="button" className="text-sm font-semibold text-slate-500" onClick={onClose}>Close</button>
        </div>
        {children}
      </div>
    </div>
  );
}
