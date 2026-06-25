import { useApplicationContext } from "../context/ApplicationContext";

export function Header() {
  const { currentStep, application } = useApplicationContext();
  const isAccountStep = currentStep === "account";
  const accountEmail = application.account.email?.trim();
  const showUserEmail = !isAccountStep && Boolean(accountEmail);

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="flex h-20 items-center justify-between pl-2 pr-6">
        <img src="https://resume-analyzer.gatnix.com/assets/image-zoOnZMzA.png" alt="DXC Logo" className="h-12 w-auto" />
        <div className="text-right text-sm text-slate-700">
          <div className="mb-1 flex items-center justify-end gap-3">
            <span>🌐 English</span>
            <span className="text-slate-400">|</span>
            {isAccountStep ? (
              <span>Sign In</span>
            ) : (
              <>
                <span>⚙ Settings</span>
                <span className="text-slate-400">|</span>
                {showUserEmail ? <span>👤 {accountEmail}</span> : <span>Sign In</span>}
              </>
            )}
          </div>
          <div className="flex items-center justify-end gap-14 font-semibold text-slate-900">
            <span>Search for Jobs</span>
            {!isAccountStep && <span>Candidate Home</span>}
          </div>
        </div>
      </div>
    </header>
  );
}
