import React from "react";

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
}

/**
 * Wraps optional ThreeUI WebGL/decorative components. If a component throws at
 * runtime (e.g. a missing shader asset bundle), we render the native fallback
 * instead of taking down the whole app.
 */
export class ThreeUIBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) return this.props.fallback ?? null;
    return this.props.children;
  }
}
