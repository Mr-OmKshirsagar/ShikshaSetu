import { AlertTriangle, RotateCcw, ArrowLeft } from "lucide-react";
import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: string;
}

/**
 * Top-level ErrorBoundary.
 *
 * When a React render throws, this component shows a professional recovery UI
 * rather than a blank/grey screen. Uses concrete Tailwind classes only —
 * no CSS custom properties that may be undefined.
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: "" };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: error?.message || "An unexpected error occurred.",
    };
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    // Log to console in development — never expose to users in production
    if (import.meta.env.DEV) {
      console.error("[ErrorBoundary] Caught error:", error);
      console.error("[ErrorBoundary] Component stack:", info.componentStack);
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-[#f4f7fb] p-6">
          <div className="w-full max-w-lg rounded-2xl border border-red-200 bg-white p-8 shadow-sm text-center space-y-5">
            {/* Icon */}
            <div className="flex justify-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50">
                <AlertTriangle size={28} className="text-red-500" />
              </div>
            </div>

            {/* Heading */}
            <div>
              <h2 className="text-lg font-bold text-[#123057]">
                Something went wrong
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                An unexpected error occurred while rendering this page.
              </p>
            </div>

            {/* Error message — safe to show */}
            <div className="rounded-xl bg-slate-50 border border-slate-100 px-4 py-3 text-xs text-slate-600 text-left font-mono break-all">
              {this.state.errorInfo}
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
              <button
                onClick={() => this.setState({ hasError: false, error: null, errorInfo: "" })}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#123057] px-5 py-2.5 text-xs font-bold text-white shadow hover:bg-[#0f2649] transition-all"
              >
                <RotateCcw size={14} />
                Try Again
              </button>
              <button
                onClick={() => window.location.href = "/"}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-5 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all"
              >
                <ArrowLeft size={14} />
                Back to Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
