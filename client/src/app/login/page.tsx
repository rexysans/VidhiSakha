"use client";

import { Lock, Eye } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";

export default function LoginPage() {
  return (
    <main className="min-h-screen bg-[#041f4b] text-slate-100">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
        <div className="text-3xl font-bold tracking-tight">VidhiSakhā</div>
        <ThemeToggle />
      </header>

      <section className="mx-auto grid w-full max-w-6xl grid-cols-1 items-center gap-8 px-6 py-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-2xl border border-slate-500/30 bg-[#0a2a5f]/70 p-8 shadow-2xl backdrop-blur">
          <h1 className="text-5xl font-extrabold leading-tight">Welcome Back, Jurist.</h1>
          <p className="mt-2 text-sm tracking-[0.25em] text-slate-300">THE DIGITAL JURIST PORTAL</p>

          <div className="mt-8 space-y-4">
            <div>
              <label className="text-xs tracking-[0.22em] text-slate-300">EMAIL ADDRESS</label>
              <input
                placeholder="counsel@vidhisakha.in"
                className="mt-2 h-12 w-full rounded-md border border-slate-500/50 bg-transparent px-3 text-sm outline-none placeholder:text-slate-400"
              />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <label className="text-xs tracking-[0.22em] text-slate-300">PASSWORD</label>
                <button className="text-xs text-slate-400">FORGOT?</button>
              </div>
              <div className="mt-2 flex h-12 items-center rounded-md border border-slate-500/50 px-3">
                <input
                  type="password"
                  value="••••••••"
                  readOnly
                  className="w-full bg-transparent text-sm outline-none"
                />
                <Eye className="h-4 w-4 text-slate-400" />
              </div>
            </div>
          </div>

          <button className="mt-6 inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-[#163d78] font-semibold hover:bg-[#1a4a91]">
            Secure Login <Lock className="h-4 w-4" />
          </button>

          <div className="my-5 flex items-center gap-3 text-xs text-slate-400">
            <span className="h-px flex-1 bg-slate-500/40" />
            AURA OF AUTHORITY
            <span className="h-px flex-1 bg-slate-500/40" />
          </div>

          <button className="inline-flex h-11 w-full items-center justify-center gap-3 rounded-lg bg-slate-700/60 font-medium">
            <span className="rounded bg-black px-1 text-[10px]">G</span> Continue with Google
          </button>

          <p className="mt-6 text-center text-sm text-slate-300">
            New to VidhiSakhā? <a className="font-semibold underline">Create an account</a>
          </p>
        </div>

        <div className="hidden lg:block">
          <div className="rounded-2xl border border-slate-500/30 bg-slate-900/20 p-6 text-sm text-slate-200">
            <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Authority</div>
            <blockquote className="mt-3 text-2xl italic leading-relaxed text-slate-100">
              “Justice must not only be done, but must also be seen to be done.”
            </blockquote>
            <p className="mt-6 text-xs text-slate-300">By accessing this portal, you affirm your identity as a legal professional.</p>
          </div>
        </div>
      </section>

      <footer className="mx-auto mt-8 flex w-full max-w-6xl items-center justify-between px-6 pb-8 text-xs text-slate-400">
        <div>© 2024 VIDHISAKHĀ.</div>
        <div className="flex gap-6">
          <span>TERMS OF SERVICE</span>
          <span>PRIVACY POLICY</span>
        </div>
      </footer>
    </main>
  );
}
