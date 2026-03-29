import Link from "next/link";
import { Search, Settings, Shield, Lock, Scale } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f3f6fb] text-[#071d49] dark:bg-[#031c49] dark:text-white">
      <header className="mx-auto flex w-full max-w-7xl items-center justify-between border-b border-slate-200/70 px-6 py-4 dark:border-[#1f3765]">
        <div className="text-3xl font-extrabold">VidhiSakhā</div>
        <nav className="hidden items-center gap-8 text-sm font-semibold md:flex">
          <span className="border-b-2 border-current pb-1">Constitutional Law</span>
          <span>Recent Queries</span>
          <span>My Vault</span>
          <span>Legal Library</span>
        </nav>
        <div className="flex items-center gap-3">
          <Search className="h-4 w-4" />
          <Settings className="h-4 w-4" />
          <ThemeToggle />
          <Link href="/login" className="rounded-full border border-slate-400/30 px-3 py-1 text-xs">Login</Link>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-7xl grid-cols-1 items-center gap-8 px-6 py-14 lg:grid-cols-2">
        <div>
          <div className="inline-block rounded bg-[#dae5ff] px-3 py-1 text-xs font-semibold tracking-[0.18em] text-[#2b4e92] dark:bg-[#174388] dark:text-slate-100">
            THE DIGITAL JURIST
          </div>
          <h1 className="mt-5 text-6xl font-black leading-[1.03]">
            Understand the
            <br />
            Constitution
            <br />
            with VidhiSakhā.
          </h1>
          <p className="mt-5 max-w-xl text-2xl text-slate-600 dark:text-slate-300">
            Your digital jurist for navigating Indian constitutional law with clarity and precision.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/chat" className="rounded-xl bg-[#103a79] px-6 py-3 text-sm font-semibold text-white hover:bg-[#15478f]">
              Start a New Consultation
            </Link>
            <button className="rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold dark:border-[#2a4677] dark:bg-[#0f2a57]">
              Explore Library
            </button>
          </div>
          <div className="mt-10 flex flex-wrap items-center gap-8 text-sm font-semibold tracking-[0.15em] text-slate-500 dark:text-slate-300">
            <div className="flex items-center gap-2"><Shield className="h-4 w-4" /> SUPREME COURT DATABASE</div>
            <div className="flex items-center gap-2"><Scale className="h-4 w-4" /> EXPERT LEGAL INSIGHTS</div>
          </div>
        </div>

        <div className="rounded-2xl bg-gradient-to-br from-[#0f2f65] to-[#03183f] p-6 shadow-2xl">
          <div className="h-[460px] rounded-xl border border-slate-500/30 bg-[radial-gradient(circle_at_20%_10%,rgba(122,164,255,0.35),rgba(0,0,0,0)_42%),linear-gradient(160deg,#0a244f,#041633)] p-6">
            <p className="text-sm text-slate-300">“Justice must not only be done, but must also be seen to be done.”</p>
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-6 pb-16">
        <h2 className="text-5xl font-extrabold">Precision in Every Clause</h2>
        <p className="mt-3 max-w-2xl text-lg text-slate-600 dark:text-slate-300">
          Leveraging advanced legal technology to provide clarity on the foundational laws of the nation.
        </p>

        <div className="mt-8 grid gap-5 md:grid-cols-2">
          <article className="rounded-2xl bg-white p-6 shadow-sm dark:bg-[#0d2c5a]">
            <div className="rounded-md bg-[#d9e7ff] p-2 inline-flex dark:bg-[#184a92]"><Lock className="h-4 w-4" /></div>
            <h3 className="mt-4 text-3xl font-bold">Expert Legal Human Summaries</h3>
            <p className="mt-3 text-slate-600 dark:text-slate-300">Complex constitutional matters condensed into clear, actionable summaries.</p>
          </article>

          <article className="rounded-2xl bg-[#173f79] p-6 text-white">
            <h3 className="text-3xl font-bold">Statutory Detail & Precedents</h3>
            <p className="mt-3 text-slate-200">Deep-link into every Article and Amendment with chronological case law mapping.</p>
          </article>
        </div>
      </section>
    </main>
  );
}
