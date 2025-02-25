import React, { Component, ErrorInfo, ReactNode } from "react";
import { Box, Typography } from "@mui/material";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            p: 3,
            my: 2,
            bgcolor: "error.main",
            color: "error.contrastText",
            borderRadius: 1,
          }}
        >
          <Typography variant="h6" component="h2" gutterBottom>
            エラーが発生しました
          </Typography>
          <Typography variant="body1">
            {this.state.error?.message ||
              "アプリケーションの実行中にエラーが発生しました。"}
          </Typography>
          <Typography variant="body2" sx={{ mt: 2 }}>
            ページを更新してもう一度お試しください。
          </Typography>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
