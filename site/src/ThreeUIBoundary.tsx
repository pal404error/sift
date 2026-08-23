import React from "react";

// ThreeUI's WebGL components occasionally fail to initialize (unsupported GPU,
// headless context, etc.). Render them inside this boundary so a failure degrades
// gracefully to the provided CSS fallback instead of crashing the whole page.
export function ThreeUIBoundary({
  children,
  fallback,
}: {
  children: React.ReactNode;
  fallback: React.ReactNode;
}) {
  const [failed, setFailed] = React.useState(false);
  React.useEffect(() => {
    if (failed) return;
    const id = window.setTimeout(() => setFailed(true), 4000);
    return () => window.clearTimeout(id);
  }, [failed]);
  if (failed) return <>{fallback}</>;
  return (
    <React.ErrorBoundary
      fallback={fallback}
      onError={() => setFailed(true)}
    >
      {children}
    </React.ErrorBoundary>
  );
}
