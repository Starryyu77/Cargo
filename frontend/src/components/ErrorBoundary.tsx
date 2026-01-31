import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-red-900 text-white p-10 font-mono">
          <h1 className="text-4xl font-bold mb-4">SYSTEM FAILURE</h1>
          <div className="border border-white p-4 bg-black/50">
            <p className="text-xl mb-2">{this.state.error?.toString()}</p>
            <p className="opacity-70">Please check the console for details.</p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
