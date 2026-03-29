export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f5f7fb] dark:bg-[#031a45]">
      <div className="flex flex-col items-center gap-5">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-300 border-t-[#2d67ff] dark:border-slate-700 dark:border-t-[#3d89ff]" />
        <p className="text-xs font-semibold tracking-[0.2em] text-slate-500 dark:text-slate-400 uppercase">
          Loading VidhiSakhā
        </p>
      </div>
    </div>
  );
}
