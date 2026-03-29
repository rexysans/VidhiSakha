export default function Page() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#f5f7fb] p-8 text-center dark:bg-[#031a45]">
      <div className="max-w-md space-y-4 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-[#1f3765] dark:bg-[#0b1f44]">
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100 capitalize">Statutes Directory</h1>
        <p className="text-sm leading-relaxed text-slate-500 dark:text-slate-400">
          This section of the VidhiSakhā platform is currently under construction. Please check back later.
        </p>
        <div className="pt-4">
          <a href="/chat" className="inline-flex h-10 items-center justify-center rounded-lg bg-[#1e63ff] px-6 text-sm font-medium text-white transition-colors hover:bg-[#2d6fff]">
            Return to Chat
          </a>
        </div>
      </div>
    </div>
  );
}
