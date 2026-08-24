import React from "react";

// ThreeUI's WebGL components can fail to initialize or lose their context. React
// error boundaries only catch render-phase errors, so async failures inside the
// animation loop are reported via onError (wired to a parent state) so the
// affected component degrades to its fallback while the rest of the page stays up.
type Props = { children: React.ReactNode; fallback: React.ReactNode; onError?: () => void };
type State = { failed: boolean };

class Boundary extends React.Component<Props, State> {
  state: State = { failed: false };
  static getDerivedStateFromError(): State {
    return { failed: true };
  }
  componentDidCatch() {
    this.props.onError?.();
  }
  render() {
    return this.state.failed ? <>{this.props.fallback}</> : this.props.children;
  }
}

export function ThreeUIBoundary({ children, fallback, onError }: Props) {
  return (
    <Boundary fallback={fallback} onError={onError}>
      {children}
    </Boundary>
  );
}
