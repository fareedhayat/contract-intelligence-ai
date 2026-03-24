import { Component, type ErrorInfo, type ReactNode } from "react";
import { Button, Text, makeStyles, tokens } from "@fluentui/react-components";
import { ErrorCircleRegular } from "@fluentui/react-icons";

const useStyles = makeStyles({
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "48px 24px",
    gap: "16px",
    textAlign: "center",
  },
  icon: {
    fontSize: "48px",
    color: tokens.colorPaletteRedForeground1,
  },
  detail: {
    color: tokens.colorNeutralForeground3,
    fontFamily: "monospace",
    fontSize: "12px",
    maxWidth: "600px",
    wordBreak: "break-word",
  },
});

function ErrorFallback({ error, onReset }: { error: Error | null; onReset: () => void }) {
  const styles = useStyles();
  return (
    <div className={styles.container}>
      <ErrorCircleRegular className={styles.icon} />
      <Text size={500} weight="semibold">Something went wrong</Text>
      {error && <Text className={styles.detail}>{error.message}</Text>}
      <Button onClick={onReset}>Try again</Button>
    </div>
  );
}

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <ErrorFallback
        error={this.state.error}
        onReset={() => this.setState({ hasError: false, error: null })}
      />
    );
  }
}
