import { Component, type ErrorInfo, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  message: string
}

export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
    message: '',
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      message: error.message || 'Unknown frontend error',
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('React frontend crashed:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ maxWidth: 760, margin: '40px auto', padding: 24 }}>
          <div className="error">
            <strong>React frontend crashed.</strong>
            <p style={{ marginTop: 8 }}>{this.state.message}</p>
            <p style={{ marginTop: 8 }}>
              Use <code>run-frontend.bat</code> for the stable fallback, or check the browser console
              while testing <code>run-react-frontend.bat</code>.
            </p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
