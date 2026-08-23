import React from "react";

// ThreeUI's WebGL components occasionally fail to initialize (unsupported GPU,
// headless context, etc.). Render them inside this boundary so a failure degrades
// gracefully to the provided CSS fallback instead of crashing the whole page.
type BoundaryProps = { children: React.ReactNode; fallback: React.ReactNode };
type BoundaryState = { failed: boolean };

class ThreeUIErrorBoundary extends React.Component<BoundaryProps, BoundaryState> {
  state: BoundaryState = { failed: false };
  static getDerivedStateFromError(): BoundaryState {
    return { failed: true };
  }
  render() {
    if (this.state.failed) return <>{this.props.fallback}</>;
    return this.props.children;
  }
}

export function ThreeUIBoundary({ children, fallback }: BoundaryProps) {
  const [timedOut, setTimedOut] = React.useState(false);
  React.useEffect(() => {
    if (timedOut) return;
    const id = window.setTimeout(() => setTimedOut(true), 6000);
    return () => window.clearTimeout(id);
  }, [timedOut]);
  if (timedOut) return <>{fallback}</>;
  return <ThreeUIErrorBoundary fallback={fallback}>{children}</ThreeUIErrorBoundary>;
}
